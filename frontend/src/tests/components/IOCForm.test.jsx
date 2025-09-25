import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import IOCForm from '../../components/IOC/IOCForm';

describe('IOCForm', () => {
  it('renders the form correctly', () => {
    render(<IOCForm onSubmit={() => {}} isLoading={false} />);
    
    // Check if input and button are rendered
    expect(screen.getByPlaceholderText(/enter ip, domain, url, or hash/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /check ioc/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/force refresh/i)).toBeInTheDocument();
  });

  it('disables the button when input is empty', () => {
    render(<IOCForm onSubmit={() => {}} isLoading={false} />);
    
    // Button should be disabled initially
    expect(screen.getByRole('button', { name: /check ioc/i })).toBeDisabled();
    
    // Enter some text
    fireEvent.change(screen.getByPlaceholderText(/enter ip, domain, url, or hash/i), {
      target: { value: '8.8.8.8' },
    });
    
    // Button should be enabled
    expect(screen.getByRole('button', { name: /check ioc/i })).not.toBeDisabled();
  });

  it('disables form elements when loading', () => {
    render(<IOCForm onSubmit={() => {}} isLoading={true} />);
    
    // Input, button, and checkbox should be disabled
    expect(screen.getByPlaceholderText(/enter ip, domain, url, or hash/i)).toBeDisabled();
    expect(screen.getByRole('button', { name: /checking/i })).toBeDisabled();
    expect(screen.getByLabelText(/force refresh/i)).toBeDisabled();
  });

  it('calls onSubmit with the correct values when form is submitted', () => {
    const mockSubmit = vi.fn();
    render(<IOCForm onSubmit={mockSubmit} isLoading={false} />);
    
    // Enter an IOC value
    fireEvent.change(screen.getByPlaceholderText(/enter ip, domain, url, or hash/i), {
      target: { value: '8.8.8.8' },
    });
    
    // Check the force refresh checkbox
    fireEvent.click(screen.getByLabelText(/force refresh/i));
    
    // Submit the form
    fireEvent.submit(screen.getByRole('button', { name: /check ioc/i }));
    
    // Check that onSubmit was called with the correct values
    expect(mockSubmit).toHaveBeenCalledWith('8.8.8.8', true);
  });

  it('trims whitespace from input before submitting', () => {
    const mockSubmit = vi.fn();
    render(<IOCForm onSubmit={mockSubmit} isLoading={false} />);
    
    // Enter an IOC value with whitespace
    fireEvent.change(screen.getByPlaceholderText(/enter ip, domain, url, or hash/i), {
      target: { value: '  8.8.8.8  ' },
    });
    
    // Submit the form
    fireEvent.submit(screen.getByRole('button', { name: /check ioc/i }));
    
    // Check that onSubmit was called with trimmed value
    expect(mockSubmit).toHaveBeenCalledWith('8.8.8.8', false);
  });
});

