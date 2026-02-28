import React, { useState, useEffect } from 'react';
import Button from './common/Button';
import { employeeAPI, attendanceAPI } from '../services/api';
import './AttendanceForm.css';

const AttendanceForm = ({ onSuccess }) => {
  const [employees, setEmployees] = useState([]);
  const [formData, setFormData] = useState({
    employee_id: '',
    date: new Date().toISOString().split('T')[0],
    status: 'Present'
  });
  const [loading, setLoading] = useState(false);
  const [loadingEmployees, setLoadingEmployees] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    setLoadingEmployees(true);
    try {
      const data = await employeeAPI.getAll();
      setEmployees(data);
      if (data.length > 0) {
        setFormData(prev => ({ ...prev, employee_id: data[0].employee_id }));
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load employees' });
    } finally {
      setLoadingEmployees(false);
    }
  };

  const handleChange = (field) => (e) => {
    setFormData({ ...formData, [field]: e.target.value });
    if (message.text) {
      setMessage({ type: '', text: '' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.employee_id) {
      setMessage({ type: 'error', text: 'Please select an employee' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      await attendanceAPI.create(formData);
      setMessage({ type: 'success', text: 'Attendance recorded successfully!' });
      setFormData({
        ...formData,
        date: new Date().toISOString().split('T')[0],
        status: 'Present'
      });
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setLoading(false);
    }
  };

  if (loadingEmployees) {
    return (
      <div className="attendance-form">
        <h2>Mark Attendance</h2>
        <div className="loading-state">
          <div className="spinner-large"></div>
          <p>Loading employees...</p>
        </div>
      </div>
    );
  }

  if (employees.length === 0) {
    return (
      <div className="attendance-form">
        <h2>Mark Attendance</h2>
        <div className="empty-state">
          <p>No employees found. Please add employees first.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="attendance-form">
      <h2>Mark Attendance</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="employee">
            Employee <span className="required">*</span>
          </label>
          <select
            id="employee"
            className="select-field"
            value={formData.employee_id}
            onChange={handleChange('employee_id')}
          >
            {employees.map(emp => (
              <option key={emp.employee_id} value={emp.employee_id}>
                {emp.name} ({emp.employee_id})
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="date">
            Date <span className="required">*</span>
          </label>
          <input
            id="date"
            type="date"
            className="input-field"
            value={formData.date}
            onChange={handleChange('date')}
          />
        </div>

        <div className="form-group">
          <label>
            Status <span className="required">*</span>
          </label>
          <div className="radio-group">
            <label className="radio-label">
              <input
                type="radio"
                name="status"
                value="Present"
                checked={formData.status === 'Present'}
                onChange={handleChange('status')}
              />
              <span>Present</span>
            </label>
            <label className="radio-label">
              <input
                type="radio"
                name="status"
                value="Absent"
                checked={formData.status === 'Absent'}
                onChange={handleChange('status')}
              />
              <span>Absent</span>
            </label>
          </div>
        </div>

        {message.text && (
          <div className={`message message-${message.type}`}>
            {message.text}
          </div>
        )}

        <Button type="primary" onClick={handleSubmit} loading={loading}>
          Mark Attendance
        </Button>
      </form>
    </div>
  );
};

export default AttendanceForm;
