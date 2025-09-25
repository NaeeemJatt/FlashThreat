import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ProviderCard from '../../components/IOC/ProviderCard';

describe('ProviderCard', () => {
  const mockProviderData = {
    provider: 'virustotal',
    status: 'ok',
    latency_ms: 500,
    link: 'https://virustotal.com/gui/ip/8.8.8.8',
    reputation: 10,
    malicious_count: 0,
    suspicious_count: 0,
    harmless_count: 50,
    evidence: [
      {
        title: 'Geolocation',
        category: 'geolocation',
        severity: 'info',
        description: 'Located in United States',
        attributes: { country: 'United States' }
      }
    ]
  };

  it('renders provider name correctly', () => {
    render(<ProviderCard provider="virustotal" data={mockProviderData} />);
    expect(screen.getByText('VirusTotal')).toBeInTheDocument();
  });

  it('renders loading state when data is null', () => {
    render(<ProviderCard provider="virustotal" data={null} />);
    expect(screen.getByText(/loading data from virustotal/i)).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders metrics when data is available', () => {
    render(<ProviderCard provider="virustotal" data={mockProviderData} />);
    expect(screen.getByText('10')).toBeInTheDocument(); // Reputation
    expect(screen.getByText('0')).toBeInTheDocument(); // Malicious
  });

  it('toggles evidence visibility when button is clicked', () => {
    render(<ProviderCard provider="virustotal" data={mockProviderData} />);
    
    // Evidence should be hidden initially
    expect(screen.queryByText('Located in United States')).not.toBeInTheDocument();
    
    // Click the button to show evidence
    fireEvent.click(screen.getByText('Show Evidence'));
    
    // Evidence should now be visible
    expect(screen.getByText('Located in United States')).toBeInTheDocument();
    
    // Click the button again to hide evidence
    fireEvent.click(screen.getByText('Hide Evidence'));
    
    // Evidence should be hidden again
    expect(screen.queryByText('Located in United States')).not.toBeInTheDocument();
  });

  it('renders error state correctly', () => {
    const errorData = {
      provider: 'virustotal',
      status: 'error',
      error: {
        code: 'timeout',
        message: 'Request timed out'
      }
    };
    
    render(<ProviderCard provider="virustotal" data={errorData} />);
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Request timed out')).toBeInTheDocument();
  });

  it('renders cached indicator when data is from cache', () => {
    const cachedData = {
      ...mockProviderData,
      cached: true,
      cache_age_seconds: 120
    };
    
    render(<ProviderCard provider="virustotal" data={cachedData} />);
    expect(screen.getByText(/cached \(120s\)/i)).toBeInTheDocument();
  });

  it('renders external link when available', () => {
    render(<ProviderCard provider="virustotal" data={mockProviderData} />);
    const link = screen.getByText(/view on virustotal/i);
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', 'https://virustotal.com/gui/ip/8.8.8.8');
    expect(link).toHaveAttribute('target', '_blank');
  });
});

