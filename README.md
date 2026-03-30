# universal-health-record-system

# Universal Health Records Sharing System (UHRS)

A web-based platform that enables secure sharing of patient medical records across hospitals and clinics using a patient's national ID number.

## Live URL
https://universal-health-record-system-production.up.railway.app

## Tech Stack
- Python (Flask)
- Supabase (PostgreSQL database)
- Plain HTML, CSS, JavaScript

## Setup Instructions

### 1. Clone the repository

git clone https://github.com/Fadhili-N/universal-health-record-system.git
cd universal-health-record-system


### 2. Create and activate virtual environment

python -m venv venv
venv\Scripts\activate

### 3. Install dependencies

pip install -r requirements.txt


### 4. Create a `.env` file in the project root

SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SECRET_KEY=uhrs_secret_2026


### 5. Run the application

python app.py


### 6. Open in browser

http://127.0.0.1:5000

## Test Credentials
- **Doctor login:** username: `doctor1` password: `password123`
- **Admin login:** username: `admin1` password: `admin123`

## Features
- Healthcare worker login with role-based access
- Patient registration using national ID number
- Search patients by national ID
- View full medical history
- Add and update medical records
- Admin panel for managing healthcare workers
- Audit log for tracking all system access