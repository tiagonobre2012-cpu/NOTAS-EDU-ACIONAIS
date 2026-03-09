from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Classroom(Base):
    __tablename__ = "classrooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    students = relationship("Student", back_populates="classroom", cascade="all, delete-orphan")
    grade_records = relationship("GradeRecord", back_populates="classroom", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    grade_records = relationship("GradeRecord", back_populates="subject", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (UniqueConstraint("name", "classroom_id", name="uq_student_name_classroom"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id", ondelete="CASCADE"), index=True)

    classroom = relationship("Classroom", back_populates="students")
    grade_records = relationship("GradeRecord", back_populates="student", cascade="all, delete-orphan")


class GradeRecord(Base):
    __tablename__ = "grade_records"
    __table_args__ = (
        UniqueConstraint("student_id", "classroom_id", "subject_id", name="uq_grade_record_unique"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)

    note_1: Mapped[float | None] = mapped_column(Float, nullable=True)
    note_2: Mapped[float | None] = mapped_column(Float, nullable=True)
    note_3: Mapped[float | None] = mapped_column(Float, nullable=True)
    recovery_note: Mapped[float | None] = mapped_column(Float, nullable=True)
    average: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(30), default="PENDING")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="grade_records")
    classroom = relationship("Classroom", back_populates="grade_records")
    subject = relationship("Subject", back_populates="grade_records")
