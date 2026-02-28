# 🏢 HRMS Lite

Hey there! Welcome to HRMS Lite - a simple, clean HR management system I built to help small teams manage their employees and track attendance without all the complexity of enterprise solutions.

## ✨ What Can It Do?

This app keeps things straightforward:

- **Manage Your Team**: Add new employees, see everyone at a glance, and remove people when they leave
- **Track Attendance**: Mark who's present or absent each day and view attendance history
- **Stay Organized**: Built-in validation ensures emails are valid, employee IDs are unique, and all required info is filled in
- **Dashboard Overview**: See your team stats, department breakdown, and recent activity at a glance
- **Filter & Search**: Find attendance records by date range and see attendance rates
- **Works Everywhere**: Clean, professional interface that looks good on any screen

## 🛠️ Tech Stack

I chose these technologies for their reliability and ease of use:

**Frontend**
- React 19 with Vite (because fast refresh is life)
- Vanilla CSS (keeping it simple and performant)
- Modern JavaScript (no unnecessary complexity)

**Backend**
- FastAPI (Python's fastest web framework)
- SQLAlchemy (makes database work a breeze)
- MySQL (reliable and widely supported)
- Pydantic (automatic data validation)

## 📋 What You'll Need

Before getting started, make sure you have:
- Node.js 18 or higher
- Python 3.9 or higher
- MySQL 8.0 or higher

## 🚀 Getting Started

### Setting Up the Backend

1. Jump into the backend folder:
```bash
cd backend
```

2. Create a virtual environment (keeps things tidy):
```bash
python -m venv venv
source venv/bin/activate  # Windows folks: venv\Scripts\activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your database info:
```env
DATABASE_URL=mysql+pymysql://root:12345678@127.0.0.1:3306/hrms_lite
FRONTEND_URL=http://localhost:5173
```

5. Fire up the server:
```bash
uvicorn main:app --reload
```

Your API is now running at `http://localhost:8000` 🎉

### Setting Up the Frontend

1. Navigate to the frontend folder:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file:
```env
VITE_API_URL=http://localhost:8000
```

4. Start the dev server:
```bash
npm run dev
```

Open `http://localhost:5173` and you're good to go! 🚀

## 📊 Want Some Sample Data?

I've included a SQL file with 50 employees and their attendance for February 2026. To load it:

**Easy way (Windows):**
```bash
cd backend
load_sample_data.bat
```

**Manual way:**
```bash
mysql -h 127.0.0.1 -P 3306 -u root -p12345678 hrms_lite < backend/sample_data.sql
```

This gives you realistic data to play with right away!

## 🔧 Configuration

### Backend Environment Variables

| Variable | What It Does | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Your MySQL connection string | `mysql+pymysql://root:pass@localhost:3306/hrms_lite` |
| `FRONTEND_URL` | Where your frontend lives (for CORS) | `http://localhost:5173` |

### Frontend Environment Variables

| Variable | What It Does | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Where your backend API lives | `http://localhost:8000` |

## 🌐 Deploying to Production

Ready to share your app with the world? Here's how:

### Deploy Frontend (Vercel - Recommended)

Vercel makes this super easy:

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
cd frontend
vercel
```

3. Add your backend URL in Vercel dashboard:
   - Go to your project settings
   - Add environment variable: `VITE_API_URL` = your backend URL
   - Redeploy

**Or use the Vercel dashboard:**
- Connect your GitHub repo
- Point to the `frontend` folder
- Add the `VITE_API_URL` environment variable
- Hit deploy!

### Deploy Backend (Railway - Recommended)

Railway is great for Python apps:

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Deploy:
```bash
cd backend
railway login
railway init
railway up
```

3. Add environment variables in Railway dashboard:
   - `DATABASE_URL`: Your MySQL connection string
   - `FRONTEND_URL`: Your Vercel URL

**Or use Railway dashboard:**
- Connect your GitHub repo
- Point to the `backend` folder
- Add environment variables
- Railway handles the rest!

### Alternative: Render for Backend

Render is another solid choice:

1. Create a new Web Service
2. Connect your GitHub repo
3. Configure:
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables
5. Deploy!

## 📡 API Reference

Here's what the API can do:

### Employee Endpoints

**Create an Employee**
```http
POST /employees
Content-Type: application/json

{
  "employee_id": "EMP001",
  "name": "Priya Sharma",
  "email": "priya.sharma@company.com",
  "department": "Engineering"
}
```
Returns: `201 Created` on success, `409 Conflict` if ID exists

**Get All Employees**
```http
GET /employees
```
Returns: `200 OK` with array of all employees

**Delete an Employee**
```http
DELETE /employees/EMP001
```
Returns: `204 No Content` on success, `404 Not Found` if employee doesn't exist

### Attendance Endpoints

**Mark Attendance**
```http
POST /attendance
Content-Type: application/json

{
  "employee_id": "EMP001",
  "date": "2026-02-28",
  "status": "Present"
}
```
Returns: `201 Created` on success

**Get Employee Attendance**
```http
GET /attendance/EMP001
```
Returns: `200 OK` with attendance records (newest first)

## 🧪 Testing

Want to make sure everything works? Here's how:

**Backend Tests**
```bash
cd backend
pytest
```

I've included property-based tests that check all the important stuff - validation, uniqueness, cascade deletes, etc.

**Frontend Testing**
The frontend is tested manually (sometimes the old ways are the best ways):
1. Fire up both servers
2. Try creating, viewing, and deleting employees
3. Mark some attendance and check the records
4. Make sure errors show up when they should

## 📁 Project Structure

Here's how everything is organized:

```
hrms-lite/
├── backend/
│   ├── main.py                    # FastAPI app and all routes
│   ├── models.py                  # Database models (Employee, Attendance)
│   ├── schemas.py                 # Request/response validation
│   ├── database.py                # Database connection setup
│   ├── crud.py                    # Database operations
│   ├── sample_data.sql            # 50 employees + 1,400 attendance records
│   ├── load_sample_data.bat       # Easy data loading script
│   ├── requirements.txt           # Python packages
│   ├── test_*.py                  # Property-based tests
│   └── deployment configs         # Railway, Render, Procfile
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main app with tab navigation
│   │   ├── components/
│   │   │   ├── Dashboard.jsx      # Overview with stats
│   │   │   ├── EmployeeList.jsx   # View all employees
│   │   │   ├── EmployeeForm.jsx   # Add new employees
│   │   │   ├── AttendanceForm.jsx # Mark attendance
│   │   │   ├── AttendanceView.jsx # View attendance records
│   │   │   └── common/            # Reusable UI components
│   │   └── services/
│   │       └── api.js             # API calls
│   ├── package.json
│   └── deployment configs         # Vercel, Netlify
│
└── README.md                      # You are here! 👋
```

## 🎯 Design Choices

A few decisions I made along the way:

- **No Authentication**: Kept it simple for a single admin user. In a real app, you'd definitely want proper auth!
- **No Edit Feature**: You can create and delete, but not edit. This keeps the data trail clean and simple.
- **MySQL**: Widely supported, reliable, and available on most free hosting tiers.
- **Minimal Dependencies**: Only what we actually need - keeps things fast and maintainable.
- **Component CSS**: No heavy frameworks - just clean, scoped styles that do the job.

## 💡 Ideas for the Future

Some things that would be cool to add:
- User login and different permission levels
- Edit employee details and attendance records
- More advanced filtering and search
- Department management
- Import employees from CSV
- Export reports to PDF
- Email notifications
- Better mobile experience
- Dark mode (because why not?)

## 📝 Note

This was built as a coding assignment to demonstrate full-stack development skills. Feel free to use it, learn from it, or build upon it!

## 🤝 Questions?

If something's not working or you have questions, feel free to open an issue. I'm happy to help!

---

Made with ☕ and code
