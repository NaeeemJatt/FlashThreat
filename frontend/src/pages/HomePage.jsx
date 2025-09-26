import React from 'react';
import { useNavigate } from 'react-router-dom';
import IOCForm from '../components/IOC/IOCForm';
import styles from './HomePage.module.css';

const HomePage = () => {
  const navigate = useNavigate();

  const handleSubmit = (ioc, forceRefresh) => {
    // Navigate to the check results page with the IOC
    navigate(`/result/${encodeURIComponent(ioc)}`);
  };

  return (
    <div className={styles.container}>
      <h4 className={styles.title}>IOC Lookup</h4>
      <p className={styles.description}>
        Enter an IP address, domain, URL, or file hash to check against multiple threat intelligence sources.
      </p>

      <IOCForm onSubmit={handleSubmit} isLoading={false} />
    </div>
  );
};

export default HomePage;

