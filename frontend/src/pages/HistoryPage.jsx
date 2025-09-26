import React, { useState, useEffect } from 'react';
import { useAuth } from '../lib/auth';
import { getLookupHistory } from '../lib/api';
import styles from './HistoryPage.module.css';

const HistoryPage = () => {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 50,
    offset: 0,
    has_more: false
  });
  const [currentPage, setCurrentPage] = useState(1);

  // Fetch history data
  const fetchHistory = async (page = 1) => {
    try {
      setLoading(true);
      setError(null);
      
      const offset = (page - 1) * pagination.limit;
      const response = await getLookupHistory(pagination.limit, offset);
      
      setHistory(response.lookups);
      setPagination(response.pagination);
      setCurrentPage(page);
    } catch (err) {
      console.error('Failed to fetch history:', err);
      setError('Failed to load history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Load history on component mount
  useEffect(() => {
    fetchHistory();
  }, []);

  // Handle page change
  const handlePageChange = (newPage) => {
    fetchHistory(newPage);
  };

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
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const handleViewDetails = (lookupId) => {
    // Navigate to lookup details page
    window.location.href = `/check-id/${lookupId}`;
  };

  const totalPages = Math.ceil(pagination.total / pagination.limit);

  if (loading) {
    return (
      <div className={styles.container}>
        <h1 className={styles.title}>Lookup History</h1>
        <div className={styles.loading}>
          <p>Loading history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <h1 className={styles.title}>Lookup History</h1>
        <div className={styles.error}>
          <p>{error}</p>
          <button onClick={() => fetchHistory(currentPage)} className={styles.retryButton}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Lookup History</h1>
      <p className={styles.description}>
        View your recent IOC lookups and their results.
        {user?.role === 'admin' && ' (Admin view - all users)'}
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
              {user?.role === 'admin' && <th>User</th>}
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item) => (
              <tr key={item.id}>
                <td>{formatDate(item.started_at || item.created_at)}</td>
                <td className={styles.iocValue}>{item.ioc?.value || 'N/A'}</td>
                <td>{item.ioc?.type || 'N/A'}</td>
                <td>
                  <span className={`${styles.verdict} ${getVerdictClass(item.verdict)}`}>
                    {item.verdict || 'unknown'}
                  </span>
                </td>
                <td>{item.score || 0}</td>
                {user?.role === 'admin' && (
                  <td>{item.user?.email || 'N/A'}</td>
                )}
                <td>
                  <button 
                    className={styles.viewButton}
                    onClick={() => handleViewDetails(item.id)}
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {history.length === 0 && !loading && (
        <div className={styles.empty}>
          <p>No lookup history found.</p>
        </div>
      )}

      {/* Pagination */}
      {pagination.total > 0 && (
        <div className={styles.pagination}>
          <div className={styles.paginationInfo}>
            Showing {pagination.offset + 1} to {Math.min(pagination.offset + pagination.limit, pagination.total)} of {pagination.total} results
          </div>
          <div className={styles.paginationControls}>
            <button 
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage <= 1}
              className={styles.paginationButton}
            >
              Previous
            </button>
            <span className={styles.pageInfo}>
              Page {currentPage} of {totalPages}
            </span>
            <button 
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className={styles.paginationButton}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoryPage;

