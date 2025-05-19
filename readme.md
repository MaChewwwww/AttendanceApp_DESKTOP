1. Clone the repository
git clone https://github.com/yourusername/AttendanceApp_DESKTOP.git
cd AttendanceApp_DESKTOP

2. Create a virtual environment (recommended)
python -m venv venv

3. Activate the virtual environment

Windows : 
venv\Scripts\activate

Linux :
source venv/bin/activate

4. Install dependencies
pip install -r requirements.txt

5. Create the database
python create_db.py

6. Running the Application
Ensure your virtual environment is activated (if using one). Launch the application :
python main.py