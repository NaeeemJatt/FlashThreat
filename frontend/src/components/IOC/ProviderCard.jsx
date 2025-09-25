import React, { useState } from 'react';
import styles from './ProviderCard.module.css';

const ProviderCard = ({ provider, data }) => {
  const [showEvidence, setShowEvidence] = useState(false);

  // Handle different provider statuses
  const getStatusClass = () => {
    if (!data) return styles.loading;
    
    switch (data.status) {
      case 'ok':
        return styles.ok;
      case 'not_found':
        return styles.notFound;
      case 'auth_error':
        return styles.authError;
      case 'rate_limited':
        return styles.rateLimit;
      case 'timeout':
        return styles.timeout;
      default:
        return styles.error;
    }
  };

  // Get status text
  const getStatusText = () => {
    if (!data) return 'Loading...';
    
    switch (data.status) {
      case 'ok':
        return 'OK';
      case 'not_found':
        return 'Not Found';
      case 'auth_error':
        return 'Auth Error';
      case 'rate_limited':
        return 'Rate Limited';
      case 'timeout':
        return 'Timeout';
      default:
        return 'Error';
    }
  };

  // Get provider name display
  const getProviderName = () => {
    switch (provider) {
      case 'virustotal':
        return 'VirusTotal';
      case 'abuseipdb':
        return 'AbuseIPDB';
      case 'shodan':
        return 'Shodan';
      case 'otx':
        return 'AlienVault OTX';
      default:
        return provider;
    }
  };

  return (
    <div className={`${styles.card} ${getStatusClass()}`}>
      <div className={styles.header}>
        <h3 className={styles.title}>{getProviderName()}</h3>
        <div className={styles.status}>
          <span className={styles.statusDot}></span>
          <span className={styles.statusText}>{getStatusText()}</span>
          {data?.cached && (
            <span className={styles.cached}>
              Cached ({data.cache_age_seconds}s)
            </span>
          )}
        </div>
      </div>

      {data ? (
        <div className={styles.content}>
          {data.status === 'ok' ? (
            <>
              <div className={styles.metrics}>
                {data.reputation !== null && (
                  <div className={styles.metric}>
                    <div className={styles.metricValue}>{data.reputation}</div>
                    <div className={styles.metricLabel}>Reputation</div>
                  </div>
                )}
                {data.confidence !== null && (
                  <div className={styles.metric}>
                    <div className={styles.metricValue}>{data.confidence}</div>
                    <div className={styles.metricLabel}>Confidence</div>
                  </div>
                )}
                {data.malicious_count !== null && (
                  <div className={styles.metric}>
                    <div className={styles.metricValue}>{data.malicious_count}</div>
                    <div className={styles.metricLabel}>Malicious</div>
                  </div>
                )}
              </div>

              {data.evidence && data.evidence.length > 0 && (
                <div className={styles.evidence}>
                  <button 
                    className={styles.evidenceToggle}
                    onClick={() => setShowEvidence(!showEvidence)}
                  >
                    {showEvidence ? 'Hide Evidence' : 'Show Evidence'}
                  </button>
                  
                  {showEvidence && (
                    <ul className={styles.evidenceList}>
                      {data.evidence.map((item, index) => (
                        <li key={index} className={`${styles.evidenceItem} ${styles[item.severity || 'info']}`}>
                          <div className={styles.evidenceHeader}>
                            <strong>{item.title}</strong>
                            <span className={styles.evidenceCategory}>{item.category}</span>
                          </div>
                          <p className={styles.evidenceDescription}>{item.description}</p>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              {data.link && (
                <div className={styles.footer}>
                  <a 
                    href={data.link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className={styles.link}
                  >
                    View on {getProviderName()}
                  </a>
                </div>
              )}
            </>
          ) : (
            <div className={styles.error}>
              {data.error && data.error.message}
            </div>
          )}
        </div>
      ) : (
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading data from {getProviderName()}...</p>
        </div>
      )}
    </div>
  );
};

export default ProviderCard;

