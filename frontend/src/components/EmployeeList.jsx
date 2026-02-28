import React, { useState, useEffect } from 'react';
import Table from './common/Table';
import { employeeAPI } from '../services/api';
import './EmployeeList.css';

const EmployeeList = ({ refreshTrigger }) => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchEmployees = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await employeeAPI.getAll();
      setEmployees(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, [refreshTrigger]);

  const handleDelete = async (index) => {
    const employee = employees[index];
    if (!window.confirm(`Are you sure you want to delete ${employee.name}?`)) {
      return;
    }

    try {
      await employeeAPI.delete(employee.employee_id);
      fetchEmployees();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <div className="employee-list">
        <h2>Employee List</h2>
        <div className="loading-state">
          <div className="spinner-large"></div>
          <p>Loading employees...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="employee-list">
        <h2>Employee List</h2>
        <div className="error-state">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (employees.length === 0) {
    return (
      <div className="employee-list">
        <h2>Employee List</h2>
        <div className="empty-state">
          <p>No employees found. Add your first employee to get started.</p>
        </div>
      </div>
    );
  }

  const headers = ['Employee ID', 'Name', 'Email', 'Department'];
  const rows = employees.map(emp => [
    emp.employee_id,
    emp.name,
    emp.email,
    emp.department
  ]);

  return (
    <div className="employee-list">
      <h2>Employee List</h2>
      <Table headers={headers} rows={rows} onDelete={handleDelete} />
    </div>
  );
};

export default EmployeeList;
