
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)
    is_elective: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    likes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    level: Mapped[str]

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="course"
    )

    __table_args__ = (
        CheckConstraint("credits > 0", name="credits_check"),
        CheckConstraint("likes >= 0", name="likes_check"),
    )


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        name="email",
    )
    

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="student",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint(
            "char_length(name) >= 2",
            name="name_check"
        ),
        CheckConstraint(
            "position('@' IN email) > 1",
            name="email_format"
        ),
        UniqueConstraint(
            "email",
            name="students_email_key"
        ),
    )


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )
    course_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("courses.id", ondelete="RESTRICT"),
        nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    course: Mapped["Course"] = relationship(back_populates="enrollments")
    student: Mapped["Student"] = relationship(back_populates="enrollments")

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "student_id",
            name="enrollments_course_id_student_id_key"
        ),
        Index("enrollments_student_id_idx", "student_id"),
    )
