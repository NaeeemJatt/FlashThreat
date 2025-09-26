import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import SummaryCard from '../components/IOC/SummaryCard';
import ProviderCard from '../components/IOC/ProviderCard';
import { streamIOC } from '../lib/api';
import styles from './CheckResultPage.module.css';

const CheckResultPage = () => {
  const { ioc } = useParams();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [providerResults, setProviderResults] = useState({
    virustotal: null,
    abuseipdb: null,
    otx: null,
  });
  const [closeStream, setCloseStream] = useState(null);
  const [error, setError] = useState(null);

  // Clean up stream on unmount
  useEffect(() => {
    return () => {
      if (closeStream) {
        closeStream();
      }
    };
  }, [closeStream]);

  // Load results when component mounts or ioc changes
  useEffect(() => {
    if (ioc) {
      handleIocCheck(ioc, false);
    }
  }, [ioc]);

  const handleIocCheck = (iocValue, forceRefresh) => {
    setIsLoading(true);
    setResult(null);
    setError(null);
    setProviderResults({
      virustotal: null,
      abuseipdb: null,
      otx: null,
    });

    // Close existing stream if any
    if (closeStream) {
      closeStream();
    }

    // Start streaming
    const close = streamIOC(
      iocValue,
      forceRefresh,
      {
        onProvider: (data) => {
          const { provider } = data.provider;
          setProviderResults((prev) => ({
            ...prev,
            [provider]: data.provider,
          }));
        },
        onDone: (data) => {
          setResult(data);
          setIsLoading(false);
        },
        onError: (error) => {
          console.error('Stream error:', error);
          setError(error.message || 'An error occurred during analysis');
          setIsLoading(false);
        },
      }
    );

    setCloseStream(() => close);
  };

  const handleBackToHome = () => {
    navigate('/');
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button onClick={handleBackToHome} className={styles.backButton}>
          ← Back to Home
        </button>
        <h1 className={styles.title}>IOC Analysis Results</h1>
        <div className={styles.iocDisplay}>
          <span className={styles.iocLabel}>Analyzing:</span>
          <span className={styles.iocValue}>{ioc}</span>
        </div>
      </div>


      {error && (
        <div className={styles.error}>
          <h3>Analysis Error</h3>
          <p>{error}</p>
          <button onClick={() => handleIocCheck(ioc, true)} className={styles.retryButton}>
            Retry Analysis
          </button>
        </div>
      )}

      {isLoading && (
        <div className={styles.loading}>
          <div className={styles.loadingSpinner}></div>
          <p>Analyzing {ioc} against threat intelligence sources...</p>
        </div>
      )}

      {(result || isLoading) && (
        <>
          <SummaryCard 
            summary={result?.summary} 
            ioc={result?.ioc} 
            timing={result?.timing} 
          />

          <div className={styles.providerGrid}>
            <ProviderCard provider="virustotal" data={providerResults.virustotal} />
            <ProviderCard provider="abuseipdb" data={providerResults.abuseipdb} />
            <ProviderCard provider="otx" data={providerResults.otx} />
          </div>
        </>
      )}

      {result && (
        <div className={styles.actions}>
          <button 
            onClick={() => handleIocCheck(ioc, true)} 
            className={styles.refreshButton}
            disabled={isLoading}
          >
            {isLoading ? 'Refreshing...' : 'Refresh Analysis'}
          </button>
        </div>
      )}
    </div>
  );
};

export default CheckResultPage;
