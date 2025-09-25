import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import DebugViewer from '../components/Debug/DebugViewer';
import styles from './ApiDataPage.module.css';

const ApiDataPage = () => {
  const { ioc } = useParams();
  const [debugData, setDebugData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchDebugData = async (iocValue) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/debug_ioc?ioc=${encodeURIComponent(iocValue)}&force_refresh=true`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setDebugData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (ioc) {
      fetchDebugData(ioc);
    }
  }, [ioc]);

  const handleIocSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const iocValue = formData.get('ioc');
    if (iocValue) {
      fetchDebugData(iocValue);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>API Response Data Viewer</h1>
        <p className={styles.description}>
          View complete API responses from all threat intelligence providers
        </p>
      </div>

      <div className={styles.searchSection}>
        <form onSubmit={handleIocSubmit} className={styles.searchForm}>
          <div className={styles.inputGroup}>
            <input
              type="text"
              name="ioc"
              placeholder="Enter IP, domain, URL, or hash..."
              className={styles.input}
              defaultValue={ioc || ''}
              required
            />
            <button type="submit" className={styles.submitButton} disabled={loading}>
              {loading ? 'Loading...' : 'Analyze'}
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div className={styles.error}>
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      )}

      {debugData && (
        <div className={styles.results}>
          <div className={styles.summary}>
            <h2>Analysis Summary</h2>
            <div className={styles.summaryGrid}>
              <div className={styles.summaryItem}>
                <span className={styles.summaryLabel}>IOC:</span>
                <span className={styles.summaryValue}>{debugData.debug_info?.ioc}</span>
              </div>
              <div className={styles.summaryItem}>
                <span className={styles.summaryLabel}>Type:</span>
                <span className={styles.summaryValue}>{debugData.debug_info?.ioc_type}</span>
              </div>
              <div className={styles.summaryItem}>
                <span className={styles.summaryLabel}>Lookup ID:</span>
                <span className={styles.summaryValue}>{debugData.debug_info?.lookup_id}</span>
              </div>
              <div className={styles.summaryItem}>
                <span className={styles.summaryLabel}>Total Time:</span>
                <span className={styles.summaryValue}>{debugData.timing?.total_ms}ms</span>
              </div>
            </div>
          </div>

          <div className={styles.providers}>
            <h2>Provider Responses</h2>
            {debugData.providers?.map((provider, index) => (
              <div key={index} className={styles.providerSection}>
                <h3 className={styles.providerTitle}>
                  {provider.provider?.toUpperCase() || 'Unknown Provider'}
                </h3>
                <div className={styles.providerStatus}>
                  <span className={`${styles.statusDot} ${styles[provider.status]}`}></span>
                  <span className={styles.statusText}>{provider.status}</span>
                  {provider.latency_ms && (
                    <span className={styles.latency}>{provider.latency_ms}ms</span>
                  )}
                </div>
                
                <DebugViewer 
                  data={provider} 
                  title={`${provider.provider} - Complete Response`}
                />
              </div>
            ))}
          </div>

          <div className={styles.rawData}>
            <h2>Complete API Response</h2>
            <DebugViewer 
              data={debugData} 
              title="Full API Response Structure"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiDataPage;
