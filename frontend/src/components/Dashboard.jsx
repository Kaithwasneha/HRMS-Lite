import { useState, useEffect } from 'react';
import './Dashboard.css';

const Dashboard = ({ refreshTrigger }) => {
  const [stats, setStats] = useState({
    totalEmployees: 0,
    totalAttendance: 0,
    presentToday: 0,
    absentToday: 0,
    departments: []
  });
  const [recentAttendance, setRecentAttendance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, [refreshTrigger]);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      // Use the new optimized endpoint
      const response = await fetch(`${import.meta.env.VITE_API_URL}/dashboard/stats`);
      if (!response.ok) throw new Error('Failed to fetch dashboard data');
      
      const data = await response.json();
      
      setStats({
        totalEmployees: data.total_employees,
        totalAttendance: data.total_attendance,
        presentToday: data.present_today,
        absentToday: data.absent_today,
        departments: data.departments
      });
      
      setRecentAttendance(data.recent_attendance.map(record => ({
        employeeName: record.employee_name,
        date: record.date,
        status: record.status
      })));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard">
        <h2>Dashboard</h2>
        <div className="loading-state">
          <div className="spinner-large"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <h2>Dashboard</h2>
        <div className="error-state">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      
      <div className="stats-grid">
        <div className="stat-card stat-employees">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-value">{stats.totalEmployees}</div>
            <div className="stat-label">Total Employees</div>
          </div>
        </div>

        <div className="stat-card stat-attendance">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-value">{stats.totalAttendance}</div>
            <div className="stat-label">Total Attendance Records</div>
          </div>
        </div>

        <div className="stat-card stat-present">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-value">{stats.presentToday}</div>
            <div className="stat-label">Present Today</div>
          </div>
        </div>

        <div className="stat-card stat-absent">
          <div className="stat-icon">❌</div>
          <div className="stat-content">
            <div className="stat-value">{stats.absentToday}</div>
            <div className="stat-label">Absent Today</div>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="dashboard-section">
          <h3>Department Distribution</h3>
          {stats.departments.length > 0 ? (
            <div className="department-list">
              {stats.departments.map((dept, index) => (
                <div key={index} className="department-item">
                  <div className="department-info">
                    <span className="department-name">{dept.name}</span>
                    <span className="department-count">{dept.count} {dept.count === 1 ? 'employee' : 'employees'}</span>
                  </div>
                  <div className="department-bar">
                    <div 
                      className="department-bar-fill" 
                      style={{ width: `${(dept.count / stats.totalEmployees) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-section">
              <p>No departments found. Add employees to see department distribution.</p>
            </div>
          )}
        </div>

        <div className="dashboard-section">
          <h3>Recent Attendance</h3>
          {recentAttendance.length > 0 ? (
            <div className="recent-attendance-list">
              {recentAttendance.map((record, index) => (
                <div key={index} className="attendance-item">
                  <div className="attendance-employee">{record.employeeName}</div>
                  <div className="attendance-date">{new Date(record.date).toLocaleDateString()}</div>
                  <div className={`attendance-status status-${record.status.toLowerCase()}`}>
                    {record.status}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-section">
              <p>No attendance records found. Mark attendance to see recent activity.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
