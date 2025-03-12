'use client';

import { useState, useEffect } from 'react';

interface HistoryItem {
  id: string;
  status: string;
  file_path: string | null;
  created_at: string;
}

interface HistoryDisplayProps {
  onSelectDocument: (documentId: string) => void;
}

export const HistoryDisplay: React.FC<HistoryDisplayProps> = ({ onSelectDocument }) => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [mounted, setMounted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    
    const fetchHistory = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/history`);
        
        if (!response.ok) {
          throw new Error(`Error: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        setHistory(data.history || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchHistory();
  }, [mounted]);
  
  // Don't render loading state during hydration
  if (!mounted) {
    return null;
  }
  
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch (e) {
      return dateString;
    }
  };
  
  const getFileName = (filePath: string | null) => {
    if (!filePath) return 'Text Input';
    return filePath.split('/').pop() || filePath;
  };
  
  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p className="mt-2">Loading history...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-100 text-red-800 p-4 rounded-lg">
        <h3 className="text-lg font-medium mb-2">Error Loading History</h3>
        <p>{error}</p>
      </div>
    );
  }
  
  if (history.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No document analysis history found.</p>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-center mb-6">Analysis History</h2>
      
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white dark:bg-gray-800 rounded-lg overflow-hidden">
          <thead className="bg-gray-100 dark:bg-gray-700">
            <tr>
              <th className="py-2 px-4 text-left">Document</th>
              <th className="py-2 px-4 text-left">Status</th>
              <th className="py-2 px-4 text-left">Date</th>
              <th className="py-2 px-4 text-left">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
            {history.map((item) => (
              <tr key={item.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td className="py-3 px-4">{getFileName(item.file_path)}</td>
                <td className="py-3 px-4">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      item.status === 'compliant'
                        ? 'bg-green-100 text-green-800'
                        : item.status === 'non-compliant'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {item.status}
                  </span>
                </td>
                <td className="py-3 px-4">{formatDate(item.created_at)}</td>
                <td className="py-3 px-4">
                  <button
                    onClick={() => onSelectDocument(item.id)}
                    className="text-blue-500 hover:text-blue-700 font-medium"
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}; 