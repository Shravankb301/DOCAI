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
    public_data_checks?: Array<{
      source_name: string;
      source_url: string;
      source_description: string;
      relevance_score: number;
      matched_categories: string[];
    }>;
    citations?: Array<{
      citation_number: number;
      source_name: string;
      source_url: string;
      source_description: string;
      relevance_score: number;
      citation_text: string;
      transformer_score?: number;
      reference_info?: {
        title: string;
        url: string;
        description: string;
        organization?: string;
        publication_date?: string;
        access_date: string;
        categories: string[];
        relevant_sections?: string[];
        section_urls?: Record<string, string>;
        type: string;
      };
    }>;
    enhanced_citations?: Array<{
      source_name: string;
      source_url: string;
      source_description: string;
      relevance_score: number;
      matched_categories: string[];
      transformer_score: number;
    }>;
    analysis_timestamp?: string;
    original_length?: number;
    warning?: string;
    section_analysis?: Array<{
      section_number: number;
      section_text: string;
      status: string;
      confidence: number;
    }>;
    detailed_summary?: {
      compliance_metrics: {
        compliant_sections: number;
        non_compliant_sections: number;
        compliance_percentage: number;
        risk_distribution: {
          high_risk: number;
          medium_risk: number;
          low_risk: number;
        };
      };
      key_regulatory_frameworks: Array<{
        name: string;
        relevance: number;
        description: string;
      }>;
      problematic_sections: Array<{
        section_number: number;
        confidence: number;
        preview: string;
      }>;
      recommendations: string[];
    };
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
          
          {/* Executive Summary Section */}
          {results.detailed_summary && (
            <div className="bg-blue-50 dark:bg-blue-900 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
              <h3 className="text-lg font-medium mb-3 text-blue-800 dark:text-blue-200">Executive Summary</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                {/* Compliance Metrics */}
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-sm">
                  <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Compliance Metrics</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span>Overall Compliance:</span>
                      <span className="font-medium">{results.detailed_summary.compliance_metrics.compliance_percentage.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                      <div 
                        className={`h-2.5 rounded-full ${
                          results.detailed_summary.compliance_metrics.compliance_percentage > 80
                            ? 'bg-green-500'
                            : results.detailed_summary.compliance_metrics.compliance_percentage > 50
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                        }`}
                        style={{ width: `${results.detailed_summary.compliance_metrics.compliance_percentage}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-sm mt-3">
                      <div>
                        <span className="inline-block w-3 h-3 bg-green-500 rounded-full mr-1"></span>
                        <span>Compliant Sections: {results.detailed_summary.compliance_metrics.compliant_sections}</span>
                      </div>
                      <div>
                        <span className="inline-block w-3 h-3 bg-red-500 rounded-full mr-1"></span>
                        <span>Non-Compliant: {results.detailed_summary.compliance_metrics.non_compliant_sections}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Risk Distribution */}
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-sm">
                  <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Risk Distribution</h4>
                  <div className="space-y-2">
                    <div className="flex items-center">
                      <span className="inline-block w-3 h-3 bg-red-500 rounded-full mr-2"></span>
                      <span className="flex-1">High Risk Issues:</span>
                      <span className="font-medium">{results.detailed_summary.compliance_metrics.risk_distribution.high_risk}</span>
                    </div>
                    <div className="flex items-center">
                      <span className="inline-block w-3 h-3 bg-yellow-500 rounded-full mr-2"></span>
                      <span className="flex-1">Medium Risk Issues:</span>
                      <span className="font-medium">{results.detailed_summary.compliance_metrics.risk_distribution.medium_risk}</span>
                    </div>
                    <div className="flex items-center">
                      <span className="inline-block w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                      <span className="flex-1">Low Risk Issues:</span>
                      <span className="font-medium">{results.detailed_summary.compliance_metrics.risk_distribution.low_risk}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Recommendations */}
              {results.detailed_summary.recommendations && results.detailed_summary.recommendations.length > 0 && (
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-sm mb-4">
                  <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Recommendations</h4>
                  <ul className="list-disc pl-5 space-y-1 text-sm">
                    {results.detailed_summary.recommendations.map((recommendation, index) => (
                      <li key={index}>{recommendation}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Key Regulatory Frameworks */}
              {results.detailed_summary.key_regulatory_frameworks && results.detailed_summary.key_regulatory_frameworks.length > 0 && (
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-sm">
                  <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Key Regulatory Frameworks</h4>
                  <div className="space-y-2 text-sm">
                    {results.detailed_summary.key_regulatory_frameworks.map((framework, index) => (
                      <div key={index} className="border-l-4 border-blue-500 pl-3 py-1">
                        <div className="flex justify-between">
                          <span className="font-medium">{framework.name}</span>
                          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                            {(framework.relevance * 100).toFixed(0)}% relevant
                          </span>
                        </div>
                        <p className="text-gray-600 dark:text-gray-400 text-xs mt-1">{framework.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          
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
          
          {/* Section Analysis */}
          {results.section_analysis && results.section_analysis.length > 0 && (
            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
              <h3 className="text-lg font-medium mb-3">Section-by-Section Analysis</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white dark:bg-gray-800 rounded-lg overflow-hidden">
                  <thead className="bg-gray-200 dark:bg-gray-700">
                    <tr>
                      <th className="py-2 px-4 text-left text-xs font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wider">Section</th>
                      <th className="py-2 px-4 text-left text-xs font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wider">Status</th>
                      <th className="py-2 px-4 text-left text-xs font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wider">Confidence</th>
                      <th className="py-2 px-4 text-left text-xs font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wider">Content Preview</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {results.section_analysis.map((section) => (
                      <tr key={section.section_number} className={
                        section.status === 'compliant' 
                          ? 'bg-green-50 dark:bg-green-900 dark:bg-opacity-20' 
                          : 'bg-red-50 dark:bg-red-900 dark:bg-opacity-20'
                      }>
                        <td className="py-2 px-4 text-sm">{section.section_number}</td>
                        <td className="py-2 px-4 text-sm">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            section.status === 'compliant'
                              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                          }`}>
                            {section.status}
                          </span>
                        </td>
                        <td className="py-2 px-4 text-sm">{(section.confidence * 100).toFixed(0)}%</td>
                        <td className="py-2 px-4 text-sm text-gray-500 dark:text-gray-400 whitespace-normal break-words">
                          {/* Improved display for section text */}
                          {section.section_text.startsWith("PDF Document") || 
                           section.section_text.startsWith("Binary content") ||
                           section.section_text.includes("[technical content]") ? (
                            <div className="flex items-center">
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                              </svg>
                              <span className="italic">{section.section_text}</span>
                            </div>
                          ) : (
                            section.section_text
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                Note: This analysis breaks down the document into sections to identify specific areas of compliance concern.
                Binary or non-text content is identified and labeled appropriately.
              </div>
            </div>
          )}
          
          {/* Problematic Sections */}
          {results.detailed_summary && results.detailed_summary.problematic_sections && results.detailed_summary.problematic_sections.length > 0 && (
            <div className="bg-red-50 dark:bg-red-900 dark:bg-opacity-20 p-4 rounded-lg border border-red-200 dark:border-red-800">
              <h3 className="text-lg font-medium mb-3 text-red-800 dark:text-red-200">Problematic Sections</h3>
              <div className="space-y-3">
                {results.detailed_summary.problematic_sections.map((section) => (
                  <div key={section.section_number} className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-sm">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">Section {section.section_number}</span>
                      <span className="text-xs bg-red-100 text-red-800 px-2 py-0.5 rounded-full">
                        {(section.confidence * 100).toFixed(0)}% non-compliant
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{section.preview}</p>
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
          
          {results.public_data_checks && results.public_data_checks.length > 0 && (
            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
              <h3 className="text-lg font-medium mb-3">Compliance Standards Checks</h3>
              <div className="space-y-4">
                {results.public_data_checks.map((check, index) => (
                  <div key={index} className="border-l-4 pl-3 py-1" 
                    style={{ 
                      borderColor: check.relevance_score > 0.7 
                        ? '#3b82f6' 
                        : check.relevance_score > 0.4 
                          ? '#6366f1' 
                          : '#8b5cf6' 
                    }}
                  >
                    <div className="flex items-center mb-1">
                      <span className="font-medium">{check.source_name}</span>
                      <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-800">
                        Relevance: {(check.relevance_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                      {check.source_description}
                    </div>
                    {check.matched_categories.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-2">
                        {check.matched_categories.map((category, catIndex) => (
                          <span key={catIndex} className="px-2 py-0.5 text-xs bg-gray-200 dark:bg-gray-600 rounded-full">
                            {category.replace('_', ' ')}
                          </span>
                        ))}
                      </div>
                    )}
                    <div className="text-sm">
                      <a 
                        href={check.source_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        View Source [{index + 1}]
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Citations */}
          {results.citations && results.citations.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
              <h4 className="text-lg font-medium mb-3">Citations & References</h4>
              <div className="space-y-4 text-sm">
                {results.citations.map((citation, index) => (
                  <div key={index} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                    <div className="flex items-start">
                      <span className="mr-2 font-medium text-gray-700 dark:text-gray-300">{citation.citation_number}.</span>
                      <div className="flex-1">
                        <div className="flex justify-between items-start mb-2">
                          <a 
                            href={citation.source_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline font-medium"
                          >
                            {citation.source_name}
                          </a>
                          <span className="ml-2 px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                            {Math.round(citation.relevance_score * 100)}% match
                          </span>
                        </div>
                        
                        <p className="text-gray-600 dark:text-gray-400 mb-2">
                          {citation.source_description}
                        </p>
                        
                        {/* Citation text in a formatted box */}
                        <div className="bg-white dark:bg-gray-900 p-3 rounded border border-gray-200 dark:border-gray-700 mb-3 font-mono text-xs">
                          {citation.citation_text}
                        </div>
                        
                        {/* Reference details in a grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs mb-3">
                          {citation.reference_info?.organization && (
                            <div>
                              <span className="font-medium text-gray-700 dark:text-gray-300">Organization:</span>
                              <span className="ml-1 text-gray-600 dark:text-gray-400">
                                {citation.reference_info.organization}
                              </span>
                            </div>
                          )}
                          
                          {citation.reference_info?.publication_date && (
                            <div>
                              <span className="font-medium text-gray-700 dark:text-gray-300">Publication Date:</span>
                              <span className="ml-1 text-gray-600 dark:text-gray-400">
                                {citation.reference_info.publication_date}
                              </span>
                            </div>
                          )}
                          
                          <div>
                            <span className="font-medium text-gray-700 dark:text-gray-300">Source Type:</span>
                            <span className="ml-1 text-gray-600 dark:text-gray-400">
                              {citation.reference_info?.type || "Regulatory Document"}
                            </span>
                          </div>
                          
                          <div>
                            <span className="font-medium text-gray-700 dark:text-gray-300">Access Date:</span>
                            <span className="ml-1 text-gray-600 dark:text-gray-400">
                              {citation.reference_info?.access_date || new Date().toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                        
                        {/* Relevant sections */}
                        {citation.reference_info?.relevant_sections && citation.reference_info.relevant_sections.length > 0 && (
                          <div className="mb-3">
                            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Relevant Sections:</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {citation.reference_info.relevant_sections.map((section, secIndex) => (
                                <span key={secIndex} className="px-2 py-0.5 text-xs bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200 rounded-full">
                                  {section}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Categories */}
                        {citation.reference_info?.categories && citation.reference_info.categories.length > 0 && (
                          <div className="mb-3">
                            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Categories:</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {citation.reference_info.categories.map((category, catIndex) => (
                                <span key={catIndex} className="px-2 py-0.5 text-xs bg-gray-200 dark:bg-gray-600 rounded-full">
                                  {category.replace('_', ' ')}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Section URLs */}
                        {citation.reference_info?.section_urls && Object.keys(citation.reference_info.section_urls).length > 0 && (
                          <div className="mb-3">
                            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Specific Section Links:</span>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-1">
                              {Object.entries(citation.reference_info.section_urls).map(([key, url], urlIndex) => (
                                <a 
                                  key={urlIndex}
                                  href={url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center px-2 py-1 text-xs bg-gray-50 text-blue-600 hover:bg-gray-100 rounded border border-gray-200"
                                >
                                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                  </svg>
                                  {key.replace('_', ' ')}
                                </a>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Visit source button */}
                        <div className="mt-3">
                          <a 
                            href={citation.source_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="inline-flex items-center px-3 py-1 text-xs bg-blue-50 text-blue-700 hover:bg-blue-100 rounded border border-blue-200"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                            Visit Source
                          </a>
                        </div>
                        
                        {citation.transformer_score && (
                          <div className="mt-2 text-xs text-gray-500 dark:text-gray-500">
                            AI confidence: {Math.round(citation.transformer_score * 100)}%
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
                <p>Citations are generated based on AI analysis of document content against regulatory sources.</p>
                <p className="mt-1">Higher match percentages indicate stronger relevance to your document.</p>
                <p className="mt-1">Click on source names, section links, or "Visit Source" buttons to access the original regulatory documents.</p>
              </div>
            </div>
          )}
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