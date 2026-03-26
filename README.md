# Macalester College International Student Program Tax Session Queue & Check-in System 🧾

A full-stack, automated queue management system built for the International Student Program (ISP) at Macalester College. This system digitizes the tax return review process, intelligently routing students to available staff members based on their review stage (Round 1 or Final Review).

## 💡 Background & Motivation
During previous tax seasons, our program relied on a manual and often chaotic process to manage the influx of international students needing tax assistance. This system was developed to solve three critical pain points discovered in our workflow:

1. **Chaotic Queue Management:** Students waiting in physical lines had no visibility into their wait times or queue status, leading to confusion and a poor user experience.
2. **Inefficient Manual Routing:** The tax review requires two distinct phases (Round 1 by a Junior reviewer, Round 2 by a Senior reviewer). Manually tracking who finished Round 1 and finding an available Senior reviewer was error-prone and created bottlenecks.
3. **Lack of Analytics:** We had zero data persistence. We couldn't accurately track how many students were served, average wait times, or individual staff workloads, making it impossible to optimize staffing for future tax seasons.

## ✨ Key Features
* **Intelligent Dispatch Algorithm:** Automatically assigns students to the correct staff role (Junior vs. Senior) and ensures a student doesn't get the same staff member for both rounds.
* **Role-Based Workspaces:** A dedicated interface for students to check in, and a separate dashboard for staff to manage their current cases and advance students to the next round.
* **Automated Notifications:** Triggers email alerts to students when it's their turn, directing them to the specific desk and staff member.
* **Data Persistence for Analytics:** Built with SQLAlchemy and SQLite to log timestamps (`created_at`, `updated_at`) for every status change, laying the groundwork for post-tax-season performance reports.

## 🛠️ Tech Stack
* **Frontend:** React, TypeScript, Vite
* **Backend:** Python, FastAPI
* **Database:** SQLite (managed via SQLAlchemy ORM)
* **Deployment:** Vercel (Frontend) & Render (Backend)

---

## 🔄 System Workflow

1. **Staff Onboarding:** At the start of the session, staff members are added to the system via the `/api/admin/add_staff` endpoint with their specific role (`Junior` or `Senior`) and physical desk location. Their status is set to `Available`.
2. **Student Check-In:** An international student arrives, enters their Macalester email on the frontend, and joins the Round 1 waitlist (`Waiting_R1`).
3. **Round 1 Dispatch:** The algorithm detects an available Junior staff member, updates the database, and sends an email to the student: *"Please go to Desk A to meet with Alice."*
4. **Transition to Final Review:** Once Alice finishes Round 1, she enters her Staff ID and the student's email on the Staff Dashboard and clicks "Complete Round 1". The student is seamlessly pushed to the `Waiting_R2` queue.
5. **Round 2 Dispatch:** The algorithm immediately searches for an available Senior staff member (who is NOT Alice) and dispatches the student for their final review.
6. **Completion:** The Senior staff clicks "Complete Final", the student's status changes to `Done`, and they receive a final confirmation email.
