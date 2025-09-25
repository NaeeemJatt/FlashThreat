import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { useAuth } from '../../lib/auth';
import styles from './Layout.module.css';

const Layout = () => {
  const { user, logout } = useAuth();

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <div className={styles.logo}>FlashThreat</div>
        <nav className={styles.nav}>
          <NavLink to="/" className={({ isActive }) => isActive ? styles.activeLink : styles.link}>
            Home
          </NavLink>
          <NavLink to="/bulk" className={({ isActive }) => isActive ? styles.activeLink : styles.link}>
            Bulk
          </NavLink>
          <NavLink to="/history" className={({ isActive }) => isActive ? styles.activeLink : styles.link}>
            History
          </NavLink>
          <NavLink to="/api-data" className={({ isActive }) => isActive ? styles.activeLink : styles.link}>
            API Data
          </NavLink>
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
      <footer className={styles.footer}>
        <p>FlashThreat &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
};

export default Layout;

