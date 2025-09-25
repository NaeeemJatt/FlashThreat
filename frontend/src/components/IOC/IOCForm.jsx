import React, { useState } from 'react';
import styles from './IOCForm.module.css';

const IOCForm = ({ onSubmit, isLoading }) => {
  const [ioc, setIoc] = useState('');
  const [forceRefresh, setForceRefresh] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (ioc.trim()) {
      onSubmit(ioc.trim(), forceRefresh);
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.inputGroup}>
        <input
          type="text"
          value={ioc}
          onChange={(e) => setIoc(e.target.value)}
          placeholder="Enter IP, domain, URL, or hash..."
          className={styles.input}
          disabled={isLoading}
          aria-label="IOC input"
        />
        <button type="submit" className={styles.button} disabled={isLoading || !ioc.trim()}>
          {isLoading ? 'Checking...' : 'Check IOC'}
        </button>
      </div>
      <div className={styles.options}>
        <label className={styles.checkbox}>
          <input
            type="checkbox"
            checked={forceRefresh}
            onChange={(e) => setForceRefresh(e.target.checked)}
            disabled={isLoading}
          />
          Force refresh (bypass cache)
        </label>
      </div>
    </form>
  );
};

export default IOCForm;

