import React, { useState, useEffect } from 'react';
import IOCForm from '../components/IOC/IOCForm';
import SummaryCard from '../components/IOC/SummaryCard';
import ProviderCard from '../components/IOC/ProviderCard';
import { streamIOC } from '../lib/api';
import styles from './HomePage.module.css';

const HomePage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [providerResults, setProviderResults] = useState({
    virustotal: null,
    abuseipdb: null,
    otx: null,
  });
  const [closeStream, setCloseStream] = useState(null);

  // Clean up stream on unmount
  useEffect(() => {
    return () => {
      if (closeStream) {
        closeStream();
      }
    };
  }, [closeStream]);

  const handleSubmit = (ioc, forceRefresh) => {
    setIsLoading(true);
    setResult(null);
    setProviderResults({
      virustotal: null,
      abuseipdb: null,
      shodan: null,
      otx: null,
    });

    // Close existing stream if any
    if (closeStream) {
      closeStream();
    }

    // Start streaming
    const close = streamIOC(
      ioc,
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
          setIsLoading(false);
        },
      }
    );

    setCloseStream(() => close);
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>IOC Lookup</h1>
      <p className={styles.description}>
        Enter an IP address, domain, URL, or file hash to check against multiple threat intelligence sources.
      </p>

      <IOCForm onSubmit={handleSubmit} isLoading={isLoading} />

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
    </div>
  );
};

export default HomePage;

