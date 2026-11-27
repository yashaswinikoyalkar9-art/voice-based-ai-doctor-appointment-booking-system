from datetime import date, time, datetime
from sqlalchemy import create_engine, String, Integer, Date, Time, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./appointments.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase): pass

class Doctor(Base):
    __tablename__ = "doctors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    specialty: Mapped[str] = mapped_column(String, nullable=False)

class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_phone: Mapped[str] = mapped_column(String, index=True, nullable=False)
    doctor_id: Mapped[int] = mapped_column(Integer, nullable=False)
    doctor_name: Mapped[str] = mapped_column(String, nullable=False)
    specialty: Mapped[str] = mapped_column(String, nullable=False)
    appointment_date: Mapped[str] = mapped_column(String, nullable=False)
    appointment_time: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="booked")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.query(Doctor).count() == 0:
            db.add_all([
                Doctor(name="Dr. Ananya Rao", specialty="General Physician"),
                Doctor(name="Dr. Vikram Shah", specialty="Cardiology"),
                Doctor(name="Dr. Meera Iyer", specialty="Dermatology"),
                Doctor(name="Dr. Rahul Nair", specialty="Orthopedics"),
            ])
            db.commit()
