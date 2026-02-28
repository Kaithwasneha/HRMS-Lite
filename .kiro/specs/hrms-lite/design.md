# Design Document: HRMS Lite

## Overview

HRMS Lite is a full-stack web application with a React frontend and FastAPI backend. The system provides employee management and attendance tracking capabilities for small organizations. The architecture follows a client-server model with RESTful API communication.

## Technology Stack

### Frontend
- **Framework**: React 18+ with Vite
- **Language**: JavaScript/JSX
- **Styling**: CSS3 (component-scoped)
- **HTTP Client**: Fetch API
- **Deployment**: Vercel or Netlify

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: MySQL (primary choice for deployment compatibility)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic models
- **CORS**: FastAPI CORS middleware
- **Deployment**: Render or Railway

## System Architecture

```
┌─────────────────┐         HTTP/REST        ┌─────────────────┐
│                 │ ◄────────────────────────►│                 │
│  React Frontend │                           │  FastAPI Backend│
│   (Port 5173)   │                           │   (Port 8000)   │
│                 │                           │                 │
└─────────────────┘                           └────────┬────────┘
                                                       │
                                                       │ SQLAlchemy
                                                       ▼
                                              ┌─────────────────┐
                                              │      MySQL      │
                                              │    Database     │
                                              └─────────────────┘
```

## Data Models

### Employee Model

```python
class Employee:
    employee_id: str (Primary Key, Unique)
    name: str (Required)
    email: str (Required, Email Format)
    department: str (Required)
```

**Constraints**:
- `employee_id`: Unique, non-empty string
- `email`: Must match email regex pattern
- All fields are required (non-nullable)

### Attendance Model

```python
class Attendance:
    id: int (Primary Key, Auto-increment)
    employee_id: str (Foreign Key → Employee.employee_id, Cascade Delete)
    date: date (Required)
    status: str (Required, Enum: "Present" | "Absent")
```

**Constraints**:
- `status`: Must be exactly "Present" or "Absent"
- `employee_id`: Must reference existing employee
- Cascade delete: When employee deleted, all attendance records deleted

## API Endpoints

### Employee Endpoints

#### POST /employees
Create a new employee record.

**Request Body**:
```json
{
  "employee_id": "string",
  "name": "string",
  "email": "string",
  "department": "string"
}
```

**Responses**:
- `201 Created`: Employee created successfully
- `409 Conflict`: Employee ID already exists
- `422 Unprocessable Entity`: Validation error (invalid email, missing fields)

**Validates**: Requirements 1.1, 2.1, 2.2, 3.1, 3.2, 4.1-4.5

#### GET /employees
Retrieve all employee records.

**Responses**:
- `200 OK`: Returns array of employee objects

**Validates**: Requirements 1.2

#### DELETE /employees/{employee_id}
Delete an employee and all associated attendance records.

**Responses**:
- `204 No Content`: Employee deleted successfully
- `404 Not Found`: Employee not found

**Validates**: Requirements 1.3

### Attendance Endpoints

#### POST /attendance
Create an attendance record.

**Request Body**:
```json
{
  "employee_id": "string",
  "date": "YYYY-MM-DD",
  "status": "Present" | "Absent"
}
```

**Responses**:
- `201 Created`: Attendance recorded successfully
- `404 Not Found`: Employee not found
- `422 Unprocessable Entity`: Invalid status or date format

**Validates**: Requirements 5.1, 5.3, 5.4

#### GET /attendance/{employee_id}
Retrieve all attendance records for a specific employee.

**Responses**:
- `200 OK`: Returns array of attendance objects sorted by date (descending)
- `404 Not Found`: Employee not found

**Validates**: Requirements 6.1

## Frontend Architecture

### Component Structure

```
src/
├── App.jsx                 # Root component with routing
├── components/
│   ├── EmployeeList.jsx    # Display all employees
│   ├── EmployeeForm.jsx    # Add new employee
│   ├── AttendanceForm.jsx  # Mark attendance
│   ├── AttendanceView.jsx  # View attendance records
│   └── common/
│       ├── Button.jsx      # Reusable button
│       ├── Input.jsx       # Reusable input field
│       └── Table.jsx       # Reusable data table
├── services/
│   └── api.js              # API client functions
└── styles/
    └── App.css             # Global styles
```

### Component Responsibilities

#### App.jsx
- Navigation between Employee Management and Attendance Management
- Route handling (if using React Router) or conditional rendering
- Global error boundary

#### EmployeeList.jsx
- Fetch and display all employees in table format
- Delete employee functionality
- Loading and empty states
- Error handling

**Validates**: Requirements 1.4, 9.1, 9.2, 9.4

#### EmployeeForm.jsx
- Form with fields: employee_id, name, email, department
- Client-side validation (required fields, email format)
- Submit to POST /employees endpoint
- Display success/error messages

**Validates**: Requirements 1.5, 3.3, 3.4, 4.6

#### AttendanceForm.jsx
- Employee selection dropdown
- Date picker (defaults to today)
- Status radio buttons (Present/Absent)
- Submit to POST /attendance endpoint
- Display success/error messages

**Validates**: Requirements 5.2

#### AttendanceView.jsx
- Employee selection dropdown
- Fetch and display attendance records for selected employee
- Display in chronological order (newest first)
- Show employee name, date, status
- Loading and empty states

**Validates**: Requirements 6.2, 6.3, 9.3

#### Common Components
- **Button.jsx**: Consistent button styling, loading states
- **Input.jsx**: Form input with label, validation error display
- **Table.jsx**: Reusable table with headers and rows

**Validates**: Requirements 11.1-11.4

### State Management
- Component-level state using React hooks (useState, useEffect)
- No global state management library needed for this scope

### API Service Layer

```javascript
// services/api.js
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const employeeAPI = {
  getAll: async () => { /* GET /employees */ },
  create: async (data) => { /* POST /employees */ },
  delete: async (id) => { /* DELETE /employees/{id} */ }
};

export const attendanceAPI = {
  create: async (data) => { /* POST /attendance */ },
  getByEmployee: async (employeeId) => { /* GET /attendance/{employeeId} */ }
};
```

## Backend Architecture

### Project Structure

```
backend/
├── main.py                 # FastAPI app initialization, CORS, routes
├── models.py               # SQLAlchemy models
├── schemas.py              # Pydantic schemas for validation
├── database.py             # Database connection and session
├── crud.py                 # Database operations
└── requirements.txt        # Python dependencies
```

### Module Responsibilities

#### main.py
- FastAPI app instance
- CORS middleware configuration
- Route definitions
- Error handling middleware
- Health check endpoint

#### models.py
- SQLAlchemy ORM models for Employee and Attendance
- Database table definitions
- Relationships and constraints

**Validates**: Requirements 12.1, 12.2

#### schemas.py
- Pydantic models for request/response validation
- Email validation using regex
- Status enum validation
- Required field validation

**Validates**: Requirements 3.1, 4.1-4.5, 5.3

#### database.py
- Database connection string (from environment variable)
- SQLAlchemy engine and session management
- Database initialization

**Validates**: Requirements 12.3, 12.4

#### crud.py
- Database CRUD operations
- Employee creation with uniqueness check
- Cascade delete for attendance records
- Query functions

**Validates**: Requirements 1.1-1.3, 2.1, 5.1, 6.1

### Error Handling Strategy

```python
# HTTP Status Code Mapping
- 200 OK: Successful GET request
- 201 Created: Successful POST request
- 204 No Content: Successful DELETE request
- 404 Not Found: Resource not found
- 409 Conflict: Duplicate employee_id
- 422 Unprocessable Entity: Validation error
- 500 Internal Server Error: Server error
```

**Validates**: Requirements 7.6, 8.1-8.4

### Validation Rules

#### Employee Validation
1. All fields required (employee_id, name, email, department)
2. Email must match pattern: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
3. Employee_id must be unique (database constraint + application check)

#### Attendance Validation
1. Employee_id must exist in database
2. Date must be valid ISO format (YYYY-MM-DD)
3. Status must be exactly "Present" or "Absent"

## Deployment Configuration

### Frontend Deployment (Vercel/Netlify)

**Environment Variables**:
- `VITE_API_URL`: Backend API URL (e.g., https://hrms-api.railway.app)

**Build Configuration**:
- Build command: `npm run build`
- Output directory: `dist`
- Node version: 18+

**Validates**: Requirements 13.1, 13.3

### Backend Deployment (Render/Railway)

**Environment Variables**:
- `DATABASE_URL`: MySQL connection string (e.g., mysql://user:password@host:3306/dbname)
- `FRONTEND_URL`: Frontend URL for CORS (e.g., https://hrms-lite.vercel.app)

**Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Validates**: Requirements 13.2, 13.4

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",  # Local development
    os.getenv("FRONTEND_URL")  # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Validates**: Requirements 13.4

## UI/UX Design Principles

### Visual Design
- **Color Scheme**: Professional blue/gray palette
  - Primary: #2563eb (blue)
  - Secondary: #64748b (gray)
  - Success: #10b981 (green)
  - Error: #ef4444 (red)
- **Typography**: System font stack for performance
- **Spacing**: 8px base unit (8, 16, 24, 32px)

**Validates**: Requirements 10.1-10.3

### Responsive Design
- Minimum width: 320px (mobile)
- Optimal width: 1024px+ (desktop)
- Flexible layouts using CSS Grid/Flexbox

**Validates**: Requirements 10.4

### Navigation
- Tab-based or button-based navigation
- Clear labels: "Employee Management" and "Attendance Management"
- Active state indication

**Validates**: Requirements 10.5

### Loading States
- Spinner or skeleton screens during API calls
- Disabled buttons during submission

**Validates**: Requirements 9.1

### Empty States
- "No employees found. Add your first employee to get started."
- "No attendance records found for this employee."

**Validates**: Requirements 9.2, 9.3

### Error States
- Toast notifications or inline error messages
- Clear error text from API responses
- Retry actions where appropriate

**Validates**: Requirements 8.5, 9.4

## Correctness Properties

### Property 1: Employee ID Uniqueness
**Statement**: For all employee creation attempts, if an employee_id already exists in the database, the system must reject the creation with HTTP 409.

**Validates**: Requirements 2.1, 2.2

**Test Strategy**: Property-based test generating random employee_ids, attempting duplicate creation

### Property 2: Email Format Validation
**Statement**: For all employee creation attempts, if the email does not match the email regex pattern, the system must reject the creation with HTTP 422.

**Validates**: Requirements 3.1, 3.2

**Test Strategy**: Property-based test generating invalid email formats

### Property 3: Required Field Validation
**Statement**: For all employee creation attempts, if any required field (employee_id, name, email, department) is missing or empty, the system must reject the creation with HTTP 422.

**Validates**: Requirements 4.1-4.5

**Test Strategy**: Property-based test with combinations of missing fields

### Property 4: Attendance Status Validation
**Statement**: For all attendance creation attempts, if the status is not exactly "Present" or "Absent", the system must reject the creation with HTTP 422.

**Validates**: Requirements 5.3, 5.4

**Test Strategy**: Property-based test generating invalid status values

### Property 5: Cascade Delete Integrity
**Statement**: For all employee deletion operations, all associated attendance records must be deleted from the database.

**Validates**: Requirements 1.3

**Test Strategy**: Create employee with attendance records, delete employee, verify attendance records are gone

### Property 6: Attendance Chronological Order
**Statement**: For all attendance retrieval operations, the returned records must be sorted by date in descending order (newest first).

**Validates**: Requirements 6.2

**Test Strategy**: Create multiple attendance records with different dates, verify order

### Property 7: RESTful HTTP Methods
**Statement**: All API endpoints must use the correct HTTP methods (POST for creation, GET for retrieval, DELETE for deletion) and return appropriate status codes.

**Validates**: Requirements 7.1-7.6

**Test Strategy**: Verify each endpoint uses correct method and returns correct status codes

### Property 8: CORS Configuration
**Statement**: The backend must accept requests from the configured frontend origin and reject requests from other origins.

**Validates**: Requirements 13.4

**Test Strategy**: Send requests with different Origin headers, verify CORS behavior

## Documentation Requirements

### README.md Structure

1. **Project Overview**: Brief description of HRMS Lite
2. **Features**: List of key features
3. **Technology Stack**: Frontend and backend technologies
4. **Local Development Setup**:
   - Prerequisites (Node.js, Python, MySQL)
   - Backend setup steps
   - Frontend setup steps
   - Environment variable configuration
5. **Deployment Instructions**:
   - Frontend deployment to Vercel/Netlify
   - Backend deployment to Render/Railway
   - Environment variables for production
6. **API Documentation**: Brief endpoint reference
7. **Live URLs**: Links to deployed frontend and backend

**Validates**: Requirements 14.1-14.5

## Implementation Notes

### Database Choice Rationale
MySQL is chosen for this implementation because:
- Wide availability on free-tier deployment platforms (Render, Railway, PlanetScale)
- Strong ACID compliance for data integrity
- Excellent SQLAlchemy support
- Relational model fits the employee-attendance relationship
- Familiar to most developers

### Minimal Scope Decisions
To achieve 6-8 hour implementation target:
- No authentication/authorization (single admin user assumption)
- No employee update/edit functionality (only create and delete)
- No attendance update/delete functionality (only create and view)
- No pagination (acceptable for small organizations)
- No advanced filtering or search
- No data export functionality
- Basic CSS styling (no component library like Material-UI)

### Future Enhancements (Out of Scope)
- User authentication and role-based access
- Employee profile editing
- Attendance editing and deletion
- Date range filtering for attendance
- Attendance reports and analytics
- Department management
- Bulk employee import
- Email notifications
- Mobile app

## Success Criteria

The implementation is complete when:
1. All 14 requirements are satisfied
2. Frontend and backend run locally without errors
3. All CRUD operations work end-to-end
4. Validation errors display correctly
5. Application is deployed and accessible via public URLs
6. README documentation is complete and accurate
7. Code is clean, commented, and follows best practices
