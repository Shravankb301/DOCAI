'use client';

import { useState, FormEvent, ChangeEvent, DragEvent } from 'react';

interface UploadFormProps {
  onSubmit: (formData: FormData) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export const UploadForm: React.FC<UploadFormProps> = ({ onSubmit, isLoading, error }) => {
  const [file, setFile] = useState<File | null>(null);
  const [textContent, setTextContent] = useState('');
  const [activeTab, setActiveTab] = useState<'upload' | 'text'>('upload');
  const [isDragging, setIsDragging] = useState(false);
  
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };
  
  const handleTextChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setTextContent(e.target.value);
  };
  
  const handleDragOver = (e: DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };
  
  const handleDragLeave = (e: DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };
  
  const handleDrop = (e: DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
    }
  };
  
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (activeTab === 'upload' && !file) {
      alert('Please select a file to upload');
      return;
    }
    
    if (activeTab === 'text' && !textContent.trim()) {
      alert('Please enter some text content');
      return;
    }
    
    const formData = new FormData();
    
    if (activeTab === 'upload' && file) {
      formData.append('file', file);
    } else if (activeTab === 'text') {
      formData.append('text_content', textContent);
    }
    
    await onSubmit(formData);
  };
  
  return (
    <div>
      <div className="flex border-b mb-4">
        <button
          className={`py-2 px-4 ${
            activeTab === 'upload'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500'
          }`}
          onClick={() => setActiveTab('upload')}
        >
          Upload Document
        </button>
        <button
          className={`py-2 px-4 ${
            activeTab === 'text'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500'
          }`}
          onClick={() => setActiveTab('text')}
        >
          Enter Text
        </button>
      </div>
      
      <form onSubmit={handleSubmit}>
        {activeTab === 'upload' ? (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Upload Document
            </label>
            <div className="flex items-center justify-center w-full">
              <label
                className={`flex flex-col items-center justify-center w-full h-64 border-2 ${
                  isDragging ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-300 border-dashed'
                } rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-700 hover:bg-gray-100`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <svg className="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                    <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                  </svg>
                  <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    TXT, PDF, DOC, DOCX, RTF, MD (MAX. 10MB)
                  </p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  onChange={handleFileChange}
                  accept=".txt,.pdf,.doc,.docx,.rtf,.md"
                />
              </label>
            </div>
            {file && (
              <div className="mt-2 flex items-center p-2 text-sm text-gray-500 bg-gray-100 dark:bg-gray-700 dark:text-gray-300 rounded">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd"></path>
                </svg>
                <span className="truncate max-w-xs">{file.name}</span>
                <span className="ml-2">({(file.size / 1024).toFixed(2)} KB)</span>
                <button
                  type="button"
                  className="ml-auto text-gray-500 hover:text-gray-700"
                  onClick={() => setFile(null)}
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"></path>
                  </svg>
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Document Text
            </label>
            <textarea
              className="w-full px-3 py-2 text-gray-700 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white dark:border-gray-600"
              rows={10}
              placeholder="Enter document text here..."
              value={textContent}
              onChange={handleTextChange}
            ></textarea>
          </div>
        )}
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}
        
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isLoading}
            className={`px-4 py-2 text-white bg-blue-500 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              isLoading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {isLoading ? (
              <div className="flex items-center">
                <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                <span>Analyzing...</span>
              </div>
            ) : (
              'Analyze Document'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}; 