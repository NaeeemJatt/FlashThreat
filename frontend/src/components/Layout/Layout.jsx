import React from 'react';
import { Outlet, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../lib/auth';
import styles from './Layout.module.css';

const Layout = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  
  // Check if we're on a result page
  const isResultPage = location.pathname.startsWith('/result/');
  
  const handleBackToHome = () => {
    navigate('/');
  };

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <div className={styles.logo}>FlashThreat</div>
        <nav className={styles.nav}>
          {isResultPage ? (
            <button onClick={handleBackToHome} className={styles.backButton}>
              ← Back to Home
            </button>
          ) : (
            <>
              <NavLink to="/" className={({ isActive }) => isActive ? styles.activeLink : styles.link}>
                Home
              </NavLink>
              <NavLink to="/bulk" className={({ isActive }) => isActive ? styles.activeLink : styles.link}>
                Bulk
              </NavLink>
              <NavLink to="/history" className={({ isActive }) => isActive ? styles.activeLink : styles.link}>
                History
              </NavLink>
            </>
          )}
        </nav>
        <div className={styles.user}>
          {user && (
            <>
              <span className={styles.email}>{user.email}</span>
              <span className={styles.role}>{user.role}</span>
              <button className={styles.logoutButton} onClick={logout}>
                Logout
              </button>
            </>
          )}
        </div>
      </header>
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;

