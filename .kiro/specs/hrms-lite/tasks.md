# Implementation Plan: HRMS Lite

## Overview

This plan implements a full-stack HRMS Lite application with a React frontend and FastAPI backend. The implementation follows a bottom-up approach: backend first (database, models, API), then frontend (components, API integration), and finally deployment configuration. Each task builds incrementally toward a production-ready application targeting 6-8 hours of development time.

## Tasks

- [x] 1. Set up backend project structure and database
  - Create backend directory with main.py, models.py, schemas.py, database.py, crud.py
  - Create requirements.txt with FastAPI, SQLAlchemy, pymysql, pydantic[email], uvicorn
  - Set up database connection with SQLAlchemy engine and session management
  - Create Employee and Attendance SQLAlchemy models with proper constraints
  - Implement database initialization function
  - _Requirements: 12.1, 12.2, 12.3, 12.4_

- [x] 1.1 Write property test for database models
  - **Property 5: Cascade Delete Integrity**
  - **Validates: Requirements 1.3**

- [x] 2. Implement Pydantic schemas and validation
  - Create EmployeeCreate schema with email validation regex
  - Create EmployeeResponse schema
  - Create AttendanceCreate schema with status enum validation
  - Create AttendanceResponse schema
  - Implement required field validation for all schemas
  - _Requirements: 3.1, 4.1, 4.2, 4.3, 4.4, 4.5, 5.3_

- [x] 2.1 Write property test for email validation
  - **Property 2: Email Format Validation**
  - **Validates: Requirements 3.1, 3.2**

- [x] 2.2 Write property test for required field validation
  - **Property 3: Required Field Validation**
  - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

- [x] 2.3 Write property test for attendance status validation
  - **Property 4: Attendance Status Validation**
  - **Validates: Requirements 5.3, 5.4**

- [x] 3. Implement CRUD operations
  - [x] 3.1 Implement create_employee with uniqueness check
    - Check if employee_id exists before insertion
    - Raise exception for duplicate employee_id
    - _Requirements: 1.1, 2.1_
  
  - [x] 3.2 Implement get_all_employees query
    - Return all employees from database
    - _Requirements: 1.2_
  
  - [x] 3.3 Implement delete_employee with cascade
    - Delete employee and all associated attendance records
    - _Requirements: 1.3_
  
  - [x] 3.4 Implement create_attendance
    - Verify employee exists before creating attendance
    - Insert attendance record
    - _Requirements: 5.1_
  
  - [x] 3.5 Implement get_attendance_by_employee
    - Query attendance records for specific employee
    - Sort by date descending
    - _Requirements: 6.1, 6.2_

- [x] 3.6 Write property test for employee ID uniqueness
  - **Property 1: Employee ID Uniqueness**
  - **Validates: Requirements 2.1, 2.2**

- [x] 3.7 Write property test for attendance chronological order
  - **Property 6: Attendance Chronological Order**
  - **Validates: Requirements 6.2**

- [x] 4. Implement FastAPI endpoints and error handling
  - [x] 4.1 Initialize FastAPI app with CORS middleware
    - Configure CORS for localhost:5173 and environment variable FRONTEND_URL
    - _Requirements: 13.4_
  
  - [x] 4.2 Implement POST /employees endpoint
    - Accept EmployeeCreate schema
    - Return 201 on success, 409 for duplicate, 422 for validation errors
    - _Requirements: 1.1, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 4.5, 7.1, 8.1, 8.2_
  
  - [x] 4.3 Implement GET /employees endpoint
    - Return all employees with 200 status
    - _Requirements: 1.2, 7.2_
  
  - [x] 4.4 Implement DELETE /employees/{employee_id} endpoint
    - Return 204 on success, 404 if not found
    - _Requirements: 1.3, 7.3, 8.3_
  
  - [x] 4.5 Implement POST /attendance endpoint
    - Accept AttendanceCreate schema
    - Return 201 on success, 404 if employee not found, 422 for validation errors
    - _Requirements: 5.1, 5.3, 5.4, 7.4, 8.1_
  
  - [x] 4.6 Implement GET /attendance/{employee_id} endpoint
    - Return attendance records with 200 status, 404 if employee not found
    - _Requirements: 6.1, 7.5, 8.3_
  
  - [x] 4.7 Add global exception handler for 500 errors
    - Catch unhandled exceptions and return 500 with error message
    - _Requirements: 8.4_

- [x] 4.8 Write property test for RESTful HTTP methods
  - **Property 7: RESTful HTTP Methods**
  - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6**

- [x] 4.9 Write property test for CORS configuration
  - **Property 8: CORS Configuration**
  - **Validates: Requirements 13.4**

- [x] 5. Checkpoint - Backend complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Set up frontend project structure
  - Create React project with Vite
  - Create directory structure: components/, components/common/, services/, styles/
  - Create placeholder files: App.jsx, api.js, App.css
  - Install dependencies (no additional libraries needed beyond React)
  - Configure VITE_API_URL environment variable
  - _Requirements: 13.1, 13.3_

- [x] 7. Implement reusable UI components
  - [x] 7.1 Create Button component
    - Props: onClick, children, type, disabled, loading
    - Consistent styling with primary/secondary variants
    - _Requirements: 11.3_
  
  - [x] 7.2 Create Input component
    - Props: label, value, onChange, type, error, required
    - Display validation error messages
    - _Requirements: 11.2_
  
  - [x] 7.3 Create Table component
    - Props: headers, rows, onDelete
    - Render data in table format with action buttons
    - _Requirements: 11.4_

- [x] 8. Implement API service layer
  - Create api.js with API_BASE_URL from environment variable
  - Implement employeeAPI.getAll() - GET /employees
  - Implement employeeAPI.create(data) - POST /employees
  - Implement employeeAPI.delete(id) - DELETE /employees/{id}
  - Implement attendanceAPI.create(data) - POST /attendance
  - Implement attendanceAPI.getByEmployee(employeeId) - GET /attendance/{employeeId}
  - Add error handling for network failures
  - _Requirements: 11.1_

- [x] 9. Implement employee management components
  - [x] 9.1 Create EmployeeForm component
    - Form fields: employee_id, name, email, department (all required)
    - Client-side email validation with regex
    - Prevent submission when fields empty
    - Call employeeAPI.create() on submit
    - Display success/error messages
    - Clear form on success
    - _Requirements: 1.5, 3.3, 3.4, 4.6_
  
  - [x] 9.2 Create EmployeeList component
    - Fetch employees on mount using employeeAPI.getAll()
    - Display loading spinner during fetch
    - Display empty state when no employees
    - Render employees in Table component
    - Implement delete functionality with confirmation
    - Display error state on API failure
    - _Requirements: 1.4, 9.1, 9.2, 9.4_

- [x] 9.3 Write unit tests for EmployeeForm validation
  - Test email validation logic
  - Test required field validation
  - _Requirements: 3.3, 3.4, 4.6_

- [x] 10. Implement attendance management components
  - [x] 10.1 Create AttendanceForm component
    - Employee selection dropdown (fetch from employeeAPI.getAll())
    - Date input (default to today)
    - Status radio buttons (Present/Absent)
    - Call attendanceAPI.create() on submit
    - Display success/error messages
    - _Requirements: 5.2_
  
  - [x] 10.2 Create AttendanceView component
    - Employee selection dropdown
    - Fetch attendance on employee selection using attendanceAPI.getByEmployee()
    - Display loading spinner during fetch
    - Display empty state when no attendance records
    - Render attendance in table format (employee name, date, status)
    - Display records in chronological order (newest first)
    - _Requirements: 6.2, 6.3, 9.3_

- [x] 10.3 Write unit tests for AttendanceForm
  - Test form submission with valid data
  - Test error handling
  - _Requirements: 5.2_

- [x] 11. Implement App component and navigation
  - Create navigation between Employee Management and Attendance Management
  - Implement tab-based or button-based navigation with active state
  - Render EmployeeForm and EmployeeList in Employee Management view
  - Render AttendanceForm and AttendanceView in Attendance Management view
  - Add global error boundary
  - _Requirements: 10.5_

- [x] 12. Implement styling and responsive design
  - Create App.css with color scheme (blue/gray palette)
  - Define CSS variables for colors: primary (#2563eb), secondary (#64748b), success (#10b981), error (#ef4444)
  - Implement consistent spacing (8px base unit)
  - Use system font stack for typography
  - Style all components with consistent spacing and typography
  - Ensure responsive layout for desktop (1024px+) and mobile (320px+)
  - Style loading states, empty states, and error states
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 13. Checkpoint - Frontend complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 14. Create deployment configuration files
  - [x] 14.1 Create backend deployment configuration
    - Add Procfile or railway.json with start command
    - Document DATABASE_URL and FRONTEND_URL environment variables
    - _Requirements: 13.2_
  
  - [x] 14.2 Create frontend deployment configuration
    - Create vercel.json or netlify.toml if needed
    - Document VITE_API_URL environment variable
    - _Requirements: 13.1, 13.3_

- [x] 15. Create comprehensive README documentation
  - Write project overview and features list
  - Document technology stack (React, FastAPI, MySQL)
  - Write local development setup instructions for backend (Python, pip, database setup)
  - Write local development setup instructions for frontend (Node.js, npm)
  - Document all environment variables (DATABASE_URL, FRONTEND_URL, VITE_API_URL)
  - Write deployment instructions for Vercel/Netlify (frontend)
  - Write deployment instructions for Render/Railway (backend)
  - Add API endpoint reference
  - Add placeholders for live frontend URL and backend API URL
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 16. Final checkpoint - Application complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Backend implementation (tasks 1-5) should be completed before frontend work begins
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific component behavior and edge cases
- The implementation targets 6-8 hours of focused development time
- Database choice is PostgreSQL for better deployment platform support
- No authentication is implemented (single admin user assumption)
- No update/edit functionality for employees or attendance (create and delete only)
