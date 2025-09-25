import React, { useState } from 'react';
import styles from './DebugViewer.module.css';

const DebugViewer = ({ data, title = "API Response Data" }) => {
  const [expandedSections, setExpandedSections] = useState({});
  const [showRawData, setShowRawData] = useState(false);

  const toggleSection = (sectionKey) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionKey]: !prev[sectionKey]
    }));
  };

  const formatValue = (value) => {
    if (value === null || value === undefined) {
      return <span className={styles.nullValue}>null</span>;
    }
    if (typeof value === 'object') {
      return <pre className={styles.jsonValue}>{JSON.stringify(value, null, 2)}</pre>;
    }
    if (typeof value === 'boolean') {
      return <span className={styles.booleanValue}>{value.toString()}</span>;
    }
    if (typeof value === 'number') {
      return <span className={styles.numberValue}>{value}</span>;
    }
    return <span className={styles.stringValue}>"{value}"</span>;
  };

  const renderObject = (obj, path = '', level = 0) => {
    if (level > 5) return <span className={styles.maxDepth}>[Max depth reached]</span>;
    
    if (obj === null || obj === undefined) {
      return <span className={styles.nullValue}>null</span>;
    }
    
    if (typeof obj !== 'object') {
      return formatValue(obj);
    }
    
    if (Array.isArray(obj)) {
      return (
        <div className={styles.arrayContainer}>
          <span className={styles.arrayBracket}>[</span>
          {obj.map((item, index) => (
            <div key={index} className={styles.arrayItem}>
              <span className={styles.arrayIndex}>{index}:</span>
              {renderObject(item, `${path}[${index}]`, level + 1)}
            </div>
          ))}
          <span className={styles.arrayBracket}>]</span>
        </div>
      );
    }
    
    const keys = Object.keys(obj);
    if (keys.length === 0) {
      return <span className={styles.emptyObject}>{'{}'}</span>;
    }
    
    return (
      <div className={styles.objectContainer}>
        <span className={styles.objectBrace}>{'{'}</span>
        {keys.map((key, index) => {
          const isExpanded = expandedSections[`${path}.${key}`];
          const hasChildren = typeof obj[key] === 'object' && obj[key] !== null;
          
          return (
            <div key={key} className={styles.objectItem}>
              <div 
                className={styles.objectKey}
                onClick={hasChildren ? () => toggleSection(`${path}.${key}`) : undefined}
              >
                <span className={styles.keyName}>"{key}"</span>
                <span className={styles.keySeparator}>:</span>
                {hasChildren && (
                  <span className={styles.expandButton}>
                    {isExpanded ? '▼' : '▶'}
                  </span>
                )}
              </div>
              {hasChildren && isExpanded && (
                <div className={styles.objectValue}>
                  {renderObject(obj[key], `${path}.${key}`, level + 1)}
                </div>
              )}
              {!hasChildren && (
                <div className={styles.objectValue}>
                  {formatValue(obj[key])}
                </div>
              )}
            </div>
          );
        })}
        <span className={styles.objectBrace}>{'}'}</span>
      </div>
    );
  };

  return (
    <div className={styles.debugViewer}>
      <div className={styles.header}>
        <h3 className={styles.title}>{title}</h3>
        <div className={styles.controls}>
          <label className={styles.toggle}>
            <input
              type="checkbox"
              checked={showRawData}
              onChange={(e) => setShowRawData(e.target.checked)}
            />
            Show Raw API Data
          </label>
        </div>
      </div>
      
      <div className={styles.content}>
        {data && (
          <div className={styles.dataContainer}>
            {showRawData && data.raw_api_response && (
              <div className={styles.rawDataSection}>
                <h4 className={styles.sectionTitle}>Raw API Response</h4>
                <div className={styles.rawDataContent}>
                  {renderObject(data.raw_api_response)}
                </div>
              </div>
            )}
            
            <div className={styles.normalizedDataSection}>
              <h4 className={styles.sectionTitle}>Normalized Data</h4>
              <div className={styles.normalizedDataContent}>
                {renderObject(data)}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DebugViewer;
