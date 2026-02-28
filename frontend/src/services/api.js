// API Service Layer for HRMS Lite

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Employee API functions
export const employeeAPI = {
  // Get all employees
  getAll: async () => {
    const response = await fetch(`${API_BASE_URL}/employees`);
    if (!response.ok) {
      throw new Error('Failed to fetch employees');
    }
    return response.json();
  },

  // Create a new employee
  create: async (data) => {
    const response = await fetch(`${API_BASE_URL}/employees`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create employee');
    }
    return response.json();
  },

  // Delete an employee
  delete: async (id) => {
    const response = await fetch(`${API_BASE_URL}/employees/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete employee');
    }
    return response.status === 204;
  },
};

// Attendance API functions
export const attendanceAPI = {
  // Create an attendance record
  create: async (data) => {
    const response = await fetch(`${API_BASE_URL}/attendance`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create attendance record');
    }
    return response.json();
  },

  // Get attendance records for a specific employee
  getByEmployee: async (employeeId) => {
    const response = await fetch(`${API_BASE_URL}/attendance/${employeeId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch attendance records');
    }
    return response.json();
  },
};
