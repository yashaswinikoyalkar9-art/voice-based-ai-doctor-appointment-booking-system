from datetime import date as Date, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import and_
from db import init_db, SessionLocal, Doctor, Appointment

app = FastAPI(title="CareCall API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173","http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
init_db()

class BookRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=20)
    doctor_id: int
    date: str
    time: str

class PhoneRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=20)

def clean_phone(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 7:
        raise HTTPException(400, "Please provide a valid phone number.")
    return digits

def all_slots(doctor_id: int, day: str):
    # Demo slots, intentionally mocked for the assignment.
    slots = ["09:30", "10:00", "10:30", "11:30", "14:00", "14:30", "15:00", "16:00"]
    with SessionLocal() as db:
        booked = {a.appointment_time for a in db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id, Appointment.appointment_date == day, Appointment.status == "booked").all()}
    return [s for s in slots if s not in booked]

@app.get("/api/doctors")
def doctors():
    with SessionLocal() as db:
        return [{"id":d.id,"name":d.name,"specialty":d.specialty} for d in db.query(Doctor).all()]

@app.get("/api/availability")
def availability(doctor_id: int, date: str):
    try: Date.fromisoformat(date)
    except Exception: raise HTTPException(400, "Date must be YYYY-MM-DD")
    with SessionLocal() as db:
        doctor=db.get(Doctor,doctor_id)
        if not doctor: raise HTTPException(404,"Doctor not found")
        return {"doctor_id":doctor.id,"doctor":doctor.name,"date":date,"slots":all_slots(doctor_id,date)}

@app.get("/api/appointments")
def appointments():
    with SessionLocal() as db:
        rows=db.query(Appointment).order_by(Appointment.appointment_date,Appointment.appointment_time).all()
        return [serialize(a) for a in rows]

def serialize(a):
    return {"id":a.id,"phone":a.patient_phone,"doctor_id":a.doctor_id,"doctor":a.doctor_name,"specialty":a.specialty,"date":a.appointment_date,"time":a.appointment_time,"status":a.status}

@app.post("/api/book")
def book(req: BookRequest):
    phone=clean_phone(req.phone)
    try: Date.fromisoformat(req.date)
    except Exception: raise HTTPException(400,"Date must be YYYY-MM-DD")
    with SessionLocal() as db:
        doctor=db.get(Doctor,req.doctor_id)
        if not doctor: raise HTTPException(404,"Doctor not found")
        if req.time not in all_slots(req.doctor_id,req.date): raise HTTPException(409,"That slot is no longer available.")
        a=Appointment(patient_phone=phone,doctor_id=doctor.id,doctor_name=doctor.name,specialty=doctor.specialty,appointment_date=req.date,appointment_time=req.time)
        db.add(a); db.commit(); db.refresh(a)
        return serialize(a)

@app.post("/api/cancel")
def cancel(req: PhoneRequest):
    phone=clean_phone(req.phone)
    with SessionLocal() as db:
        a=db.query(Appointment).filter(and_(Appointment.patient_phone==phone,Appointment.status=="booked")).order_by(Appointment.appointment_date,Appointment.appointment_time).first()
        if not a: raise HTTPException(404,"No active appointment found for that phone number.")
        a.status="cancelled"; db.commit()
        return serialize(a)

@app.get("/api/health")
def health(): return {"status":"ok"}
