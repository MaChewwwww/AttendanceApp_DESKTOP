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

### 5. Configure Email Settings (Required for Email Verification)

1. **Enable 2-Factor Authentication on your Google Account**
   - Go to your Google Account settings
   - Navigate to Security > 2-Step Verification
   - Enable 2-factor authentication if not already enabled

2. **Generate an App Password**
   - In Google Account settings, go to Security > App passwords
   - Select "Mail" and your device
   - Copy the 16-character app password

3. **Create Environment File**
   - Copy `.env.example` to `.env` (or create `.env` file)
   - Update the email configuration:
   ```
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_PASSWORD=your-16-character-app-password
   ```

4. **Test Email Configuration** (Optional)
   ```bash
   python -c "from app.email_service import EmailService; service = EmailService(); print(service.test_email_configuration())"
   ```

### 6. Initialize the Database
```bash
python create_db.py
```

### 7. Run the Application
```bash
python main.py
```




## 📧 Email Features

The application now includes:
- **Email Verification**: New users receive verification emails
- **Password Reset**: Users can request password reset via email
- **Welcome Emails**: Sent after successful email verification
- **HTML Email Templates**: Professional-looking email designs

## 📲 Features
### ✅ Web App (Student Portal)
- Login and face-based attendance submission
- Email verification for new accounts
- Password reset functionality
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
- Email verification endpoints
- Password reset endpoints
- Fast and scalable interface for cross-platform support
- Secured with token-based authentication

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
7. Email Service
- Gmail SMTP, HTML Templates, Token-based verification
