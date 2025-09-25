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
                {data.total_scans !== null && (
                  <div className={styles.metric}>
                    <div className={styles.metricValue}>{data.total_scans}</div>
                    <div className={styles.metricLabel}>Total Scans</div>
                  </div>
                )}
                {data.detection_ratio !== null && (
                  <div className={styles.metric}>
                    <div className={styles.metricValue}>{data.detection_ratio}%</div>
                    <div className={styles.metricLabel}>Detection Ratio</div>
                  </div>
                )}
              </div>

              {/* Enhanced IP Details Section */}
              <div className={styles.ipDetails}>
                <h4 className={styles.detailsTitle}>IP Analysis Details</h4>
                
                {/* Geolocation Information */}
                {data.geolocation && (
                  <div className={styles.detailSection}>
                    <div className={styles.detailHeader}>
                      <span className={styles.detailIcon}>🌍</span>
                      <span className={styles.detailLabel}>Geolocation</span>
                    </div>
                    <div className={styles.detailContent}>
                      {data.geolocation.country && (
                        <div className={styles.detailItem}>
                          <span className={styles.detailKey}>Country:</span>
                          <span className={styles.detailValue}>{data.geolocation.country}</span>
                        </div>
                      )}
                      {data.geolocation.region && (
                        <div className={styles.detailItem}>
                          <span className={styles.detailKey}>Region:</span>
                          <span className={styles.detailValue}>{data.geolocation.region}</span>
                        </div>
                      )}
                      {data.geolocation.city && (
                        <div className={styles.detailItem}>
                          <span className={styles.detailKey}>City:</span>
                          <span className={styles.detailValue}>{data.geolocation.city}</span>
                        </div>
                      )}
                      {data.geolocation.isp && (
                        <div className={styles.detailItem}>
                          <span className={styles.detailKey}>ISP:</span>
                          <span className={styles.detailValue}>{data.geolocation.isp}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Network Information */}
                {data.network && (
                  <div className={styles.detailSection}>
                    <div className={styles.detailHeader}>
                      <span className={styles.detailIcon}>🌐</span>
                      <span className={styles.detailLabel}>Network Information</span>
                    </div>
                    <div className={styles.detailContent}>
                      {data.network.organization && (
                        <div className={styles.detailItem}>
                          <span className={styles.detailKey}>Organization:</span>
                          <span className={styles.detailValue}>{data.network.organization}</span>
                        </div>
                      )}
                      {data.network.asn && (
                        <div className={styles.detailItem}>
                          <span className={styles.detailKey}>ASN:</span>
                          <span className={styles.detailValue}>{data.network.asn}</span>
                        </div>
                      )}
                      {data.network.owner && (
                        <div className={styles.detailItem}>
                          <span className={styles.detailKey}>Owner:</span>
                          <span className={styles.detailValue}>{data.network.owner}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Security Information */}
                {data.security && (
                  <div className={styles.detailSection}>
                    <div className={styles.detailHeader}>
                      <span className={styles.detailIcon}>🔒</span>
                      <span className={styles.detailLabel}>Security Analysis</span>
                    </div>
                    <div className={styles.detailContent}>
                      {data.security.ports && data.security.ports.length > 0 && (
                        <div className={styles.detailItem}>
                          <span className={styles.detailKey}>Open Ports:</span>
                          <span className={styles.detailValue}>
                            {data.security.ports.map(port => `${port.port} (${port.service})`).join(', ')}
                          </span>
                        </div>
                      )}
                      {data.security.vulnerabilities && data.security.vulnerabilities.length > 0 && (
                        <div className={styles.detailItem}>
                          <span className={styles.detailKey}>Vulnerabilities:</span>
                          <span className={styles.detailValue}>
                            {data.security.vulnerabilities.length} found
                          </span>
                        </div>
                      )}
                      {data.security.ssl_info && (
                        <div className={styles.detailItem}>
                          <span className={styles.detailKey}>SSL Certificate:</span>
                          <span className={styles.detailValue}>
                            {data.security.ssl_info.valid ? 'Valid' : 'Invalid'}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Threat Intelligence */}
                {data.threat_intel && (
                  <div className={styles.detailSection}>
                    <div className={styles.detailHeader}>
                      <span className={styles.detailIcon}>⚠️</span>
                      <span className={styles.detailLabel}>Threat Intelligence</span>
                    </div>
                    <div className={styles.detailContent}>
                      {data.threat_intel.categories && data.threat_intel.categories.length > 0 && (
                        <div className={styles.detailItem}>
                          <span className={styles.detailKey}>Categories:</span>
                          <span className={styles.detailValue}>
                            {data.threat_intel.categories.join(', ')}
                          </span>
                        </div>
                      )}
                      {data.threat_intel.last_seen && (
                        <div className={styles.detailItem}>
                          <span className={styles.detailKey}>Last Seen:</span>
                          <span className={styles.detailValue}>{data.threat_intel.last_seen}</span>
                        </div>
                      )}
                      {data.threat_intel.attack_types && data.threat_intel.attack_types.length > 0 && (
                        <div className={styles.detailItem}>
                          <span className={styles.detailKey}>Attack Types:</span>
                          <span className={styles.detailValue}>
                            {data.threat_intel.attack_types.join(', ')}
                          </span>
                        </div>
                      )}
                    </div>
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

