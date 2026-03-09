from pydantic import BaseModel, Field


class ClassroomCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class ClassroomRead(ClassroomCreate):
    id: int

    class Config:
        from_attributes = True


class SubjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class SubjectRead(SubjectCreate):
    id: int

    class Config:
        from_attributes = True


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    classroom_id: int


class StudentRead(StudentCreate):
    id: int

    class Config:
        from_attributes = True


class GradeRecordCreate(BaseModel):
    student_id: int
    classroom_id: int
    subject_id: int
    note_1: float | None = Field(default=None, ge=0, le=10)
    note_2: float | None = Field(default=None, ge=0, le=10)
    note_3: float | None = Field(default=None, ge=0, le=10)
    recovery_note: float | None = Field(default=None, ge=0, le=10)


class GradeRecordUpdate(BaseModel):
    note_1: float | None = Field(default=None, ge=0, le=10)
    note_2: float | None = Field(default=None, ge=0, le=10)
    note_3: float | None = Field(default=None, ge=0, le=10)
    recovery_note: float | None = Field(default=None, ge=0, le=10)


class GradeRecordRead(GradeRecordCreate):
    id: int
    average: float
    status: str

    class Config:
        from_attributes = True


class GradeRecordJoined(BaseModel):
    id: int
    student_id: int
    student_name: str
    classroom_id: int
    classroom_name: str
    subject_id: int
    subject_name: str
    note_1: float | None
    note_2: float | None
    note_3: float | None
    recovery_note: float | None
    average: float
    status: str
