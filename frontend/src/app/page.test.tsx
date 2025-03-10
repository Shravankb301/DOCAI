import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import Home from './page';

// Mock the components to avoid errors
jest.mock('@/components/UploadForm', () => ({
  UploadForm: () => <div data-testid="upload-form">Upload Form</div>,
}));

jest.mock('@/components/ResultsDisplay', () => ({
  ResultsDisplay: () => <div data-testid="results-display">Results Display</div>,
}));

describe('Home', () => {
  it('renders the page title', () => {
    render(<Home />);
    const heading = screen.getByText('AI Compliance Checker');
    expect(heading).toBeInTheDocument();
  });

  it('renders the upload form initially', () => {
    render(<Home />);
    const uploadForm = screen.getByTestId('upload-form');
    expect(uploadForm).toBeInTheDocument();
  });
}); 