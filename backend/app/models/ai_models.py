"""
Module for AI models used in compliance analysis.
This module provides transformer-based models for analyzing document compliance.
"""

from transformers import pipeline
import torch
from typing import List, Dict, Any, Tuple
from app.models.public_data import get_regulatory_sources, search_regulatory_sources

# Check if CUDA is available
device = 0 if torch.cuda.is_available() else -1

# Initialize the transformer model (zero-shot classification)
nlp_pipeline = pipeline(
    "zero-shot-classification", 
    model="facebook/bart-large-mnli",
    device=device
)

def analyze_compliance(text: str, candidate_labels=None) -> Tuple[str, float]:
    """
    Analyze document text for compliance using zero-shot classification.
    
    Args:
        text: The document text to analyze
        candidate_labels: Optional list of compliance labels to check against
        
    Returns:
        Tuple containing the most likely label and its confidence score
    """
    if candidate_labels is None:
        candidate_labels = ["compliant", "non-compliant"]
    
    result = nlp_pipeline(text, candidate_labels)
    label = result["labels"][0]
    confidence = result["scores"][0]
    
    return label, confidence

def analyze_document_sections(text: str, section_size: int = 500) -> List[Dict[str, Any]]:
    """
    Analyze document by breaking it into sections and analyzing each section.
    This helps with longer documents that might exceed model token limits.
    
    Args:
        text: The document text to analyze
        section_size: Size of each section in characters
        
    Returns:
        List of section analysis results
    """
    # Break text into sections
    sections = [text[i:i+section_size] for i in range(0, len(text), section_size)]
    
    results = []
    for i, section in enumerate(sections):
        label, confidence = analyze_compliance(section)
        
        # Clean the section text to ensure it's readable
        preview_text = clean_text_for_preview(section, max_length=100)
        
        results.append({
            "section_number": i + 1,
            "section_text": preview_text,
            "status": label,
            "confidence": confidence
        })
    
    return results

def clean_text_for_preview(text: str, max_length: int = 100) -> str:
    """
    Clean text to make it suitable for preview by removing non-printable characters
    and ensuring it doesn't contain binary data or gibberish.
    
    Args:
        text: The text to clean
        max_length: Maximum length of the preview text
        
    Returns:
        Cleaned text suitable for preview
    """
    import re
    
    # Handle empty text
    if not text or not text.strip():
        return "[Binary or non-text content]"
    
    # Special handling for PDF content
    if text.strip().startswith("%PDF"):
        # Extract readable parts from PDF header
        pdf_parts = re.findall(r'%PDF-[\d.]+|Title\(([^)]+)\)|Author\(([^)]+)\)|Subject\(([^)]+)\)', text)
        if pdf_parts:
            # Flatten the list of tuples and filter out empty strings
            pdf_info = [item for sublist in pdf_parts for item in (sublist if isinstance(sublist, tuple) else [sublist]) if item]
            if pdf_info:
                return "PDF Document: " + ", ".join(pdf_info)
        return "PDF Document [binary content]"
    
    # Special handling for XML/HTML content
    if re.search(r'<\w+[^>]*>.*?</\w+>', text):
        # Check if it's a short XML snippet that can be displayed as is
        if len(text) <= max_length:
            # Just clean any non-printable characters
            return ''.join(c if (c.isprintable() or c.isspace()) else ' ' for c in text)
        
        # For longer XML, provide a structured preview
        tag_content = re.findall(r'>([^<]+)<', text)
        if tag_content:
            clean_content = ' '.join(tag_content).strip()
            if clean_content:
                return f"XML/HTML content: {clean_content[:max_length-20]}..."
        
        # If we can't extract meaningful content, return the first part of the XML
        return text[:max_length] + "..." if len(text) > max_length else text
    
    # Check for high concentration of non-printable characters (likely binary)
    non_printable_count = sum(1 for c in text if not (c.isprintable() or c.isspace()))
    if non_printable_count > len(text) * 0.3:  # If more than 30% is non-printable
        # Try to extract any readable text
        words = re.findall(r'[A-Za-z]{3,}', text)
        if words:
            return f"Binary content with text fragments: {' '.join(words[:5])}..."
        return "[Binary content]"
    
    # For text with some non-printable characters
    if non_printable_count > 0:
        # Replace non-printable characters with spaces
        text = ''.join(c if (c.isprintable() or c.isspace()) else ' ' for c in text)
    
    # Remove control characters except for newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Check for common patterns in binary/encoded data and provide better descriptions
    if re.search(r'obj\s+<<.*>>\s+endobj', text):
        return "PDF Object Structure [technical content]"
    
    if re.search(r'stream.*endstream', text):
        return "PDF Stream Data [technical content]"
    
    if re.search(r'base64,', text):
        return "Base64 Encoded Data [technical content]"
    
    if re.search(r'\\x[0-9a-fA-F]{2}', text):
        return "Escaped Binary Data [technical content]"
    
    # Trim to max_length
    if len(text) > max_length:
        # Try to break at word boundary
        if ' ' in text[:max_length]:
            last_space = text[:max_length].rindex(' ')
            text = text[:last_space] + "..."
        else:
            text = text[:max_length] + "..."
    
    # Final check for empty content after cleaning
    if not text.strip():
        return "[Binary or non-text content]"
    
    return text.strip()

def generate_enhanced_citations(text: str, threshold: float = 0.3) -> List[Dict[str, Any]]:
    """
    Generate enhanced citations using transformer-based matching.
    This function uses the transformer model to compare document content
    against regulatory sources for more accurate citation matching.
    
    Args:
        text: The document text to analyze
        threshold: Minimum relevance score to include a source
        
    Returns:
        List of relevant citations with enhanced relevance scores
    """
    # Get regulatory sources
    sources = get_regulatory_sources()
    
    # First, use keyword matching to get initial matches
    keyword_matches = search_regulatory_sources(text, threshold=0.2)
    
    # For each potential match, use the transformer model to get a more accurate relevance score
    enhanced_matches = []
    
    for match in keyword_matches:
        source_name = match["source_name"]
        source_description = match["source_description"]
        
        # Create hypothesis for zero-shot classification
        hypothesis = f"This document is related to {source_name}: {source_description}"
        
        # Use zero-shot classification to determine relevance
        result = nlp_pipeline(
            text[:1000],  # Use first 1000 chars to avoid token limits
            candidate_labels=["relevant", "not relevant"],
            hypothesis_template="{}."
        )
        
        # Get relevance score
        relevance_index = result["labels"].index("relevant")
        transformer_score = result["scores"][relevance_index]
        
        # Combine keyword match score with transformer score
        # Weight transformer score more heavily (70%)
        combined_score = (0.3 * match["relevance_score"]) + (0.7 * transformer_score)
        
        # Only include if combined score is above threshold
        if combined_score >= threshold:
            enhanced_match = match.copy()
            enhanced_match["relevance_score"] = combined_score
            enhanced_match["transformer_score"] = transformer_score
            enhanced_matches.append(enhanced_match)
    
    # Sort by relevance score (highest first)
    enhanced_matches.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return enhanced_matches 