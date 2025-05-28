# AttendanceApp_DESKTOP

A desktop-based attendance system built with Python. This application allows you to manage and track attendance using a local database.

---

## 🛠 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AttendanceApp_DESKTOP.git
cd AttendanceApp_DESKTOP
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
```

### 3. Activate the Virtual Environment
```bash
venv\Scripts\activate
```

### 4. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 5. Initialize the Database
```bash
python create_db.py
```

6. Run the Application
```bash
python main.py
```




## 🎨 System Design Overview
### 🧩 Components & Tech Stack
1. Web App	Student Portal
- ASP.NET MVC, Razor, Tailwind, JS
2. Desktop App Admin System	
- Python, Tkinter, OpenCV, MySQL
3. Web API
-	FastAPI, Python, SQLite
4. Database	
- Centralized Data Management	SQLite
5. Analytics Attendance Visualizations	
- Chart.js (Web), Matplotlib (Desktop)
6. Security	Secure Authentication & Sessions	
- Token-Based API Auth, ASP.NET Sessions


## 📲 Features
### ✅ Web App (Student Portal)
- Login and face-based attendance submission
- Visual dashboard with charts showing attendance trends
- Real-time feedback on absences
- Personalized analytics (per subject/week)

### 🖥 Desktop App (Admin/Faculty)
- Admin/staff login
- Manage courses, sections, and student records
- Access and validate attendance logs
- Manual override for special cases

### 🌐 Web API (Backend)
- RESTful endpoints for login, attendance, and data sync
- Fast and scalable interface for cross-platform support
- Secured with token-based authentication
