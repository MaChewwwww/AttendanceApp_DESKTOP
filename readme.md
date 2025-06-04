# AttendanceApp_DESKTOP

A desktop-based attendance system built with Python. This application allows you to manage and track attendance using a local database.

---

## 🛠 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/MaChewwwww/AttendanceApp_DESKTOP.git
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

#### Quick Setup
```bash
# Copy the example file to create your .env
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux
```

**⚠️ IMPORTANT: You must rename `.env.example` to `.env` for the application to work!**

The `.env.example` file is just a template. Your actual configuration must be in a file named `.env` (without the `.example` extension).

#### Google SMTP Setup (Step-by-Step)

1. **Enable 2-Factor Authentication on your Google Account**
   - Go to [Google Account Settings](https://myaccount.google.com/)
   - Navigate to Security > 2-Step Verification
   - Enable 2-factor authentication if not already enabled

2. **Generate an App Password**
   - In Google Account settings, go to Security > App passwords
   - Select "Mail" and your device/app name
   - Copy the 16-character app password (format: `xxxx xxxx xxxx xxxx`)

3. **Edit your .env file (NOT the .env.example file)**
   - Open the `.env` file you created in step 1
   - Update these lines with your actual credentials:
   ```env
   EMAIL_ADDRESS=your-actual-email@gmail.com
   EMAIL_PASSWORD=your-actual-16-character-app-password
   ```

4. **Test Email Configuration** (Optional but Recommended)
   ```bash
   python -c "from app.email_service import EmailService; service = EmailService(); print(service.test_email_configuration())"
   ```

#### File Setup Checklist:
- [ ] Copy `.env.example` to `.env`
- [ ] Edit `.env` with your Gmail credentials  
- [ ] Do NOT edit `.env.example` (this is just the template)
- [ ] Do NOT commit your `.env` file to version control

#### Important Notes:
- ⚠️ **Use App Password, not your regular Gmail password**
- ✅ **App passwords are safer and can be revoked if needed**
- 🔒 **Never commit your actual .env file to version control**
- 📧 **The system sends emails for OTP verification, password reset, and registration confirmation**
- 📁 **The .env file should be in the root directory (same level as main.py)**

#### Troubleshooting Email Issues:
- **File not found error**: Make sure you renamed `.env.example` to `.env`
- **Email credentials not working**: Verify 2FA is enabled on your Google Account
- **Invalid password**: Ensure you're using the App Password (16 characters)
- **Email not sending**: Check spam/junk folders for test emails
- **Permission denied**: Generate a new App Password if issues persist
- **Environment variables not loading**: Verify no extra spaces in EMAIL_ADDRESS or EMAIL_PASSWORD

### 6. Initialize the Database
```bash
python create_db.py
```

### 7. Seed Initial Users (Optional but Recommended)
```bash
python create_seed_users.py
```

This will create default admin and test users for easier setup and testing.

### 8. Run the Application
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
