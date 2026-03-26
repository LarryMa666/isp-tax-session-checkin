from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

# Import the database configuration and models we just created
import models
from database import engine, get_db

# CRITICAL: This line automatically creates the SQLite database and all tables locally when the app starts!
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 1. Pydantic Models (Data formats sent from frontend to backend)
# ==========================================
class StudentCheckIn(BaseModel):
    email: str

class StaffAction(BaseModel):
    staff_id: int
    student_email: str

class StaffCreate(BaseModel):
    name: str
    email: str
    role: str
    desk: str

# ==========================================
# 2. Mock Email Notification Function
# ==========================================
def send_email_notification(email: str, subject: str, body: str):
    print("\n" + "="*40)
    print(f"📧 Sending email to: {email}")
    print(f"📌 Subject: {subject}")
    print(f"✉️ Body: {body}")
    print("="*40 + "\n")

# ==========================================
# 3. Core Dispatch Algorithm (Connected to real SQLite database)
# ==========================================
def trigger_dispatch(db: Session):
    """Trigger this algorithm whenever a student queues up or a staff member becomes available."""
    
    # Find all available staff
    available_staff = db.query(models.Staff).filter(models.Staff.status == "Available").all()
    if not available_staff:
        return

    # ---------------- Priority 1: Process students waiting for Round 2 ----------------
    # Fetch in chronological order based on queue time (created_at)
    waiting_r2_students = db.query(models.Student).filter(models.Student.status == "Waiting_R2").order_by(models.Student.created_at).all()
    
    for student in waiting_r2_students:
        # Find an eligible Senior (must be a Senior, and cannot be the one who did Round 1)
        eligible_seniors = [s for s in available_staff if s.role == "Senior" and s.id != student.r1_staff_id]
        
        if eligible_seniors:
            chosen_staff = eligible_seniors[0]
            
            # Update database status
            chosen_staff.status = "Busy"
            student.status = "In_Progress_R2"
            student.r2_staff_id = chosen_staff.id
            db.commit() # Commit changes to the database
            
            send_email_notification(
                student.email, 
                "Your Final Review is Ready!", 
                f"Please go to {chosen_staff.desk} to meet with {chosen_staff.name} for Round 2."
            )
            # Refresh the available_staff list
            available_staff = db.query(models.Staff).filter(models.Staff.status == "Available").all()
            if not available_staff: return

    # ---------------- Priority 2: Process students waiting for Round 1 ----------------
    waiting_r1_students = db.query(models.Student).filter(models.Student.status == "Waiting_R1").order_by(models.Student.created_at).all()
    
    for student in waiting_r1_students:
        # Prioritize Junior staff for Round 1, fallback to Senior if no Junior is available
        juniors = [s for s in available_staff if s.role == "Junior"]
        chosen_staff = juniors[0] if juniors else available_staff[0]
        
        # Update database status
        chosen_staff.status = "Busy"
        student.status = "In_Progress_R1"
        student.r1_staff_id = chosen_staff.id
        db.commit() # Commit changes to the database
        
        send_email_notification(
            student.email, 
            "Your Round 1 Review is Ready!", 
            f"Please go to {chosen_staff.desk} to meet with {chosen_staff.name} for Round 1."
        )
        available_staff = db.query(models.Staff).filter(models.Staff.status == "Available").all()
        if not available_staff: return

# ==========================================
# 4. API Endpoints
# ==========================================

# Since the database is initially empty, we need an endpoint to add staff who are working today
@app.post("/api/admin/add_staff")
def add_staff(staff: StaffCreate, db: Session = Depends(get_db)):
    new_staff = models.Staff(name=staff.name, email=staff.email, role=staff.role, desk=staff.desk, status="Available")
    db.add(new_staff)
    db.commit()
    return {"message": f"Staff {staff.name} added and is Available."}

@app.post("/api/checkin")
def student_checkin(student: StudentCheckIn, db: Session = Depends(get_db)):
    # Check if the student already exists in the database
    db_student = db.query(models.Student).filter(models.Student.email == student.email).first()
    
    if not db_student:
        # Create a new student record and write it to SQLite
        new_student = models.Student(email=student.email, status="Waiting_R1")
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        
        # Trigger the dispatch algorithm
        trigger_dispatch(db)
        return {"message": "You are in the Round 1 queue. Check your email for updates!"}
    
    return {"message": f"You are already in the system. Current status: {db_student.status}"}

@app.post("/api/staff/complete_round1")
def staff_complete_r1(action: StaffAction, db: Session = Depends(get_db)):
    staff = db.query(models.Staff).filter(models.Staff.id == action.staff_id).first()
    student = db.query(models.Student).filter(models.Student.email == action.student_email).first()
    
    if staff and student:
        staff.status = "Available"
        student.status = "Waiting_R2"
        db.commit()
        
        trigger_dispatch(db)
        return {"message": f"Round 1 complete for {student.email}. They are in R2 queue."}
    raise HTTPException(status_code=404, detail="Staff or Student not found")

@app.post("/api/staff/complete_round2")
def staff_complete_r2(action: StaffAction, db: Session = Depends(get_db)):
    staff = db.query(models.Staff).filter(models.Staff.id == action.staff_id).first()
    student = db.query(models.Student).filter(models.Student.email == action.student_email).first()
    
    if staff and student:
        staff.status = "Available"
        student.status = "Done"
        db.commit()
        
        send_email_notification(student.email, "Tax Review Complete", "Congratulations! You are all set.")
        trigger_dispatch(db)
        return {"message": f"Final review complete for {student.email}."}
    raise HTTPException(status_code=404, detail="Staff or Student not found")