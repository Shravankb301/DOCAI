from transformers import pipeline
import torch
import os
import re
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models.public_data import search_regulatory_sources, format_citations
from app.models.ai_models import analyze_compliance, generate_enhanced_citations

# Try to import the regulatory agents module
try:
    from app.models.regulatory_agents import search_with_agents
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

# Check if CUDA is available
device = 0 if torch.cuda.is_available() else -1

# Initialize the zero-shot classification pipeline
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=device
)

# Define compliance categories
COMPLIANCE_LABELS = [
    "compliant",
    "non-compliant"
]

# Public data sources for compliance checking
PUBLIC_DATA_SOURCES = [
    {
        "name": "GDPR Key Provisions",
        "url": "https://gdpr-info.eu/",
        "description": "General Data Protection Regulation official text and guidelines",
        "categories": ["data_privacy", "personal_data", "data_protection"]
    },
    {
        "name": "HIPAA Compliance Checklist",
        "url": "https://www.hhs.gov/hipaa/for-professionals/index.html",
        "description": "Health Insurance Portability and Accountability Act guidelines",
        "categories": ["healthcare", "medical_data", "patient_privacy"]
    },
    {
        "name": "PCI DSS Requirements",
        "url": "https://www.pcisecuritystandards.org/",
        "description": "Payment Card Industry Data Security Standard",
        "categories": ["payment_processing", "financial_data", "credit_card"]
    },
    {
        "name": "SOX Compliance",
        "url": "https://www.sec.gov/spotlight/sarbanes-oxley.htm",
        "description": "Sarbanes-Oxley Act for financial reporting",
        "categories": ["financial_reporting", "accounting", "corporate_governance"]
    },
    {
        "name": "ISO 27001 Standards",
        "url": "https://www.iso.org/isoiec-27001-information-security.html",
        "description": "Information security management standards",
        "categories": ["information_security", "risk_management", "security_controls"]
    }
]

def analyze_document(text: str) -> Dict[str, Any]:
    """
    Analyze document text for compliance using zero-shot classification.
    
    Args:
        text: The document text to analyze
        
    Returns:
        Dict containing analysis results including compliance status and confidence scores
    """
    # Check if text is empty
    if not text or not text.strip():
        return {
            "status": "error",
            "error_message": "Empty document content",
            "confidence": 0.0
        }
    
    # Truncate text if too long (model has token limits)
    max_length = 4096  # Increased from 2048 to allow more comprehensive analysis
    original_length = len(text)
    truncated = original_length > max_length
    
    # Store the full text for section analysis
    full_text = text
    
    if truncated:
        # Instead of simple truncation, try to preserve important parts
        # Take first 60% and last 40% of the allowed length to capture both beginning and end
        first_part_length = int(max_length * 0.6)
        last_part_length = max_length - first_part_length
        text = text[:first_part_length] + text[original_length - last_part_length:]
    
    # Perform zero-shot classification
    try:
        # Use the new analyze_compliance function from ai_models
        status, confidence = analyze_compliance(text, COMPLIANCE_LABELS)
        
        # Extract key findings from the document
        findings = extract_key_findings(text)
        
        # Check against public data sources using enhanced citation generation
        public_data_checks = check_against_public_data(text)
        
        # Generate enhanced citations using transformer-based matching
        enhanced_citations = generate_enhanced_citations(text)
        
        # Perform section-by-section analysis for more detailed insights
        # Use the full text but limit to a reasonable number of sections
        section_size = 1000  # Analyze in 1000-character chunks
        max_sections = 10    # Limit to 10 sections to avoid overwhelming
        
        # If document is very large, adjust section size to cover more content
        if original_length > section_size * max_sections:
            section_size = min(2000, original_length // max_sections)
            
        # Get section analysis results
        from app.models.ai_models import analyze_document_sections
        section_results = analyze_document_sections(
            full_text[:section_size * max_sections], 
            section_size
        )
        
        # Generate a detailed summary based on section analysis
        detailed_summary = generate_detailed_summary(section_results, findings, public_data_checks)
        
        # Create detailed result
        analysis_result = {
            "status": status,
            "confidence": confidence,
            "all_scores": {},  # Will be populated by the original classifier for backward compatibility
            "analyzed_text_length": len(text),
            "original_length": original_length,
            "truncated": truncated,
            "key_findings": findings,
            "public_data_checks": public_data_checks,
            "citations": format_citations(enhanced_citations),
            "enhanced_citations": enhanced_citations,  # Include the enhanced citations with transformer scores
            "section_analysis": section_results,       # Add section-by-section analysis
            "detailed_summary": detailed_summary,      # Add detailed summary
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # For backward compatibility, also run the original classifier
        result = classifier(
            text, 
            candidate_labels=COMPLIANCE_LABELS,
            hypothesis_template="This document is {}."
        )
        analysis_result["all_scores"] = dict(zip(result["labels"], result["scores"]))
        
        # Add warning if text was truncated
        if truncated:
            analysis_result["warning"] = f"Document was truncated from {original_length} to {max_length} characters for analysis. Analysis includes both the beginning and end of the document, but some middle content may not be reflected in the results."
        
        return analysis_result
    
    except Exception as e:
        # Log the error and return a failure result
        print(f"Error during document analysis: {str(e)}")
        return {
            "status": "error",
            "error_message": str(e),
            "confidence": 0.0
        }

def extract_key_findings(text: str) -> List[Dict[str, Any]]:
    """
    Extract key compliance-related findings from the document.
    
    Args:
        text: The document text
        
    Returns:
        List of key findings
    """
    findings = []
    
    # Define compliance-related keywords and their associated risk levels
    compliance_keywords = {
        "high_risk": [
            "violation", "non-compliance", "breach", "illegal", "prohibited",
            "penalty", "fine", "lawsuit", "litigation", "criminal"
        ],
        "medium_risk": [
            "requirement", "regulation", "policy", "standard", "guideline",
            "law", "rule", "compliance", "mandatory", "obligation"
        ],
        "low_risk": [
            "recommendation", "best practice", "suggestion", "advisory",
            "optional", "consideration", "may", "might", "could"
        ]
    }
    
    # Check for keywords in each risk category
    for risk_level, keywords in compliance_keywords.items():
        for keyword in keywords:
            if keyword in text.lower():
                findings.append({
                    "finding": f"Contains reference to '{keyword}'",
                    "risk_level": risk_level,
                    "context": extract_context(text, keyword)
                })
    
    # Limit the number of findings to avoid overwhelming the user
    if len(findings) > 10:
        findings = findings[:10]
    
    return findings

def extract_context(text: str, keyword: str, context_size: int = 50) -> str:
    """
    Extract the context around a keyword in the text.
    
    Args:
        text: The document text
        keyword: The keyword to find
        context_size: Number of characters to include before and after the keyword
        
    Returns:
        String containing the context around the keyword
    """
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    
    # Find the position of the keyword
    position = text_lower.find(keyword_lower)
    
    if position == -1:
        return ""
    
    # Calculate the start and end positions for the context
    start = max(0, position - context_size)
    end = min(len(text), position + len(keyword) + context_size)
    
    # Extract the context
    context = text[start:end]
    
    # Add ellipsis if the context is truncated
    if start > 0:
        context = "..." + context
    if end < len(text):
        context = context + "..."
    
    return context

def check_against_public_data(text: str) -> List[Dict[str, Any]]:
    """
    Check document against public data sources for compliance references.
    
    Args:
        text: The document text to analyze
        
    Returns:
        List of public data source matches with relevance scores
    """
    # Try to use the agent-based search if available
    if AGENTS_AVAILABLE:
        try:
            # Use the new agent-based search function
            agent_results = search_with_agents(text)
            if agent_results:
                return agent_results
        except Exception as e:
            print(f"Error using agent-based search: {str(e)}")
    
    # Fall back to the standard search if agents are not available or failed
    return search_regulatory_sources(text)

def generate_citations(public_data_checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate formatted citations for the public data sources.
    
    Args:
        public_data_checks: List of public data source matches
        
    Returns:
        List of formatted citations
    """
    # Use the new format_citations function from public_data module
    return format_citations(public_data_checks)

def generate_detailed_summary(section_results: List[Dict[str, Any]], 
                             findings: List[Dict[str, Any]], 
                             public_data_checks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a detailed summary based on section analysis, findings, and public data checks.
    
    Args:
        section_results: Results from section-by-section analysis
        findings: Key findings from the document
        public_data_checks: Results from public data checks
        
    Returns:
        Dict containing detailed summary information
    """
    # Count compliant vs non-compliant sections
    compliant_sections = sum(1 for section in section_results if section["status"] == "compliant")
    non_compliant_sections = len(section_results) - compliant_sections
    
    # Calculate overall compliance percentage
    compliance_percentage = (compliant_sections / len(section_results)) * 100 if section_results else 0
    
    # Count findings by risk level
    risk_counts = {
        "high_risk": sum(1 for finding in findings if finding["risk_level"] == "high_risk"),
        "medium_risk": sum(1 for finding in findings if finding["risk_level"] == "medium_risk"),
        "low_risk": sum(1 for finding in findings if finding["risk_level"] == "low_risk")
    }
    
    # Identify most relevant regulatory frameworks
    top_frameworks = sorted(
        public_data_checks, 
        key=lambda x: x["relevance_score"], 
        reverse=True
    )[:3] if public_data_checks else []
    
    # Identify problematic sections (non-compliant with high confidence)
    problematic_sections = [
        section for section in section_results 
        if section["status"] == "non-compliant" and section["confidence"] > 0.7
    ]
    
    # Generate recommendations based on findings and problematic sections
    recommendations = generate_recommendations(findings, problematic_sections)
    
    # Create the detailed summary
    return {
        "compliance_metrics": {
            "compliant_sections": compliant_sections,
            "non_compliant_sections": non_compliant_sections,
            "compliance_percentage": compliance_percentage,
            "risk_distribution": risk_counts
        },
        "key_regulatory_frameworks": [
            {
                "name": framework["source_name"],
                "relevance": framework["relevance_score"],
                "description": framework["source_description"]
            } for framework in top_frameworks
        ],
        "problematic_sections": [
            {
                "section_number": section["section_number"],
                "confidence": section["confidence"],
                "preview": section["section_text"]
            } for section in problematic_sections
        ],
        "recommendations": recommendations
    }

def generate_recommendations(findings: List[Dict[str, Any]], 
                           problematic_sections: List[Dict[str, Any]]) -> List[str]:
    """
    Generate recommendations based on findings and problematic sections.
    
    Args:
        findings: Key findings from the document
        problematic_sections: Problematic sections identified in the analysis
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # Add recommendations based on high-risk findings
    high_risk_findings = [f for f in findings if f["risk_level"] == "high_risk"]
    if high_risk_findings:
        recommendations.append(
            "Address high-risk compliance issues identified in the key findings section."
        )
        for finding in high_risk_findings[:3]:  # Limit to top 3
            keyword = finding["finding"].replace("Contains reference to '", "").replace("'", "")
            recommendations.append(
                f"Review and revise content related to '{keyword}' to ensure compliance."
            )
    
    # Add recommendations based on problematic sections
    if problematic_sections:
        recommendations.append(
            f"Review {len(problematic_sections)} sections identified as potentially non-compliant."
        )
        if len(problematic_sections) > 3:
            recommendations.append(
                "Focus on the most problematic sections first (those with highest non-compliance confidence)."
            )
    
    # Add general recommendations
    if len(findings) > 5:
        recommendations.append(
            "Consider a comprehensive compliance review as multiple potential issues were identified."
        )
    
    # Ensure we have at least some recommendations
    if not recommendations:
        if findings:
            recommendations.append(
                "Review identified findings to ensure full compliance with relevant regulations."
            )
        else:
            recommendations.append(
                "Document appears to have good compliance, but regular reviews are recommended."
            )
    
    return recommendations 