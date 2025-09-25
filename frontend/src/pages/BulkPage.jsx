import React, { useState, useEffect } from 'react';
import { submitBulkJob, getBulkJobProgress } from '../lib/api';
import styles from './BulkPage.module.css';

const BulkPage = () => {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState('');
  const [forceRefresh, setForceRefresh] = useState(false);

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

    setIsLoading(true);
    setError('');
    
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);
      formData.append('force_refresh', forceRefresh.toString());
      
      // Submit bulk job
      const response = await submitBulkJob(formData);
      setJobId(response.job_id);
      setProgress({
        total: response.total_iocs,
        processed: 0,
        completed: 0,
        failed: 0,
        status: response.status,
      });
    } catch (err) {
      console.error('Error submitting bulk job:', err);
      setError(err.response?.data?.detail || 'Failed to submit bulk job');
    } finally {
      setIsLoading(false);
    }
  };

  // Poll for job progress updates
  useEffect(() => {
    if (jobId && progress && !progress.is_finished) {
      const interval = setInterval(async () => {
        try {
          const jobProgress = await getBulkJobProgress(jobId);
          setProgress({
            total: jobProgress.total_iocs,
            processed: jobProgress.processed_iocs,
            completed: jobProgress.completed_iocs,
            failed: jobProgress.failed_iocs,
            status: jobProgress.status,
            progress_percentage: jobProgress.progress_percentage,
            download_url: jobProgress.download_url,
          });
        } catch (err) {
          console.error('Error fetching job progress:', err);
        }
      }, 2000); // Poll every 2 seconds
      
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
              {progress?.progress_percentage && (
                <span> ({progress.progress_percentage}%)</span>
              )}
            </div>
            <div className={styles.progressBar}>
              <div
                className={styles.progressFill}
                style={{ width: `${progress?.progress_percentage || 0}%` }}
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
              <button 
                className={styles.downloadButton}
                onClick={() => {
                  if (progress.download_url) {
                    window.open(`/api${progress.download_url}`, '_blank');
                  }
                }}
              >
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

