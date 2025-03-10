'use client';

interface ResultsDisplayProps {
  results: {
    status: string;
    confidence: number;
    analyzed_text_length: number;
    all_scores?: Record<string, number>;
    truncated?: boolean;
    error_message?: string;
    key_findings?: Array<{
      finding: string;
      risk_level: string;
      context: string;
    }>;
  };
  onReset: () => void;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results, onReset }) => {
  const isCompliant = results.status === 'compliant';
  const isError = results.status === 'error';
  
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-center">Analysis Results</h2>
      
      {isError ? (
        <div className="bg-red-100 text-red-800 p-4 rounded-lg">
          <h3 className="text-lg font-medium mb-2">Error During Analysis</h3>
          <p>{results.error_message || 'An unknown error occurred during document analysis.'}</p>
        </div>
      ) : (
        <>
          <div className="flex justify-center">
            <div
              className={`inline-flex items-center px-4 py-2 rounded-full ${
                isCompliant
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}
            >
              <span className="text-lg font-medium">
                {isCompliant ? 'Compliant' : 'Non-Compliant'}
              </span>
            </div>
          </div>
          
          <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
            <h3 className="text-lg font-medium mb-3">Confidence Score</h3>
            <div className="w-full bg-gray-200 rounded-full h-4 dark:bg-gray-600">
              <div
                className={`h-4 rounded-full ${
                  isCompliant ? 'bg-green-500' : 'bg-red-500'
                }`}
                style={{ width: `${Number(results.confidence) * 100}%` }}
              ></div>
            </div>
            <div className="flex justify-between mt-1 text-sm">
              <span>0%</span>
              <span>{(Number(results.confidence) * 100).toFixed(0)}%</span>
              <span>100%</span>
            </div>
          </div>
          
          {results.all_scores && (
            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
              <h3 className="text-lg font-medium mb-3">Detailed Scores</h3>
              <div className="space-y-2">
                {Object.entries(results.all_scores).map(([label, score]) => (
                  <div key={label} className="flex justify-between items-center">
                    <span className="capitalize">{label}:</span>
                    <span className="font-medium">{(Number(score) * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {results.key_findings && results.key_findings.length > 0 && (
            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
              <h3 className="text-lg font-medium mb-3">Key Findings</h3>
              <div className="space-y-4">
                {results.key_findings.map((finding, index) => (
                  <div key={index} className="border-l-4 pl-3 py-1" 
                    style={{ 
                      borderColor: finding.risk_level === 'high_risk' 
                        ? '#ef4444' 
                        : finding.risk_level === 'medium_risk' 
                          ? '#f59e0b' 
                          : '#10b981' 
                    }}
                  >
                    <div className="flex items-center mb-1">
                      <span className="font-medium">{finding.finding}</span>
                      <span className="ml-2 px-2 py-0.5 text-xs rounded-full" 
                        style={{ 
                          backgroundColor: finding.risk_level === 'high_risk' 
                            ? '#fee2e2' 
                            : finding.risk_level === 'medium_risk' 
                              ? '#fef3c7' 
                              : '#d1fae5',
                          color: finding.risk_level === 'high_risk' 
                            ? '#b91c1c' 
                            : finding.risk_level === 'medium_risk' 
                              ? '#b45309' 
                              : '#047857'
                        }}
                      >
                        {finding.risk_level.replace('_', ' ')}
                      </span>
                    </div>
                    {finding.context && (
                      <div className="text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-800 p-2 rounded">
                        {finding.context}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
            <h3 className="text-lg font-medium mb-3">Analysis Details</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Text Length Analyzed:</span>
                <span>{results.analyzed_text_length} characters</span>
              </div>
              {results.truncated && (
                <div className="text-amber-600">
                  Note: Document was truncated due to length limitations.
                </div>
              )}
            </div>
          </div>
        </>
      )}
      
      <div className="flex justify-center mt-6">
        <button
          onClick={onReset}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Analyze Another Document
        </button>
      </div>
    </div>
  );
}; 