import React from 'react';
import { useAuth } from '../lib/auth';
import { useNavigate } from 'react-router-dom';
import styles from './ProfilePage.module.css';

const ProfilePage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const getRoleDisplayName = (role) => {
    switch (role) {
      case 'admin':
        return 'Administrator';
      case 'analyst':
        return 'Security Analyst';
      default:
        return role;
    }
  };

  const getRoleDescription = (role) => {
    switch (role) {
      case 'admin':
        return 'Full system access with user management capabilities';
      case 'analyst':
        return 'Threat intelligence analysis and IOC checking capabilities';
      default:
        return 'Standard user access';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>User Profile</h1>
        <p className={styles.subtitle}>Manage your account information and preferences</p>
      </div>

      <div className={styles.profileCard}>
        <div className={styles.profileHeader}>
          <div className={styles.avatar}>
            <div className={styles.avatarIcon}>
              {user?.email?.charAt(0).toUpperCase()}
            </div>
          </div>
          <div className={styles.profileInfo}>
            <h2 className={styles.userName}>{user?.email}</h2>
            <div className={styles.roleBadge}>
              <span className={styles.roleLabel}>Role:</span>
              <span className={`${styles.roleValue} ${styles[user?.role]}`}>
                {getRoleDisplayName(user?.role)}
              </span>
            </div>
          </div>
        </div>

        <div className={styles.profileContent}>
          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>Account Information</h3>
            <div className={styles.formGroup}>
              <label className={styles.label}>Email Address</label>
              <div className={styles.value}>{user?.email}</div>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>User Role</label>
              <div className={styles.value}>
                <span className={`${styles.roleDisplay} ${styles[user?.role]}`}>
                  {getRoleDisplayName(user?.role)}
                </span>
                <p className={styles.roleDescription}>
                  {getRoleDescription(user?.role)}
                </p>
              </div>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Account Created</label>
              <div className={styles.value}>
                {formatDate(user?.created_at)}
              </div>
            </div>
          </div>

          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>Role Permissions</h3>
            <div className={styles.permissions}>
              {user?.role === 'admin' && (
                <div className={styles.permissionItem}>
                  <div className={styles.permissionIcon}>👑</div>
                  <div className={styles.permissionContent}>
                    <h4>Administrator Access</h4>
                    <p>Full system access, user management, and system configuration</p>
                  </div>
                </div>
              )}
              
              <div className={styles.permissionItem}>
                <div className={styles.permissionIcon}>🔍</div>
                <div className={styles.permissionContent}>
                  <h4>IOC Analysis</h4>
                  <p>Check IOCs against multiple threat intelligence sources</p>
                </div>
              </div>

              <div className={styles.permissionItem}>
                <div className={styles.permissionIcon}>📊</div>
                <div className={styles.permissionContent}>
                  <h4>Bulk Analysis</h4>
                  <p>Upload and analyze multiple IOCs simultaneously</p>
                </div>
              </div>

              <div className={styles.permissionItem}>
                <div className={styles.permissionIcon}>📈</div>
                <div className={styles.permissionContent}>
                  <h4>History Access</h4>
                  <p>View and manage analysis history and results</p>
                </div>
              </div>

              {user?.role === 'admin' && (
                <div className={styles.permissionItem}>
                  <div className={styles.permissionIcon}>⚙️</div>
                  <div className={styles.permissionContent}>
                    <h4>System Management</h4>
                    <p>Access system metrics, performance monitoring, and configuration</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {user?.role === 'admin' && (
            <div className={styles.section}>
              <h3 className={styles.sectionTitle}>Admin Actions</h3>
              <div className={styles.adminActions}>
                <button 
                  className={styles.adminButton}
                  onClick={() => navigate('/admin')}
                >
                  <div className={styles.adminButtonIcon}>👥</div>
                  <div className={styles.adminButtonContent}>
                    <h4>User Management</h4>
                    <p>Manage users, roles, and permissions</p>
                  </div>
                </button>
                <button 
                  className={styles.adminButton}
                  onClick={() => navigate('/system')}
                >
                  <div className={styles.adminButtonIcon}>⚙️</div>
                  <div className={styles.adminButtonContent}>
                    <h4>System Settings</h4>
                    <p>Configure system parameters and settings</p>
                  </div>
                </button>
                <button 
                  className={styles.adminButton}
                  onClick={() => navigate('/analytics')}
                >
                  <div className={styles.adminButtonIcon}>📊</div>
                  <div className={styles.adminButtonContent}>
                    <h4>Analytics & Reports</h4>
                    <p>View system analytics and generate reports</p>
                  </div>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
