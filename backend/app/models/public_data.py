"""
Module for managing public regulatory data sources for compliance checking.
This module provides access to curated regulatory sources that can be used
for compliance analysis and citation generation.
"""

from typing import List, Dict, Any, Optional
import os
import json
from datetime import datetime
import re

# Sample regulatory data (this could be extended to pull from a database or API)
REGULATORY_SOURCES = [
    {
        "keyword": "money laundering",
        "title": "Bank Secrecy Act",
        "url": "https://www.fincen.gov/resources/statutes-regulations/bank-secrecy-act",
        "description": "Regulations to combat money laundering and terrorist financing.",
        "categories": ["financial", "banking", "anti_money_laundering"]
    },
    {
        "keyword": "lending",
        "title": "Truth in Lending Act",
        "url": "https://www.consumerfinance.gov/policy-compliance/guidance/implementation-guidance/taft/",
        "description": "Guidelines ensuring transparency in lending practices.",
        "categories": ["financial", "lending", "consumer_protection"]
    },
    {
        "keyword": "data privacy",
        "title": "General Data Protection Regulation (GDPR)",
        "url": "https://gdpr-info.eu/",
        "description": "Comprehensive data privacy regulation in the EU.",
        "categories": ["data_privacy", "personal_data", "data_protection"]
    },
    {
        "keyword": "health information",
        "title": "Health Insurance Portability and Accountability Act (HIPAA)",
        "url": "https://www.hhs.gov/hipaa/for-professionals/index.html",
        "description": "Regulations for protecting sensitive patient health information.",
        "categories": ["healthcare", "medical_data", "patient_privacy"]
    },
    {
        "keyword": "payment processing",
        "title": "Payment Card Industry Data Security Standard (PCI DSS)",
        "url": "https://www.pcisecuritystandards.org/",
        "description": "Security standards for organizations that handle credit card information.",
        "categories": ["payment_processing", "financial_data", "credit_card"]
    },
    {
        "keyword": "financial reporting",
        "title": "Sarbanes-Oxley Act (SOX)",
        "url": "https://www.sec.gov/spotlight/sarbanes-oxley.htm",
        "description": "Regulations for financial disclosure and corporate governance.",
        "categories": ["financial_reporting", "accounting", "corporate_governance"]
    },
    {
        "keyword": "information security",
        "title": "ISO 27001 Standards",
        "url": "https://www.iso.org/isoiec-27001-information-security.html",
        "description": "Information security management standards.",
        "categories": ["information_security", "risk_management", "security_controls"]
    },
    # Adding more regulatory sources
    {
        "keyword": "consumer protection",
        "title": "Consumer Financial Protection Bureau (CFPB) Regulations",
        "url": "https://www.consumerfinance.gov/rules-policy/",
        "description": "Regulations to protect consumers in the financial marketplace.",
        "categories": ["consumer_protection", "financial", "lending"]
    },
    {
        "keyword": "securities",
        "title": "Securities and Exchange Commission (SEC) Regulations",
        "url": "https://www.sec.gov/rules",
        "description": "Regulations governing securities markets and protecting investors.",
        "categories": ["securities", "investing", "financial_markets"]
    },
    {
        "keyword": "anti-corruption",
        "title": "Foreign Corrupt Practices Act (FCPA)",
        "url": "https://www.justice.gov/criminal-fraud/foreign-corrupt-practices-act",
        "description": "U.S. law prohibiting bribery of foreign officials to obtain business advantages.",
        "categories": ["anti_corruption", "bribery", "international_business"]
    },
    {
        "keyword": "environmental compliance",
        "title": "Environmental Protection Agency (EPA) Regulations",
        "url": "https://www.epa.gov/laws-regulations",
        "description": "Regulations to protect human health and the environment.",
        "categories": ["environmental", "pollution", "sustainability"]
    },
    {
        "keyword": "employment",
        "title": "Equal Employment Opportunity Commission (EEOC) Regulations",
        "url": "https://www.eeoc.gov/laws-regulations",
        "description": "Regulations prohibiting workplace discrimination.",
        "categories": ["employment", "discrimination", "workplace"]
    },
    {
        "keyword": "data breach",
        "title": "Data Breach Notification Laws",
        "url": "https://www.ncsl.org/technology-and-communication/security-breach-notification-laws",
        "description": "State laws requiring notification of security breaches involving personal information.",
        "categories": ["data_privacy", "security_breach", "notification"]
    },
    {
        "keyword": "export control",
        "title": "Export Administration Regulations (EAR)",
        "url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "description": "Regulations governing exports of commercial and dual-use items.",
        "categories": ["export_control", "international_trade", "national_security"]
    },
    {
        "keyword": "healthcare compliance",
        "title": "Centers for Medicare & Medicaid Services (CMS) Regulations",
        "url": "https://www.cms.gov/regulations-and-guidance/regulations-and-guidance",
        "description": "Regulations for healthcare providers and facilities.",
        "categories": ["healthcare", "medicare", "medicaid"]
    }
]

def get_regulatory_sources() -> List[Dict[str, Any]]:
    """Return the list of regulatory sources."""
    return REGULATORY_SOURCES

def search_regulatory_sources(text: str, threshold: float = 0.3) -> List[Dict[str, Any]]:
    """
    Search for regulatory sources relevant to the given text.
    
    Args:
        text: The text to search for relevant regulatory sources
        threshold: Minimum relevance score to include a source
        
    Returns:
        List of relevant regulatory sources with relevance scores
    """
    results = []
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    for source in REGULATORY_SOURCES:
        # Initialize relevance score
        relevance_score = 0.0
        
        # Check if keyword is in the text
        if source["keyword"].lower() in text_lower:
            relevance_score += 0.5
        
        # Check if categories are in the text
        matched_categories = []
        for category in source["categories"]:
            # Replace underscores with spaces for matching
            category_term = category.replace("_", " ")
            if category_term in text_lower:
                relevance_score += 0.3
                matched_categories.append(category)
            
            # Also check for the term with underscores
            if category in text_lower:
                relevance_score += 0.3
                if category not in matched_categories:
                    matched_categories.append(category)
        
        # Check if title is in the text
        if source["title"].lower() in text_lower:
            relevance_score += 0.4
        
        # Enhanced matching: Check for related terms
        related_terms = _get_related_terms(source["keyword"])
        for term in related_terms:
            if term.lower() in text_lower:
                relevance_score += 0.2
                break
        
        # Only include sources with relevance above threshold
        if relevance_score >= threshold:
            # Cap the relevance score at 1.0
            relevance_score = min(relevance_score, 1.0)
            
            results.append({
                "source_name": source["title"],
                "source_url": source["url"],
                "source_description": source["description"],
                "relevance_score": relevance_score,
                "matched_categories": matched_categories
            })
    
    # Sort by relevance score (highest first)
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return results

def _get_related_terms(keyword: str) -> List[str]:
    """
    Get related terms for a keyword to enhance search capabilities.
    
    Args:
        keyword: The keyword to find related terms for
        
    Returns:
        List of related terms
    """
    # Dictionary of related terms for common regulatory keywords
    related_terms_dict = {
        "money laundering": ["aml", "anti-money laundering", "financial crime", "suspicious activity", "kyc", "know your customer"],
        "lending": ["loan", "credit", "mortgage", "financing", "borrowing", "interest rate"],
        "data privacy": ["personal data", "data protection", "privacy policy", "data subject", "data controller", "data processor"],
        "health information": ["phi", "protected health information", "medical records", "patient data", "healthcare data"],
        "payment processing": ["payment card", "credit card", "debit card", "card processing", "merchant services"],
        "financial reporting": ["financial statements", "accounting", "audit", "disclosure", "financial records"],
        "information security": ["infosec", "cybersecurity", "data security", "network security", "security controls"],
        "consumer protection": ["consumer rights", "unfair practices", "deceptive practices", "consumer complaints"],
        "securities": ["stocks", "bonds", "investments", "securities trading", "securities fraud"],
        "anti-corruption": ["bribery", "corruption", "foreign officials", "improper payments"],
        "environmental compliance": ["environmental regulations", "pollution control", "emissions", "waste management"],
        "employment": ["labor laws", "workplace", "discrimination", "harassment", "equal opportunity"],
        "data breach": ["security breach", "data leak", "unauthorized access", "data compromise"],
        "export control": ["export regulations", "trade compliance", "sanctions", "restricted items"],
        "healthcare compliance": ["healthcare regulations", "medicare compliance", "medicaid compliance"]
    }
    
    # Return related terms if available, otherwise return empty list
    return related_terms_dict.get(keyword.lower(), [])

def format_citations(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format sources as citations with detailed reference information.
    
    Args:
        sources: List of relevant regulatory sources
        
    Returns:
        List of formatted citations with detailed reference information
    """
    citations = []
    
    for i, source in enumerate(sources):
        citation_number = i + 1
        
        # Get current date for citation
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Extract organization information
        organization = source.get("organization", "")
        if not organization:
            # Try to extract organization from source name
            org_match = re.search(r'\((.*?)\)', source["source_name"])
            if org_match:
                organization = org_match.group(1)
            else:
                # Extract domain from URL as a fallback for organization
                domain_match = re.search(r'https?://(?:www\.)?([^/]+)', source['source_url'])
                if domain_match:
                    domain = domain_match.group(1)
                    # Convert domain to organization name (e.g., gdpr-info.eu -> GDPR Info)
                    organization = ' '.join(word.capitalize() for word in re.sub(r'[.-]', ' ', domain).split())
        
        # Extract publication date
        publication_date = source.get("publication_date", "")
        if not publication_date:
            # Try to extract year from source name or description
            year_match = re.search(r'\b(19|20)\d{2}\b', source["source_name"] + " " + source["source_description"])
            if year_match:
                publication_date = year_match.group(0)
        
        # Format citation text in a standard academic format
        citation_text = f"[{citation_number}] {source['source_name']}. "
        
        # Add organization if available
        if organization:
            citation_text += f"{organization}. "
        
        # Add publication date if available
        if publication_date:
            citation_text += f"Published {publication_date}. "
        
        # Add access information
        citation_text += f"Retrieved from {source['source_url']} on {current_date}."
        
        # Extract specific sections or articles if available
        relevant_sections = []
        if "matched_sections" in source:
            relevant_sections = source["matched_sections"]
        elif "matched_categories" in source:
            # Use categories as a fallback for sections
            relevant_sections = [cat.replace('_', ' ').title() for cat in source["matched_categories"]]
        
        # Create citation object with detailed information
        citation = {
            "citation_number": citation_number,
            "source_name": source["source_name"],
            "source_url": source["source_url"],
            "source_description": source["source_description"],
            "relevance_score": source["relevance_score"],
            "citation_text": citation_text,
            "reference_info": {
                "title": source["source_name"],
                "url": source["source_url"],
                "description": source["source_description"],
                "organization": organization,
                "publication_date": publication_date,
                "access_date": current_date,
                "categories": source.get("matched_categories", []),
                "relevant_sections": relevant_sections,
                "type": source.get("type", "Regulatory Document")
            }
        }
        
        # Add direct links to specific sections if available
        if "section_urls" in source:
            citation["reference_info"]["section_urls"] = source["section_urls"]
        elif "matched_categories" in source and len(source["matched_categories"]) > 0:
            # Generate search URLs for categories
            base_url = source["source_url"]
            if not base_url.endswith('/'):
                base_url += '/'
            
            search_urls = {}
            for category in source["matched_categories"]:
                search_term = category.replace('_', '+')
                search_urls[category] = f"{base_url}search?q={search_term}"
            
            citation["reference_info"]["section_urls"] = search_urls
        
        citations.append(citation)
    
    return citations 