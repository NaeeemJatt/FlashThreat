import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../lib/auth';

const AdminRoute = ({ children }) => {
  const { user } = useAuth();

  // Check if user is authenticated and has admin role
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role !== 'admin') {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default AdminRoute;

