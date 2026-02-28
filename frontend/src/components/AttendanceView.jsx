import React, { useState, useEffect } from 'react';
import Table from './common/Table';
import { employeeAPI, attendanceAPI } from '../services/api';
import './AttendanceView.css';

const AttendanceView = ({ refreshTrigger }) => {
  const [employees, setEmployees] = useState([]);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState('');
  const [selectedEmployeeName, setSelectedEmployeeName] = useState('');
  const [attendance, setAttendance] = useState([]);
  const [filteredAttendance, setFilteredAttendance] = useState([]);
  const [loadingEmployees, setLoadingEmployees] = useState(true);
  const [loadingAttendance, setLoadingAttendance] = useState(false);
  const [error, setError] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    fetchEmployees();
  }, []);

  useEffect(() => {
    if (selectedEmployeeId) {
      fetchAttendance(selectedEmployeeId);
    }
  }, [refreshTrigger]);

  const fetchEmployees = async () => {
    setLoadingEmployees(true);
    setError('');
    try {
      const data = await employeeAPI.getAll();
      setEmployees(data);
      if (data.length > 0) {
        setSelectedEmployeeId(data[0].employee_id);
        setSelectedEmployeeName(data[0].name);
        fetchAttendance(data[0].employee_id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingEmployees(false);
    }
  };

  const fetchAttendance = async (employeeId) => {
    setLoadingAttendance(true);
    setError('');
    try {
      const data = await attendanceAPI.getByEmployee(employeeId);
      setAttendance(data);
      setFilteredAttendance(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingAttendance(false);
    }
  };

  const filterAttendanceByDate = () => {
    if (!startDate && !endDate) {
      setFilteredAttendance(attendance);
      return;
    }

    const filtered = attendance.filter(record => {
      const recordDate = new Date(record.date);
      const start = startDate ? new Date(startDate) : null;
      const end = endDate ? new Date(endDate) : null;

      if (start && end) {
        return recordDate >= start && recordDate <= end;
      } else if (start) {
        return recordDate >= start;
      } else if (end) {
        return recordDate <= end;
      }
      return true;
    });

    setFilteredAttendance(filtered);
  };

  const handleClearFilter = () => {
    setStartDate('');
    setEndDate('');
    setFilteredAttendance(attendance);
  };

  const calculatePresentDays = () => {
    return filteredAttendance.filter(record => record.status === 'Present').length;
  };

  const calculateAbsentDays = () => {
    return filteredAttendance.filter(record => record.status === 'Absent').length;
  };

  const handleEmployeeChange = (e) => {
    const employeeId = e.target.value;
    const employee = employees.find(emp => emp.employee_id === employeeId);
    setSelectedEmployeeId(employeeId);
    setSelectedEmployeeName(employee ? employee.name : '');
    fetchAttendance(employeeId);
  };

  if (loadingEmployees) {
    return (
      <div className="attendance-view">
        <h2>Attendance Records</h2>
        <div className="loading-state">
          <div className="spinner-large"></div>
          <p>Loading employees...</p>
        </div>
      </div>
    );
  }

  if (employees.length === 0) {
    return (
      <div className="attendance-view">
        <h2>Attendance Records</h2>
        <div className="empty-state">
          <p>No employees found. Please add employees first.</p>
        </div>
      </div>
    );
  }

  const headers = ['Employee Name', 'Date', 'Status'];
  const rows = filteredAttendance.map(record => [
    selectedEmployeeName,
    new Date(record.date).toLocaleDateString(),
    record.status
  ]);

  const presentDays = calculatePresentDays();
  const absentDays = calculateAbsentDays();
  const totalDays = filteredAttendance.length;

  return (
    <div className="attendance-view">
      <h2>Attendance Records</h2>
      
      <div className="employee-selector">
        <label htmlFor="employee-select">Select Employee:</label>
        <select
          id="employee-select"
          className="select-field"
          value={selectedEmployeeId}
          onChange={handleEmployeeChange}
        >
          {employees.map(emp => (
            <option key={emp.employee_id} value={emp.employee_id}>
              {emp.name} ({emp.employee_id})
            </option>
          ))}
        </select>
      </div>

      {!loadingAttendance && attendance.length > 0 && (
        <>
          <div className="date-filter">
            <div className="filter-inputs">
              <div className="date-input-group">
                <label htmlFor="start-date">From:</label>
                <input
                  type="date"
                  id="start-date"
                  className="date-input"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              <div className="date-input-group">
                <label htmlFor="end-date">To:</label>
                <input
                  type="date"
                  id="end-date"
                  className="date-input"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>
              <button className="filter-button" onClick={filterAttendanceByDate}>
                Apply Filter
              </button>
              {(startDate || endDate) && (
                <button className="clear-button" onClick={handleClearFilter}>
                  Clear
                </button>
              )}
            </div>
          </div>

          <div className="attendance-summary">
            <div className="summary-card summary-total">
              <div className="summary-value">{totalDays}</div>
              <div className="summary-label">Total Days</div>
            </div>
            <div className="summary-card summary-present">
              <div className="summary-value">{presentDays}</div>
              <div className="summary-label">Present Days</div>
            </div>
            <div className="summary-card summary-absent">
              <div className="summary-value">{absentDays}</div>
              <div className="summary-label">Absent Days</div>
            </div>
            {totalDays > 0 && (
              <div className="summary-card summary-percentage">
                <div className="summary-value">{((presentDays / totalDays) * 100).toFixed(1)}%</div>
                <div className="summary-label">Attendance Rate</div>
              </div>
            )}
          </div>
        </>
      )}

      {loadingAttendance ? (
        <div className="loading-state">
          <div className="spinner-large"></div>
          <p>Loading attendance records...</p>
        </div>
      ) : error ? (
        <div className="error-state">
          <p>{error}</p>
        </div>
      ) : attendance.length === 0 ? (
        <div className="empty-state">
          <p>No attendance records found for this employee.</p>
        </div>
      ) : filteredAttendance.length === 0 ? (
        <div className="empty-state">
          <p>No attendance records found for the selected date range.</p>
        </div>
      ) : (
        <Table headers={headers} rows={rows} />
      )}
    </div>
  );
};

export default AttendanceView;
