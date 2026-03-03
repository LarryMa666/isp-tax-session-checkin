from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 1. 模拟数据库 (内存版)
# ==========================================
# 员工数据结构
staff_db: Dict[int, dict] = {
    1: {"id": 1, "name": "Alice", "role": "Junior", "status": "Available", "desk": "Desk A"},
    2: {"id": 2, "name": "Bob", "role": "Senior", "status": "Available", "desk": "Desk B"},
    3: {"id": 3, "name": "Charlie", "role": "Senior", "status": "Available", "desk": "Desk C"},
}

# 学生数据结构: 记录学生当前的状态和初审是谁做的
student_db: Dict[str, dict] = {} 

# 两个排队队列
queue_r1: List[str] = [] # 等待第一轮初审的学生 email 列表
queue_r2: List[str] = [] # 等待第二轮终审的学生 email 列表

# ==========================================
# 2. 数据模型 (接收前端传来的数据格式)
# ==========================================
class StudentCheckIn(BaseModel):
    email: str

class StaffAction(BaseModel):
    staff_id: int
    student_email: str

# ==========================================
# 3. 核心工具函数
# ==========================================
def send_email_notification(email: str, subject: str, body: str):
    """模拟发送邮件，打印在终端里"""
    print("\n" + "="*40)
    print(f"📧 正在发送邮件至: {email}")
    print(f"📌 主题: {subject}")
    print(f"✉️ 正文: {body}")
    print("="*40 + "\n")

def trigger_dispatch():
    """核心派单算法：当有员工空闲，或者有新学生排队时触发"""
    
    # 获取所有空闲员工
    available_staff = [s for s in staff_db.values() if s["status"] == "Available"]
    if not available_staff:
        return # 没人空闲，直接结束

    # 优先级 1：先处理等待第二轮 (Round 2) 的学生
    for student_email in list(queue_r2):
        student_info = student_db[student_email]
        r1_staff_id = student_info.get("r1_staff_id")
        
        # 寻找符合条件的 Senior：必须是 Senior，且不能是做初审的那个人
        eligible_seniors = [s for s in available_staff if s["role"] == "Senior" and s["id"] != r1_staff_id]
        
        if eligible_seniors:
            chosen_staff = eligible_seniors[0]
            # 更新状态
            chosen_staff["status"] = "Busy"
            queue_r2.remove(student_email)
            student_db[student_email]["status"] = "In_Progress_R2"
            
            # 发邮件通知学生
            send_email_notification(
                student_email, 
                "Your Final Review is Ready!", 
                f"Please go to {chosen_staff['desk']} to meet with {chosen_staff['name']} for your Round 2 review."
            )
            # 重新获取最新的空闲员工列表，继续下一次循环
            available_staff = [s for s in staff_db.values() if s["status"] == "Available"]

    # 优先级 2：处理等待第一轮 (Round 1) 的学生
    for student_email in list(queue_r1):
        if not available_staff:
            break
            
        # 寻找符合条件的员工：优先找 Junior，如果没有，再找 Senior
        juniors = [s for s in available_staff if s["role"] == "Junior"]
        chosen_staff = juniors[0] if juniors else available_staff[0]
        
        # 更新状态
        chosen_staff["status"] = "Busy"
        queue_r1.remove(student_email)
        student_db[student_email]["status"] = "In_Progress_R1"
        student_db[student_email]["r1_staff_id"] = chosen_staff["id"] # 记录初审人！！！
        
        # 发邮件通知学生
        send_email_notification(
            student_email, 
            "Your Round 1 Review is Ready!", 
            f"Please go to {chosen_staff['desk']} to meet with {chosen_staff['name']} for your Round 1 review."
        )
        available_staff = [s for s in staff_db.values() if s["status"] == "Available"]


# ==========================================
# 4. API 路由 (Endpoints)
# ==========================================
@app.post("/api/checkin")
async def student_checkin(student: StudentCheckIn):
    email = student.email
    
    if email not in student_db:
        # 新来的学生，进入初审队列
        student_db[email] = {"status": "Waiting_R1"}
        queue_r1.append(email)
        trigger_dispatch() # 触发派单看看有没有人空闲
        return {"message": "You are in the Round 1 queue. Check your email for updates!"}
    else:
        return {"message": "You are already in the system."}

@app.post("/api/staff/complete_round1")
async def staff_complete_r1(action: StaffAction):
    """Staff 点击完成初审：把学生放入终审队列，自己变回空闲"""
    staff = staff_db.get(action.staff_id)
    email = action.student_email
    
    if staff and email in student_db:
        staff["status"] = "Available"
        student_db[email]["status"] = "Waiting_R2"
        queue_r2.append(email)
        
        trigger_dispatch() # Staff空闲了，也把学生放进下一轮了，触发全局调度
        return {"message": f"Round 1 complete for {email}. They are now in R2 queue."}

@app.post("/api/staff/complete_round2")
async def staff_complete_r2(action: StaffAction):
    """Staff 点击完成终审：学生彻底完成报税，自己变回空闲"""
    staff = staff_db.get(action.staff_id)
    email = action.student_email
    
    if staff and email in student_db:
        staff["status"] = "Available"
        student_db[email]["status"] = "Done"
        
        send_email_notification(email, "Tax Review Complete", "Congratulations! Your tax review is fully complete.")
        trigger_dispatch() # Staff空闲了，看看还有没有别的排队学生
        return {"message": f"Final review complete for {email}."}