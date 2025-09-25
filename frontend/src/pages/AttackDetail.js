import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function AttackDetail() {
  const { index } = useParams();
  const navigate = useNavigate();
  const [attack, setAttack] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [attackIocs, setAttackIocs] = useState([]);
  const [loadingAttackIocs, setLoadingAttackIocs] = useState(false);
  const [attackIocsError, setAttackIocsError] = useState(null);

  useEffect(() => {
    fetchAttackData();
  }, [index]);

  const fetchAttackData = () => {
    setLoading(true);
    setError(null);
    
    axios.get(`${API_URL}/cyber-attacks/september`)
      .then(response => {
        const attacks = response.data.attacks;
        const attackIndex = parseInt(index);
        
        if (attackIndex >= 0 && attackIndex < attacks.length) {
          setAttack(attacks[attackIndex]);
        } else {
          setError("Attack not found");
        }
      })
      .catch(error => {
        console.error("Error fetching attack data:", error);
        setError("Failed to load attack data");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const fetchAttackIocs = () => {
    if (!attack) return;
    
    setLoadingAttackIocs(true);
    setAttackIocsError(null);
    
    // Use the actual attack index from the URL parameter
    const attackIndex = parseInt(index);
    
    axios.post(`${API_URL}/cyber-attacks/${attackIndex}/iocs`, attack)
      .then(response => {
        console.log("IOC Response:", response.data);
        setAttackIocs(response.data.iocs);
      })
      .catch(error => {
        console.error("Error fetching attack IOCs:", error);
        setAttackIocsError("Failed to fetch IOCs for this attack.");
      })
      .finally(() => {
        setLoadingAttackIocs(false);
      });
  };

  const getConfidenceColor = (confidence) => {
    switch (confidence?.toLowerCase()) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getRiskLevelColor = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'critical': return '#dc2626';
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      case 'very low': return '#6b7280';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div style={{
        backgroundColor: '#111827',
        minHeight: '100vh',
        color: '#e5e7eb',
        padding: '20px',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ color: '#22d3ee', marginBottom: '16px' }}>Loading Attack Details...</h2>
          <p style={{ color: '#9ca3af' }}>Please wait while we fetch the attack information.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        backgroundColor: '#111827',
        minHeight: '100vh',
        color: '#e5e7eb',
        padding: '20px',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ color: '#ef4444', marginBottom: '16px' }}>Error</h2>
          <p style={{ color: '#9ca3af', marginBottom: '20px' }}>{error}</p>
          <button
            onClick={() => navigate('/')}
            style={{
              backgroundColor: '#22d3ee',
              color: '#111827',
              fontWeight: 'bold',
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!attack) {
    return (
      <div style={{
        backgroundColor: '#111827',
        minHeight: '100vh',
        color: '#e5e7eb',
        padding: '20px',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ color: '#ef4444', marginBottom: '16px' }}>Attack Not Found</h2>
          <p style={{ color: '#9ca3af', marginBottom: '20px' }}>The requested attack could not be found.</p>
          <button
            onClick={() => navigate('/')}
            style={{
              backgroundColor: '#22d3ee',
              color: '#111827',
              fontWeight: 'bold',
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: '#111827',
      minHeight: '100vh',
      color: '#e5e7eb',
      padding: '20px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '32px',
          paddingBottom: '16px',
          borderBottom: '2px solid #374151'
        }}>
          <h1 style={{
            fontSize: '32px',
            fontWeight: 'bold',
            color: '#22d3ee',
            margin: 0
          }}>Attack Details 🔍</h1>
          <button
            onClick={() => navigate('/')}
            style={{
              backgroundColor: '#374151',
              color: '#e5e7eb',
              fontWeight: 'bold',
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontSize: '16px',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              e.target.style.backgroundColor = '#4b5563';
            }}
            onMouseOut={(e) => {
              e.target.style.backgroundColor = '#374151';
            }}
          >
            ← Back to Dashboard
          </button>
        </div>

        {/* Attack Information */}
        <div style={{
          backgroundColor: '#1f2937',
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '24px',
          boxShadow: '0 10px 25px rgba(0, 0, 0, 0.3)'
        }}>
          <h2 style={{
            color: '#22d3ee',
            marginBottom: '20px',
            fontSize: '24px',
            borderBottom: '1px solid #374151',
            paddingBottom: '8px'
          }}>Attack Information</h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '20px'
          }}>
            {attack.attacker && (
              <div style={{
                backgroundColor: '#374151',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid #4b5563'
              }}>
                <strong style={{ color: '#22d3ee', fontSize: '14px', display: 'block', marginBottom: '8px' }}>ATTACKER</strong>
                <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.5' }}>{attack.attacker}</p>
              </div>
            )}
            
            {attack.victim && (
              <div style={{
                backgroundColor: '#374151',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid #4b5563'
              }}>
                <strong style={{ color: '#22d3ee', fontSize: '14px', display: 'block', marginBottom: '8px' }}>VICTIM</strong>
                <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.5' }}>{attack.victim}</p>
              </div>
            )}
            
            {attack.vulnerability && (
              <div style={{
                backgroundColor: '#374151',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid #4b5563'
              }}>
                <strong style={{ color: '#22d3ee', fontSize: '14px', display: 'block', marginBottom: '8px' }}>VULNERABILITY EXPLOITED</strong>
                <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.5' }}>{attack.vulnerability}</p>
              </div>
            )}
            
            {attack.attack_type && (
              <div style={{
                backgroundColor: '#374151',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid #4b5563'
              }}>
                <strong style={{ color: '#22d3ee', fontSize: '14px', display: 'block', marginBottom: '8px' }}>ATTACK TYPE</strong>
                <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.5' }}>{attack.attack_type}</p>
              </div>
            )}
            
            {attack.date && (
              <div style={{
                backgroundColor: '#374151',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid #4b5563'
              }}>
                <strong style={{ color: '#22d3ee', fontSize: '14px', display: 'block', marginBottom: '8px' }}>DATE</strong>
                <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.5' }}>{attack.date}</p>
              </div>
            )}
          </div>
          
          {attack.impact && (
            <div style={{
              backgroundColor: '#374151',
              padding: '16px',
              borderRadius: '8px',
              border: '1px solid #4b5563',
              marginTop: '20px'
            }}>
              <strong style={{ color: '#22d3ee', fontSize: '14px', display: 'block', marginBottom: '8px' }}>IMPACT</strong>
              <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.6' }}>{attack.impact}</p>
            </div>
          )}
        </div>

        {/* IOCs Section */}
        <div style={{
          backgroundColor: '#1f2937',
          borderRadius: '12px',
          padding: '24px',
          boxShadow: '0 10px 25px rgba(0, 0, 0, 0.3)'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px',
            borderBottom: '1px solid #374151',
            paddingBottom: '8px'
          }}>
            <h2 style={{
              color: '#22d3ee',
              margin: 0,
              fontSize: '24px'
            }}>Related IOCs</h2>
            <button
              onClick={fetchAttackIocs}
              disabled={loadingAttackIocs}
              style={{
                backgroundColor: loadingAttackIocs ? '#6b7280' : '#dc2626',
                color: 'white',
                fontWeight: 'bold',
                padding: '10px 20px',
                borderRadius: '8px',
                border: 'none',
                cursor: loadingAttackIocs ? 'not-allowed' : 'pointer',
                fontSize: '16px',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => {
                if (!loadingAttackIocs) {
                  e.target.style.backgroundColor = '#b91c1c';
                }
              }}
              onMouseOut={(e) => {
                if (!loadingAttackIocs) {
                  e.target.style.backgroundColor = '#dc2626';
                }
              }}
            >
              {loadingAttackIocs ? 'Analyzing...' : 'Analyze IOCs'}
            </button>
          </div>

          {loadingAttackIocs && (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <p style={{ color: '#9ca3af', fontSize: '18px' }}>Analyzing IOCs with threat intelligence...</p>
            </div>
          )}

          {attackIocsError && (
            <div style={{
              backgroundColor: 'rgba(127, 29, 29, 0.3)',
              border: '1px solid #dc2626',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '20px'
            }}>
              <p style={{ color: '#ef4444', margin: 0, fontSize: '16px' }}>{attackIocsError}</p>
            </div>
          )}

          {attackIocs.length > 0 && (
            <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
              {attackIocs.map((ioc, iocIndex) => (
                <div key={iocIndex} style={{
                  backgroundColor: '#374151',
                  padding: '16px',
                  marginBottom: '12px',
                  borderRadius: '8px',
                  border: '1px solid #4b5563'
                }}>
                  {ioc.error ? (
                    <p style={{ color: '#ef4444', margin: 0 }}>{ioc.error}</p>
                  ) : ioc.raw_response ? (
                    <div>
                      <strong style={{ color: '#22d3ee', fontSize: '14px', display: 'block', marginBottom: '8px' }}>RAW RESPONSE:</strong>
                      <pre style={{
                        backgroundColor: '#1f2937',
                        padding: '12px',
                        borderRadius: '6px',
                        overflow: 'auto',
                        fontSize: '12px',
                        color: '#e5e7eb',
                        margin: 0,
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word'
                      }}>{ioc.raw_response}</pre>
                    </div>
                  ) : (
                    <div>
                      <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                        gap: '16px',
                        marginBottom: '12px'
                      }}>
                        {ioc.indicator_value && (
                          <div>
                            <strong style={{ color: '#22d3ee', fontSize: '12px', display: 'block', marginBottom: '4px' }}>INDICATOR:</strong>
                            <p style={{
                              margin: 0,
                              fontFamily: 'monospace',
                              color: '#67e8f9',
                              fontSize: '14px',
                              wordBreak: 'break-all',
                              backgroundColor: '#1f2937',
                              padding: '8px',
                              borderRadius: '4px'
                            }}>{ioc.indicator_value}</p>
                          </div>
                        )}
                        {ioc.indicator_type && (
                          <div>
                            <strong style={{ color: '#22d3ee', fontSize: '12px', display: 'block', marginBottom: '4px' }}>TYPE:</strong>
                            <p style={{ margin: 0, fontSize: '14px' }}>{ioc.indicator_type}</p>
                          </div>
                        )}
                        {ioc.confidence && (
                          <div>
                            <strong style={{ color: '#22d3ee', fontSize: '12px', display: 'block', marginBottom: '4px' }}>CONFIDENCE:</strong>
                            <span style={{
                              margin: 0,
                              fontSize: '14px',
                              color: getConfidenceColor(ioc.confidence),
                              fontWeight: 'bold',
                              backgroundColor: 'rgba(0, 0, 0, 0.3)',
                              padding: '4px 8px',
                              borderRadius: '4px'
                            }}>{ioc.confidence}</span>
                          </div>
                        )}
                        {ioc.enrichment && ioc.enrichment.risk_level && (
                          <div>
                            <strong style={{ color: '#22d3ee', fontSize: '12px', display: 'block', marginBottom: '4px' }}>RISK LEVEL:</strong>
                            <span style={{
                              margin: 0,
                              fontSize: '14px',
                              color: getRiskLevelColor(ioc.enrichment.risk_level),
                              fontWeight: 'bold',
                              backgroundColor: 'rgba(0, 0, 0, 0.3)',
                              padding: '4px 8px',
                              borderRadius: '4px'
                            }}>{ioc.enrichment.risk_level} ({ioc.enrichment.risk_score}/100)</span>
                          </div>
                        )}
                        {ioc.note && (
                          <div>
                            <strong style={{ color: '#fbbf24', fontSize: '12px', display: 'block', marginBottom: '4px' }}>NOTE:</strong>
                            <span style={{
                              margin: 0,
                              fontSize: '12px',
                              color: '#fbbf24',
                              backgroundColor: 'rgba(251, 191, 36, 0.1)',
                              padding: '4px 8px',
                              borderRadius: '4px',
                              border: '1px solid #fbbf24'
                            }}>{ioc.note}</span>
                          </div>
                        )}
                        {ioc.source && (ioc.source === 'AlienVault OTX' || ioc.source === 'MISP') && (
                          <div>
                            <strong style={{ color: '#10b981', fontSize: '12px', display: 'block', marginBottom: '4px' }}>SOURCE:</strong>
                            <span style={{
                              margin: 0,
                              fontSize: '12px',
                              color: '#10b981',
                              backgroundColor: 'rgba(16, 185, 129, 0.1)',
                              padding: '4px 8px',
                              borderRadius: '4px',
                              border: '1px solid #10b981'
                            }}>🛡️ Real Threat Intelligence ({ioc.source})</span>
                          </div>
                        )}
                      </div>
                      {ioc.description && (
                        <div>
                          <strong style={{ color: '#22d3ee', fontSize: '12px', display: 'block', marginBottom: '4px' }}>DESCRIPTION:</strong>
                          <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.5' }}>{ioc.description}</p>
                        </div>
                      )}
                      
                      {/* Enrichment Data */}
                      {ioc.enrichment && !ioc.enrichment.error && (
                        <div style={{ marginTop: '12px' }}>
                          <strong style={{ color: '#22d3ee', fontSize: '12px', display: 'block', marginBottom: '8px' }}>THREAT INTELLIGENCE:</strong>
                          
                          {/* Summary */}
                          {ioc.enrichment.summary && (
                            <div style={{ marginBottom: '12px' }}>
                              <strong style={{ color: '#fbbf24', fontSize: '11px' }}>SUMMARY:</strong>
                              <div style={{ marginTop: '4px' }}>
                                {ioc.enrichment.summary.key_findings && ioc.enrichment.summary.key_findings.length > 0 && (
                                  <div style={{ marginBottom: '4px' }}>
                                    <strong style={{ color: '#fbbf24', fontSize: '10px' }}>Key Findings:</strong>
                                    <ul style={{ margin: '2px 0', paddingLeft: '16px', fontSize: '12px' }}>
                                      {ioc.enrichment.summary.key_findings.map((finding, idx) => (
                                        <li key={idx} style={{ color: '#e5e7eb' }}>{finding}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                                {ioc.enrichment.summary.recommendations && ioc.enrichment.summary.recommendations.length > 0 && (
                                  <div>
                                    <strong style={{ color: '#fbbf24', fontSize: '10px' }}>Recommendations:</strong>
                                    <ul style={{ margin: '2px 0', paddingLeft: '16px', fontSize: '12px' }}>
                                      {ioc.enrichment.summary.recommendations.map((rec, idx) => (
                                        <li key={idx} style={{ color: '#e5e7eb' }}>{rec}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                          
                          {/* Service Results */}
                          {ioc.enrichment.enrichments && (
                            <div>
                              <strong style={{ color: '#fbbf24', fontSize: '11px' }}>ENRICHMENT RESULTS:</strong>
                              <div style={{ marginTop: '4px' }}>
                                {Object.entries(ioc.enrichment.enrichments).map(([service, data]) => (
                                  <div key={service} style={{ 
                                    marginBottom: '8px', 
                                    padding: '8px', 
                                    backgroundColor: '#1f2937', 
                                    borderRadius: '4px',
                                    border: '1px solid #374151'
                                  }}>
                                    <strong style={{ color: '#22d3ee', fontSize: '11px' }}>{service}:</strong>
                                    {data.error ? (
                                      <p style={{ color: '#ef4444', fontSize: '11px', margin: '2px 0' }}>{data.error}</p>
                                    ) : (
                                      <div style={{ fontSize: '11px', marginTop: '2px' }}>
                                        {service === 'AbuseIPDB' && (
                                          <div>
                                            <span style={{ color: '#e5e7eb' }}>
                                              Confidence: {data.abuse_confidence_percentage}% | 
                                              Reports: {data.total_reports} | 
                                              Country: {data.country_code}
                                            </span>
                                          </div>
                                        )}
                                        {service === 'VirusTotal' && (
                                          <div>
                                            <span style={{ color: '#e5e7eb' }}>
                                              Malicious: {data.malicious_detections} | 
                                              Detection Rate: {data.detection_rate}% | 
                                              Total Engines: {data.total_engines}
                                            </span>
                                          </div>
                                        )}
                                        {service === 'Shodan' && (
                                          <div>
                                            <span style={{ color: '#e5e7eb' }}>
                                              Open Ports: {data.open_ports_count} | 
                                              Vulnerabilities: {data.vulnerabilities?.length || 0} | 
                                              Country: {data.country}
                                            </span>
                                          </div>
                                        )}
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {!loadingAttackIocs && attackIocs.length === 0 && !attackIocsError && (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <p style={{ color: '#9ca3af', fontSize: '18px' }}>Click "Analyze IOCs" to get related indicators with threat intelligence analysis.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AttackDetail;
