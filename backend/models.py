from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String)  # "Junior" or "Senior"
    desk = Column(String)  # e.g., "Table 1"
    status = Column(String, default="Offline")  # "Available", "Busy", "Offline"

class Student(Base):
    __tablename__ = "students"

    email = Column(String, primary_key=True, index=True)
    status = Column(String, default="Waiting_R1") 

    r1_staff_id = Column(Integer, ForeignKey("staff.id"), nullable=True)
    r2_staff_id = Column(Integer, ForeignKey("staff.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())