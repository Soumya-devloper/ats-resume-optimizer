"""
ATS Scorer - Calculate resume compatibility with job descriptions
"""

import re
from typing import Dict, List, Tuple
from collections import Counter
import math


def calculate_ats_score(resume_text: str, job_description: str) -> Dict[str, any]:
    """
    Calculate comprehensive ATS score for resume against job description.

    Args:
        resume_text: The resume text
        job_description: The job description text

    Returns:
        Dictionary with detailed scoring breakdown
    """
    scores = {}

    # Extract keywords and calculate matches
    scores["keyword_match"] = score_keyword_match(resume_text, job_description)

    # Check formatting and structure
    scores["formatting"] = score_formatting(resume_text)

    # Check for ATS-friendly content
    scores["ats_compatibility"] = score_ats_compatibility(resume_text)

    # Check for required skills/keywords
    scores["required_match"] = score_required_keywords(resume_text, job_description)

    # Calculate weighted total
    weights = {
        "keyword_match": 0.35,
        "required_match": 0.35,
        "formatting": 0.20,
        "ats_compatibility": 0.10
    }

    total_score = sum(scores[key] * weights[key] for key in weights)
    scores["total_score"] = round(total_score, 2)

    # Get detailed breakdown
    scores["details"] = get_scoring_details(resume_text, job_description)

    return scores


def score_keyword_match(resume_text: str, job_description: str) -> float:
    """
    Score based on keyword overlap between resume and job description.
    Returns 0-100 score.
    """
    resume_words = set(extract_keywords(resume_text))
    job_words = set(extract_keywords(job_description))

    if not job_words:
        return 50.0

    # Calculate Jaccard similarity
    intersection = len(resume_words & job_words)
    union = len(resume_words | job_words)

    similarity = intersection / union if union > 0 else 0
    score = similarity * 100

    return round(score, 2)


def score_required_keywords(resume_text: str, job_description: str) -> float:
    """
    Score based on presence of explicitly required keywords/skills.
    Returns 0-100 score.
    """
    # Extract potential required items (often after "required", "must have", etc.)
    required_items = extract_required_keywords(job_description)

    if not required_items:
        return 50.0

    resume_lower = resume_text.lower()
    matched = 0

    for item in required_items:
        if item.lower() in resume_lower:
            matched += 1

    score = (matched / len(required_items)) * 100 if required_items else 0
    return round(score, 2)


def score_formatting(resume_text: str) -> float:
    """
    Score resume formatting for ATS compatibility.
    Returns 0-100 score.
    """
    score = 50.0  # Base score

    # Check for problematic characters
    problematic_chars = ['©', '®', '™', '★', '•']
    problematic_count = sum(resume_text.count(char) for char in problematic_chars)
    if problematic_count > 0:
        score -= min(10, problematic_count * 2)

    # Check line length (avoid overly long lines)
    lines = resume_text.split('\n')
    avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0
    if avg_line_length > 100:
        score -= 5

    # Check for excessive spacing
    double_spaces = resume_text.count('  ')
    if double_spaces > len(lines) * 2:
        score -= 5

    # Bonus for clear section breaks
    section_headers = len(re.findall(r'\n\s*[A-Z][A-Z\s]{2,}\n', resume_text))
    if section_headers >= 4:
        score += 10

    # Bonus for standard fonts (implied by text-only format)
    score += 10

    return round(min(100, max(0, score)), 2)


def score_ats_compatibility(resume_text: str) -> float:
    """
    Score ATS-specific best practices.
    Returns 0-100 score.
    """
    score = 50.0

    # Check for standard sections
    standard_sections = ['experience', 'education', 'skills', 'contact']
    found_sections = sum(1 for section in standard_sections if section.lower() in resume_text.lower())
    score += found_sections * 10

    # Check for good keyword distribution
    words = resume_text.lower().split()
    unique_words = len(set(words))
    word_variety = unique_words / len(words) if words else 0
    if word_variety > 0.5:
        score += 10
    if word_variety < 0.3:
        score -= 10

    # Check for action verbs
    action_verbs = [
        'developed', 'designed', 'managed', 'led', 'created', 'implemented',
        'achieved', 'improved', 'optimized', 'established', 'coordinated',
        'increased', 'reduced', 'accelerated', 'built', 'launched'
    ]
    verb_count = sum(1 for verb in action_verbs if verb in resume_text.lower())
    score += min(15, verb_count * 2)

    # Check for quantifiable results
    quantifiable = len(re.findall(r'\d+%|\$\d+|increased.*\d+|reduced.*\d+', resume_text, re.IGNORECASE))
    score += min(10, quantifiable * 2)

    # Check for too many tables/special formatting (negative)
    tables = len(re.findall(r'\|', resume_text))
    if tables > 20:
        score -= 10

    return round(min(100, max(0, score)), 2)


def extract_keywords(text: str) -> List[str]:
    """
    Extract meaningful keywords from text.
    """
    # Convert to lowercase and split
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())

    # Remove common stop words
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her',
        'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how',
        'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'its',
        'let', 'may', 'say', 'she', 'too', 'use', 'dad', 'mom', 'etc', 'per',
        'via', 'with', 'from', 'that', 'this', 'will', 'been', 'have', 'they',
        'more', 'then', 'only', 'also', 'which', 'about', 'such', 'would'
    }

    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return keywords


def extract_required_keywords(job_description: str) -> List[str]:
    """
    Extract keywords that appear to be required/preferred.
    """
    keywords = []

    # Look for skills after common phrases
    patterns = [
        r'(?:required|must have|essential|required skills?)[:\s]*([^.\n]+)',
        r'(?:preferred|nice to have)[:\s]*([^.\n]+)',
        r'(?:technical skills?|skills? in)[:\s]*([^.\n]+)',
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, job_description, re.IGNORECASE)
        for match in matches:
            text = match.group(1)
            # Extract comma/slash separated items
            items = re.split(r'[,/]|(?:and|or)', text)
            for item in items:
                cleaned = item.strip().lower()
                if cleaned and len(cleaned) > 2 and len(cleaned) < 50:
                    keywords.append(cleaned)

    # Also extract standalone skill/tech words
    tech_keywords = [
        'python', 'java', 'javascript', 'react', 'angular', 'vue', 'nodejs',
        'sql', 'mongodb', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
        'git', 'rest', 'api', 'graphql', 'typescript', 'c++', 'c#', 'golang',
        'rust', 'ruby', 'php', 'scala', 'kotlin', 'swift', 'dart', 'groovy',
        'machine learning', 'deep learning', 'nlp', 'computer vision', 'ai',
        'data science', 'analytics', 'agile', 'scrum', 'devops', 'ci/cd'
    ]

    job_lower = job_description.lower()
    for keyword in tech_keywords:
        if keyword in job_lower:
            keywords.append(keyword)

    return list(set(keywords))  # Remove duplicates


def get_scoring_details(resume_text: str, job_description: str) -> Dict[str, any]:
    """
    Get detailed information for scoring breakdown.
    """
    matched_keywords = []
    missing_keywords = []

    resume_words = set(extract_keywords(resume_text.lower()))
    job_words = set(extract_keywords(job_description.lower()))

    for word in job_words:
        if word in resume_words:
            matched_keywords.append(word)
        else:
            missing_keywords.append(word)

    required_keywords = extract_required_keywords(job_description)
    matched_required = [k for k in required_keywords if k.lower() in resume_text.lower()]
    missing_required = [k for k in required_keywords if k.lower() not in resume_text.lower()]

    return {
        "matched_keywords": matched_keywords[:20],  # Top 20
        "missing_keywords": missing_keywords[:20],  # Top 20
        "matched_required": matched_required[:10],
        "missing_required": missing_required[:10],
        "action_verbs_found": count_action_verbs(resume_text),
        "quantifiable_results": count_quantifiable_results(resume_text),
        "has_contact_info": bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)),
        "has_phone": bool(re.search(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b', resume_text)),
    }


def count_action_verbs(text: str) -> int:
    """Count action verbs in resume"""
    action_verbs = [
        'developed', 'designed', 'managed', 'led', 'created', 'implemented',
        'achieved', 'improved', 'optimized', 'established', 'coordinated',
        'increased', 'reduced', 'accelerated', 'built', 'launched', 'executed',
        'delivered', 'deployed', 'maintained', 'monitored', 'analyzed',
        'engineered', 'orchestrated', 'facilitated', 'spearheaded'
    ]
    text_lower = text.lower()
    return sum(1 for verb in action_verbs if verb in text_lower)


def count_quantifiable_results(text: str) -> int:
    """Count quantifiable results (numbers, percentages, metrics)"""
    patterns = [
        r'\d+%',  # Percentages
        r'\$\d+',  # Amounts
        r'\d+\s*(?:million|thousand|million|k|m)',  # Large numbers
        r'increased.*?\d+',  # Increased X
        r'reduced.*?\d+',  # Reduced X
        r'improved.*?\d+',  # Improved X
        r'\d+\s*(?:customers?|users?|clients?|projects?|teams?)',  # Quantities
    ]
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text, re.IGNORECASE))
    return count
