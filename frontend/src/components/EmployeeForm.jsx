import React, { useState } from 'react';
import Input from './common/Input';
import Button from './common/Button';
import { employeeAPI } from '../services/api';
import './EmployeeForm.css';

const EmployeeForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    employee_id: '',
    name: '',
    email: '',
    department: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  const validateForm = () => {
    const newErrors = {};

    if (!formData.employee_id.trim()) {
      newErrors.employee_id = 'Employee ID is required';
    }
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    if (!formData.department.trim()) {
      newErrors.department = 'Department is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (field) => (e) => {
    setFormData({ ...formData, [field]: e.target.value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
    if (message.text) {
      setMessage({ type: '', text: '' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      await employeeAPI.create(formData);
      setMessage({ type: 'success', text: 'Employee added successfully!' });
      setFormData({
        employee_id: '',
        name: '',
        email: '',
        department: ''
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

  return (
    <div className="employee-form">
      <h2>Add New Employee</h2>
      <form onSubmit={handleSubmit}>
        <Input
          label="Employee ID"
          value={formData.employee_id}
          onChange={handleChange('employee_id')}
          error={errors.employee_id}
          required
          placeholder="e.g., EMP001"
        />
        <Input
          label="Name"
          value={formData.name}
          onChange={handleChange('name')}
          error={errors.name}
          required
          placeholder="e.g., Neha"
        />
        <Input
          label="Email"
          type="email"
          value={formData.email}
          onChange={handleChange('email')}
          error={errors.email}
          required
          placeholder="e.g., neha@example.com"
        />
        <Input
          label="Department"
          value={formData.department}
          onChange={handleChange('department')}
          error={errors.department}
          required
          placeholder="e.g., Engineering"
        />

        {message.text && (
          <div className={`message message-${message.type}`}>
            {message.text}
          </div>
        )}

        <Button type="primary" onClick={handleSubmit} loading={loading}>
          Add Employee
        </Button>
      </form>
    </div>
  );
};

export default EmployeeForm;
