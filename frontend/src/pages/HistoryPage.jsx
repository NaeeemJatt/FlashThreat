import React, { useState } from 'react';
import styles from './HistoryPage.module.css';

const HistoryPage = () => {
  // Mock data for demonstration
  const [history] = useState([
    {
      id: '1',
      ioc: {
        value: '8.8.8.8',
        type: 'ipv4',
      },
      summary: {
        verdict: 'clean',
        score: 10,
      },
      timing: {
        started_at: '2023-09-22T10:15:30Z',
      },
      user: {
        email: 'admin@example.com',
      },
    },
    {
      id: '2',
      ioc: {
        value: 'malicious-domain.com',
        type: 'domain',
      },
      summary: {
        verdict: 'malicious',
        score: 85,
      },
      timing: {
        started_at: '2023-09-22T09:45:12Z',
      },
      user: {
        email: 'admin@example.com',
      },
    },
    {
      id: '3',
      ioc: {
        value: 'https://suspicious-url.com/path',
        type: 'url',
      },
      summary: {
        verdict: 'suspicious',
        score: 65,
      },
      timing: {
        started_at: '2023-09-21T16:30:45Z',
      },
      user: {
        email: 'analyst@example.com',
      },
    },
    {
      id: '4',
      ioc: {
        value: '44d88612fea8a8f36de82e1278abb02f',
        type: 'hash_md5',
      },
      summary: {
        verdict: 'unknown',
        score: 30,
      },
      timing: {
        started_at: '2023-09-21T14:20:10Z',
      },
      user: {
        email: 'admin@example.com',
      },
    },
  ]);

  const getVerdictClass = (verdict) => {
    switch (verdict) {
      case 'malicious':
        return styles.malicious;
      case 'suspicious':
        return styles.suspicious;
      case 'unknown':
        return styles.unknown;
      case 'clean':
        return styles.clean;
      default:
        return '';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Lookup History</h1>
      <p className={styles.description}>
        View your recent IOC lookups and their results.
      </p>

      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Time</th>
              <th>IOC</th>
              <th>Type</th>
              <th>Verdict</th>
              <th>Score</th>
              <th>User</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item) => (
              <tr key={item.id}>
                <td>{formatDate(item.timing.started_at)}</td>
                <td className={styles.iocValue}>{item.ioc.value}</td>
                <td>{item.ioc.type}</td>
                <td>
                  <span className={`${styles.verdict} ${getVerdictClass(item.summary.verdict)}`}>
                    {item.summary.verdict}
                  </span>
                </td>
                <td>{item.summary.score}</td>
                <td>{item.user.email}</td>
                <td>
                  <button className={styles.viewButton}>View</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {history.length === 0 && (
        <div className={styles.empty}>
          <p>No lookup history found.</p>
        </div>
      )}
    </div>
  );
};

export default HistoryPage;

