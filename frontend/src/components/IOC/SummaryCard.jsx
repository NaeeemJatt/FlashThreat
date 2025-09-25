import React from 'react';
import styles from './SummaryCard.module.css';

const SummaryCard = ({ summary, ioc, timing }) => {
  if (!summary) {
    return (
      <div className={styles.card}>
        <div className={styles.placeholder}>
          Enter an IOC to see the summary
        </div>
      </div>
    );
  }

  // Get verdict class
  const getVerdictClass = () => {
    switch (summary.verdict) {
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

  return (
    <div className={`${styles.card} ${getVerdictClass()}`}>
      <div className={styles.header}>
        <h2 className={styles.title}>Summary</h2>
        {timing && (
          <div className={styles.timing}>
            {timing.total_ms}ms
          </div>
        )}
      </div>

      <div className={styles.content}>
        <div className={styles.iocInfo}>
          <div className={styles.iocValue}>{ioc.value}</div>
          <div className={styles.iocType}>{ioc.type}</div>
        </div>

        <div className={styles.verdict}>
          <div className={styles.verdictBadge}>
            {summary.verdict.toUpperCase()}
          </div>
          <div className={styles.score}>
            Score: {summary.score}/100
          </div>
        </div>

        <div className={styles.explanation}>
          {summary.explanation}
        </div>

        {(summary.first_seen || summary.last_seen) && (
          <div className={styles.timestamps}>
            {summary.first_seen && (
              <div className={styles.timestamp}>
                <span className={styles.timestampLabel}>First seen:</span>
                <span className={styles.timestampValue}>
                  {new Date(summary.first_seen).toLocaleString()}
                </span>
              </div>
            )}
            {summary.last_seen && (
              <div className={styles.timestamp}>
                <span className={styles.timestampLabel}>Last seen:</span>
                <span className={styles.timestampValue}>
                  {new Date(summary.last_seen).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SummaryCard;

