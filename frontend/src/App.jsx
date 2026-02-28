import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import EmployeeForm from './components/EmployeeForm';
import EmployeeList from './components/EmployeeList';
import AttendanceForm from './components/AttendanceForm';
import AttendanceView from './components/AttendanceView';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [employeeRefresh, setEmployeeRefresh] = useState(0);
  const [attendanceRefresh, setAttendanceRefresh] = useState(0);
  const [dashboardRefresh, setDashboardRefresh] = useState(0);

  const handleEmployeeSuccess = () => {
    setEmployeeRefresh(prev => prev + 1);
    setDashboardRefresh(prev => prev + 1);
  };

  const handleAttendanceSuccess = () => {
    setAttendanceRefresh(prev => prev + 1);
    setDashboardRefresh(prev => prev + 1);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Welcome to Neha !! HRMS Lite</h1>
        <p className="subtitle">Human Resource Management System</p>
      </header>

      <nav className="app-nav">
        <button
          className={`nav-button ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button
          className={`nav-button ${activeTab === 'employees' ? 'active' : ''}`}
          onClick={() => setActiveTab('employees')}
        >
          Employee Management
        </button>
        <button
          className={`nav-button ${activeTab === 'attendance' ? 'active' : ''}`}
          onClick={() => setActiveTab('attendance')}
        >
          Attendance Management
        </button>
      </nav>

      <main className="app-content">
        <div className="tab-content" key={activeTab}>
          {activeTab === 'dashboard' ? (
            <Dashboard refreshTrigger={dashboardRefresh} />
          ) : activeTab === 'employees' ? (
            <div className="management-section">
              <EmployeeForm onSuccess={handleEmployeeSuccess} />
              <EmployeeList refreshTrigger={employeeRefresh} />
            </div>
          ) : (
            <div className="management-section">
              <AttendanceForm onSuccess={handleAttendanceSuccess} />
              <AttendanceView refreshTrigger={attendanceRefresh} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
