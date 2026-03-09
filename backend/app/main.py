from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Classroom, GradeRecord, Student, Subject
from .schemas import (
    ClassroomCreate,
    ClassroomRead,
    GradeRecordCreate,
    GradeRecordJoined,
    GradeRecordRead,
    GradeRecordUpdate,
    StudentCreate,
    StudentRead,
    SubjectCreate,
    SubjectRead,
)
from .services import calculate_average, calculate_status, normalize_name

Base.metadata.create_all(bind=engine)

app = FastAPI(title="School Diary API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/classrooms", response_model=ClassroomRead)
def create_classroom(payload: ClassroomCreate, db: Session = Depends(get_db)):
    classroom = Classroom(name=normalize_name(payload.name))
    db.add(classroom)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Classroom already exists")
    db.refresh(classroom)
    return classroom


@app.get("/classrooms", response_model=list[ClassroomRead])
def list_classrooms(db: Session = Depends(get_db)):
    return db.scalars(select(Classroom).order_by(Classroom.name)).all()


@app.post("/subjects", response_model=SubjectRead)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db)):
    subject = Subject(name=normalize_name(payload.name))
    db.add(subject)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Subject already exists")
    db.refresh(subject)
    return subject


@app.get("/subjects", response_model=list[SubjectRead])
def list_subjects(db: Session = Depends(get_db)):
    return db.scalars(select(Subject).order_by(Subject.name)).all()


@app.post("/students", response_model=StudentRead)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    classroom = db.get(Classroom, payload.classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    student = Student(
        name=normalize_name(payload.name),
        classroom_id=payload.classroom_id,
    )
    db.add(student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Student already exists in this classroom")
    db.refresh(student)
    return student


@app.get("/students", response_model=list[StudentRead])
def list_students(classroom_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Student)
    if classroom_id is not None:
        query = query.where(Student.classroom_id == classroom_id)
    return db.scalars(query.order_by(Student.name)).all()


@app.post("/grade-records", response_model=GradeRecordRead)
def create_grade_record(payload: GradeRecordCreate, db: Session = Depends(get_db)):
    student = db.get(Student, payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    classroom = db.get(Classroom, payload.classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    subject = db.get(Subject, payload.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    if student.classroom_id != payload.classroom_id:
        raise HTTPException(status_code=400, detail="Student does not belong to this classroom")

    average = calculate_average(payload.note_1, payload.note_2, payload.note_3, payload.recovery_note)
    status = calculate_status(average)

    grade_record = GradeRecord(
        student_id=payload.student_id,
        classroom_id=payload.classroom_id,
        subject_id=payload.subject_id,
        note_1=payload.note_1,
        note_2=payload.note_2,
        note_3=payload.note_3,
        recovery_note=payload.recovery_note,
        average=average,
        status=status,
    )

    db.add(grade_record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Grade record already exists for this student/classroom/subject")
    db.refresh(grade_record)
    return grade_record


@app.put("/grade-records/{grade_record_id}", response_model=GradeRecordRead)
def update_grade_record(grade_record_id: int, payload: GradeRecordUpdate, db: Session = Depends(get_db)):
    grade_record = db.get(GradeRecord, grade_record_id)
    if not grade_record:
        raise HTTPException(status_code=404, detail="Grade record not found")

    grade_record.note_1 = payload.note_1
    grade_record.note_2 = payload.note_2
    grade_record.note_3 = payload.note_3
    grade_record.recovery_note = payload.recovery_note

    average = calculate_average(payload.note_1, payload.note_2, payload.note_3, payload.recovery_note)
    grade_record.average = average
    grade_record.status = calculate_status(average)

    db.commit()
    db.refresh(grade_record)
    return grade_record


@app.get("/grade-records", response_model=list[GradeRecordJoined])
def list_grade_records(
    classroom_id: int = Query(...),
    subject_id: int = Query(...),
    db: Session = Depends(get_db),
):
    query = (
        select(GradeRecord, Student, Classroom, Subject)
        .join(Student, Student.id == GradeRecord.student_id)
        .join(Classroom, Classroom.id == GradeRecord.classroom_id)
        .join(Subject, Subject.id == GradeRecord.subject_id)
        .where(GradeRecord.classroom_id == classroom_id, GradeRecord.subject_id == subject_id)
        .order_by(Student.name)
    )

    rows = db.execute(query).all()
    return [
        {
            "id": grade.id,
            "student_id": student.id,
            "student_name": student.name,
            "classroom_id": classroom.id,
            "classroom_name": classroom.name,
            "subject_id": subject.id,
            "subject_name": subject.name,
            "note_1": grade.note_1,
            "note_2": grade.note_2,
            "note_3": grade.note_3,
            "recovery_note": grade.recovery_note,
            "average": grade.average,
            "status": grade.status,
        }
        for grade, student, classroom, subject in rows
    ]
