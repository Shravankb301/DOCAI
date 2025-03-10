from transformers import pipeline
import torch
import os
from typing import Dict, Any, List

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
    max_length = 2048  # Increased from 1024
    original_length = len(text)
    truncated = original_length > max_length
    
    if truncated:
        text = text[:max_length]
    
    # Perform zero-shot classification
    try:
        result = classifier(
            text, 
            candidate_labels=COMPLIANCE_LABELS,
            hypothesis_template="This document is {}."
        )
        
        # Get the most likely label and its score
        status = result["labels"][0]
        confidence = result["scores"][0]
        
        # Extract key findings from the document
        findings = extract_key_findings(text)
        
        # Create detailed result
        analysis_result = {
            "status": status,
            "confidence": confidence,
            "all_scores": dict(zip(result["labels"], result["scores"])),
            "analyzed_text_length": len(text),
            "original_length": original_length,
            "truncated": truncated,
            "key_findings": findings
        }
        
        # Add warning if text was truncated
        if truncated:
            analysis_result["warning"] = f"Document was truncated from {original_length} to {max_length} characters for analysis. Results may not reflect the entire document."
        
        return analysis_result
    
    except Exception as e:
        # Log the error and return a failure result
        print(f"Error during document analysis: {str(e)}")
        return {
            "status": "error",
            "error_message": str(e),
            "confidence": 0.0
        }

def extract_key_findings(text: str) -> List[str]:
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