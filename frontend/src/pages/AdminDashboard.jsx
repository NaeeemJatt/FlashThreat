import React, { useState, useEffect } from 'react';
import { useAuth } from '../lib/auth';
import styles from './AdminDashboard.module.css';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showUserModal, setShowUserModal] = useState(false);

  // Mock data for demonstration - in real app, this would come from API
  useEffect(() => {
    const mockUsers = [
      {
        id: '1',
        email: 'admin@example.com',
        role: 'admin',
        created_at: '2024-01-01T00:00:00Z',
        last_login: '2024-01-15T10:30:00Z',
        status: 'active',
        total_lookups: 150,
        last_activity: '2024-01-15T10:30:00Z'
      },
      {
        id: '2',
        email: 'analyst1@example.com',
        role: 'analyst',
        created_at: '2024-01-05T00:00:00Z',
        last_login: '2024-01-15T09:15:00Z',
        status: 'active',
        total_lookups: 75,
        last_activity: '2024-01-15T09:15:00Z'
      },
      {
        id: '3',
        email: 'analyst2@example.com',
        role: 'analyst',
        created_at: '2024-01-10T00:00:00Z',
        last_login: '2024-01-14T16:45:00Z',
        status: 'inactive',
        total_lookups: 25,
        last_activity: '2024-01-14T16:45:00Z'
      }
    ];
    
    setTimeout(() => {
      setUsers(mockUsers);
      setLoading(false);
    }, 1000);
  }, []);

  const handleUserAction = (userId, action) => {
    console.log(`Performing ${action} on user ${userId}`);
    // In real app, this would make API calls
    alert(`${action} action performed on user ${userId}`);
  };

  const handleCreateUser = () => {
    console.log('Creating new user');
    alert('Create user functionality would open here');
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status) => {
    return status === 'active' ? styles.activeBadge : styles.inactiveBadge;
  };

  const getRoleBadge = (role) => {
    return role === 'admin' ? styles.adminBadge : styles.analystBadge;
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.loadingSpinner}></div>
          <p>Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Admin Dashboard</h1>
        <p className={styles.subtitle}>Manage users and system settings</p>
      </div>

      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>👥</div>
          <div className={styles.statContent}>
            <h3>{users.length}</h3>
            <p>Total Users</p>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>✅</div>
          <div className={styles.statContent}>
            <h3>{users.filter(u => u.status === 'active').length}</h3>
            <p>Active Users</p>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>🔍</div>
          <div className={styles.statContent}>
            <h3>{users.reduce((sum, u) => sum + u.total_lookups, 0)}</h3>
            <p>Total Lookups</p>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>👑</div>
          <div className={styles.statContent}>
            <h3>{users.filter(u => u.role === 'admin').length}</h3>
            <p>Administrators</p>
          </div>
        </div>
      </div>

      <div className={styles.actionsBar}>
        <button className={styles.createButton} onClick={handleCreateUser}>
          <span className={styles.buttonIcon}>+</span>
          Create New User
        </button>
        <div className={styles.searchBox}>
          <input 
            type="text" 
            placeholder="Search users..." 
            className={styles.searchInput}
          />
        </div>
      </div>

      <div className={styles.usersTable}>
        <div className={styles.tableHeader}>
          <div className={styles.tableRow}>
            <div className={styles.tableCell}>User</div>
            <div className={styles.tableCell}>Role</div>
            <div className={styles.tableCell}>Status</div>
            <div className={styles.tableCell}>Last Login</div>
            <div className={styles.tableCell}>Lookups</div>
            <div className={styles.tableCell}>Actions</div>
          </div>
        </div>
        <div className={styles.tableBody}>
          {users.map((user) => (
            <div key={user.id} className={styles.tableRow}>
              <div className={styles.tableCell}>
                <div className={styles.userInfo}>
                  <div className={styles.userAvatar}>
                    {user.email.charAt(0).toUpperCase()}
                  </div>
                  <div className={styles.userDetails}>
                    <div className={styles.userEmail}>{user.email}</div>
                    <div className={styles.userId}>ID: {user.id}</div>
                  </div>
                </div>
              </div>
              <div className={styles.tableCell}>
                <span className={`${styles.roleBadge} ${getRoleBadge(user.role)}`}>
                  {user.role.toUpperCase()}
                </span>
              </div>
              <div className={styles.tableCell}>
                <span className={`${styles.statusBadge} ${getStatusBadge(user.status)}`}>
                  {user.status.toUpperCase()}
                </span>
              </div>
              <div className={styles.tableCell}>
                {formatDate(user.last_login)}
              </div>
              <div className={styles.tableCell}>
                {user.total_lookups}
              </div>
              <div className={styles.tableCell}>
                <div className={styles.actionButtons}>
                  <button 
                    className={styles.actionButton}
                    onClick={() => setSelectedUser(user)}
                  >
                    View
                  </button>
                  <button 
                    className={styles.actionButton}
                    onClick={() => handleUserAction(user.id, 'edit')}
                  >
                    Edit
                  </button>
                  <button 
                    className={styles.actionButton}
                    onClick={() => handleUserAction(user.id, 'toggle-status')}
                  >
                    {user.status === 'active' ? 'Deactivate' : 'Activate'}
                  </button>
                  <button 
                    className={styles.actionButton}
                    onClick={() => handleUserAction(user.id, 'delete')}
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedUser && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h3>User Details</h3>
              <button 
                className={styles.closeButton}
                onClick={() => setSelectedUser(null)}
              >
                ×
              </button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.userDetail}>
                <label>Email:</label>
                <span>{selectedUser.email}</span>
              </div>
              <div className={styles.userDetail}>
                <label>Role:</label>
                <span className={`${styles.roleBadge} ${getRoleBadge(selectedUser.role)}`}>
                  {selectedUser.role.toUpperCase()}
                </span>
              </div>
              <div className={styles.userDetail}>
                <label>Status:</label>
                <span className={`${styles.statusBadge} ${getStatusBadge(selectedUser.status)}`}>
                  {selectedUser.status.toUpperCase()}
                </span>
              </div>
              <div className={styles.userDetail}>
                <label>Created:</label>
                <span>{formatDate(selectedUser.created_at)}</span>
              </div>
              <div className={styles.userDetail}>
                <label>Last Login:</label>
                <span>{formatDate(selectedUser.last_login)}</span>
              </div>
              <div className={styles.userDetail}>
                <label>Total Lookups:</label>
                <span>{selectedUser.total_lookups}</span>
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button 
                className={styles.modalButton}
                onClick={() => handleUserAction(selectedUser.id, 'edit')}
              >
                Edit User
              </button>
              <button 
                className={styles.modalButton}
                onClick={() => setSelectedUser(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;

