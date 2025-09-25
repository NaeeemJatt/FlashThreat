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

        {/* Enhanced Analysis Details */}
        <div className={styles.analysisDetails}>
          <h4 className={styles.analysisTitle}>Analysis Breakdown</h4>
          
          <div className={styles.analysisGrid}>
            {/* Risk Assessment */}
            <div className={styles.analysisSection}>
              <div className={styles.sectionHeader}>
                <span className={styles.sectionIcon}>⚠️</span>
                <span className={styles.sectionLabel}>Risk Assessment</span>
              </div>
              <div className={styles.sectionContent}>
                <div className={styles.riskItem}>
                  <span className={styles.riskLabel}>Threat Level:</span>
                  <span className={`${styles.riskValue} ${styles[summary.verdict]}`}>
                    {summary.verdict.toUpperCase()}
                  </span>
                </div>
                <div className={styles.riskItem}>
                  <span className={styles.riskLabel}>Confidence:</span>
                  <span className={styles.riskValue}>
                    {summary.confidence || 'N/A'}%
                  </span>
                </div>
                <div className={styles.riskItem}>
                  <span className={styles.riskLabel}>Reliability:</span>
                  <span className={styles.riskValue}>
                    {summary.reliability || 'N/A'}%
                  </span>
                </div>
              </div>
            </div>

            {/* Detection Sources */}
            <div className={styles.analysisSection}>
              <div className={styles.sectionHeader}>
                <span className={styles.sectionIcon}>🔍</span>
                <span className={styles.sectionLabel}>Detection Sources</span>
              </div>
              <div className={styles.sectionContent}>
                <div className={styles.sourceItem}>
                  <span className={styles.sourceLabel}>Total Scans:</span>
                  <span className={styles.sourceValue}>
                    {summary.total_scans || 'N/A'}
                  </span>
                </div>
                <div className={styles.sourceItem}>
                  <span className={styles.sourceLabel}>Malicious Detections:</span>
                  <span className={styles.sourceValue}>
                    {summary.malicious_detections || 'N/A'}
                  </span>
                </div>
                <div className={styles.sourceItem}>
                  <span className={styles.sourceLabel}>Clean Detections:</span>
                  <span className={styles.sourceValue}>
                    {summary.clean_detections || 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            {/* Geographic Information */}
            {summary.geolocation && (
              <div className={styles.analysisSection}>
                <div className={styles.sectionHeader}>
                  <span className={styles.sectionIcon}>🌍</span>
                  <span className={styles.sectionLabel}>Geographic Info</span>
                </div>
                <div className={styles.sectionContent}>
                  {summary.geolocation.country && (
                    <div className={styles.geoItem}>
                      <span className={styles.geoLabel}>Country:</span>
                      <span className={styles.geoValue}>
                        {summary.geolocation.country}
                      </span>
                    </div>
                  )}
                  {summary.geolocation.region && (
                    <div className={styles.geoItem}>
                      <span className={styles.geoLabel}>Region:</span>
                      <span className={styles.geoValue}>
                        {summary.geolocation.region}
                      </span>
                    </div>
                  )}
                  {summary.geolocation.isp && (
                    <div className={styles.geoItem}>
                      <span className={styles.geoLabel}>ISP:</span>
                      <span className={styles.geoValue}>
                        {summary.geolocation.isp}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Network Information */}
            {summary.network && (
              <div className={styles.analysisSection}>
                <div className={styles.sectionHeader}>
                  <span className={styles.sectionIcon}>🌐</span>
                  <span className={styles.sectionLabel}>Network Info</span>
                </div>
                <div className={styles.sectionContent}>
                  {summary.network.organization && (
                    <div className={styles.networkItem}>
                      <span className={styles.networkLabel}>Organization:</span>
                      <span className={styles.networkValue}>
                        {summary.network.organization}
                      </span>
                    </div>
                  )}
                  {summary.network.asn && (
                    <div className={styles.networkItem}>
                      <span className={styles.networkLabel}>ASN:</span>
                      <span className={styles.networkValue}>
                        {summary.network.asn}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
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

