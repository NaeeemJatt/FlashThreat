import React, { useState } from 'react';
import styles from './BulkPage.module.css';

const BulkPage = () => {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      setError('');
    } else {
      setFile(null);
      setError('Please select a valid CSV file');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a CSV file');
      return;
    }

    // TODO: Implement bulk upload functionality
    setIsLoading(true);
    setTimeout(() => {
      setJobId('demo-job-id');
      setProgress({
        total: 100,
        processed: 0,
        completed: 0,
        failed: 0,
        status: 'processing',
      });
      setIsLoading(false);
    }, 1000);
  };

  // Simulate progress updates for demo
  React.useEffect(() => {
    if (jobId && progress && progress.status === 'processing') {
      const interval = setInterval(() => {
        setProgress((prev) => {
          const processed = Math.min(prev.processed + 10, prev.total);
          const completed = Math.min(prev.completed + 8, prev.total);
          const failed = Math.min(prev.failed + 2, prev.total - completed);
          
          const status = processed === prev.total ? 'completed' : 'processing';
          
          return {
            ...prev,
            processed,
            completed,
            failed,
            status,
          };
        });
      }, 1000);
      
      return () => clearInterval(interval);
    }
  }, [jobId, progress]);

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Bulk IOC Lookup</h1>
      <p className={styles.description}>
        Upload a CSV file with one IOC per line to process multiple indicators in batch.
      </p>

      {!jobId ? (
        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.fileUpload}>
            <label className={styles.fileLabel}>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className={styles.fileInput}
                disabled={isLoading}
              />
              <div className={styles.fileDrop}>
                <div className={styles.fileIcon}>📄</div>
                <div className={styles.fileText}>
                  {file ? file.name : 'Drop CSV file here or click to browse'}
                </div>
              </div>
            </label>
          </div>

          {error && <div className={styles.error}>{error}</div>}

          <div className={styles.formActions}>
            <button
              type="submit"
              className={styles.submitButton}
              disabled={!file || isLoading}
            >
              {isLoading ? 'Uploading...' : 'Upload and Process'}
            </button>
          </div>
        </form>
      ) : (
        <div className={styles.jobStatus}>
          <h2 className={styles.jobTitle}>Job Status</h2>
          
          <div className={styles.jobInfo}>
            <div className={styles.jobId}>Job ID: {jobId}</div>
            <div className={styles.jobStatus}>Status: {progress?.status}</div>
          </div>
          
          <div className={styles.progressContainer}>
            <div className={styles.progressLabel}>
              {progress?.processed} / {progress?.total} processed
            </div>
            <div className={styles.progressBar}>
              <div
                className={styles.progressFill}
                style={{ width: `${(progress?.processed / progress?.total) * 100}%` }}
              ></div>
            </div>
          </div>
          
          <div className={styles.stats}>
            <div className={styles.stat}>
              <div className={styles.statValue}>{progress?.completed}</div>
              <div className={styles.statLabel}>Completed</div>
            </div>
            <div className={styles.stat}>
              <div className={styles.statValue}>{progress?.failed}</div>
              <div className={styles.statLabel}>Failed</div>
            </div>
          </div>
          
          {progress?.status === 'completed' && (
            <div className={styles.downloadSection}>
              <p>Your results are ready!</p>
              <button className={styles.downloadButton}>
                Download Results
              </button>
            </div>
          )}
          
          <button
            className={styles.newJobButton}
            onClick={() => {
              setJobId(null);
              setProgress(null);
              setFile(null);
            }}
          >
            Start New Job
          </button>
        </div>
      )}
    </div>
  );
};

export default BulkPage;

