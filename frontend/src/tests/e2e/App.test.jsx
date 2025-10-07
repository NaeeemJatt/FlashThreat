import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import App from '../../App';
import * as api from '../../lib/api';

// Mock the API module
vi.mock('../../lib/api', () => ({
  checkIOC: vi.fn(),
  streamIOC: vi.fn(),
  getLookupHistory: vi.fn(),
  submitBulkJob: vi.fn(),
  getBulkJobProgress: vi.fn(),
}));

// Mock the auth module
vi.mock('../../lib/auth', () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => ({
    user: { id: '1', email: 'test@example.com', role: 'analyst' },
    loading: false,
    isAuthenticated: true,
    login: vi.fn(),
    logout: vi.fn(),
  }),
}));

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('App E2E Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the home page correctly', () => {
    renderWithRouter(<App />);
    
    expect(screen.getByText(/Flash Intelligence/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/enter ip, domain, url, or hash/i)).toBeInTheDocument();
  });

  it('handles IOC check flow', async () => {
    const mockResult = {
      lookup_id: 'test-id',
      providers: [
        { provider: 'virustotal', status: 'success' },
        { provider: 'abuseipdb', status: 'success' },
        { provider: 'otx', status: 'success' }
      ],
      summary: { verdict: 'clean', score: 0 }
    };

    api.checkIOC.mockResolvedValue(mockResult);

    renderWithRouter(<App />);
    
    const input = screen.getByPlaceholderText(/enter ip, domain, url, or hash/i);
    const button = screen.getByRole('button', { name: /check ioc/i });

    fireEvent.change(input, { target: { value: '8.8.8.8' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(api.checkIOC).toHaveBeenCalledWith('8.8.8.8', false);
    });
  });

  it('handles navigation between pages', () => {
    renderWithRouter(<App />);
    
    // Navigate to bulk page
    const bulkLink = screen.getByText(/bulk/i);
    fireEvent.click(bulkLink);
    
    expect(screen.getByText(/bulk analysis/i)).toBeInTheDocument();
  });

  it('handles error states gracefully', async () => {
    api.checkIOC.mockRejectedValue(new Error('Network error'));

    renderWithRouter(<App />);
    
    const input = screen.getByPlaceholderText(/enter ip, domain, url, or hash/i);
    const button = screen.getByRole('button', { name: /check ioc/i });

    fireEvent.change(input, { target: { value: '8.8.8.8' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('handles bulk file upload', async () => {
    const mockFile = new File(['test,data\n8.8.8.8,test'], 'test.csv', { type: 'text/csv' });
    const mockResponse = { job_id: 'test-job', status: 'pending' };

    api.submitBulkJob.mockResolvedValue(mockResponse);

    renderWithRouter(<App />);
    
    // Navigate to bulk page
    const bulkLink = screen.getByText(/bulk/i);
    fireEvent.click(bulkLink);
    
    const fileInput = screen.getByLabelText(/choose file/i);
    fireEvent.change(fileInput, { target: { files: [mockFile] } });
    
    const submitButton = screen.getByRole('button', { name: /submit/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(api.submitBulkJob).toHaveBeenCalled();
    });
  });

  it('handles authentication flow', () => {
    renderWithRouter(<App />);
    
    // Should show login page when not authenticated
    expect(screen.getByText(/login/i)).toBeInTheDocument();
  });
});
