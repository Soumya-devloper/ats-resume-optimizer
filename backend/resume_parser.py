"""
Resume Parser - Extract and structure resume content
"""

import re
from typing import Dict, List, Any
from enum import Enum


class ResumeSection(str, Enum):
    """Common resume sections"""
    CONTACT = "contact"
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    CERTIFICATIONS = "certifications"
    PROJECTS = "projects"
    OTHER = "other"


def parse_resume(resume_text: str) -> Dict[str, Any]:
    """
    Parse resume text into structured sections.

    Args:
        resume_text: Raw resume text

    Returns:
        Dictionary with parsed sections
    """
    sections = {
        "contact": extract_contact_info(resume_text),
        "summary": extract_summary(resume_text),
        "experience": extract_experience(resume_text),
        "education": extract_education(resume_text),
        "skills": extract_skills(resume_text),
        "certifications": extract_certifications(resume_text),
        "projects": extract_projects(resume_text),
        "raw_text": resume_text,
        "word_count": len(resume_text.split()),
    }

    return sections


def extract_contact_info(text: str) -> Dict[str, str]:
    """Extract contact information"""
    contact = {}

    # Email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_match:
        contact["email"] = email_match.group(0)

    # Phone
    phone_match = re.search(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b', text)
    if phone_match:
        contact["phone"] = phone_match.group(0)

    # LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
    if linkedin_match:
        contact["linkedin"] = linkedin_match.group(0)

    # GitHub
    github_match = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
    if github_match:
        contact["github"] = github_match.group(0)

    return contact


def extract_summary(text: str) -> str:
    """Extract professional summary"""
    # Look for common section headers
    summary_headers = [
        r'(?:professional\s+)?summary',
        r'objective',
        r'profile',
        r'about\s+me',
    ]

    for header in summary_headers:
        pattern = rf'{header}[:\s]*(.+?)(?=\n\s*(?:experience|education|skills|certification|project|$))'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            summary_text = match.group(1).strip()
            # Get first 500 chars or first paragraph
            return summary_text.split('\n\n')[0][:500]

    return ""


def extract_experience(text: str) -> List[Dict[str, str]]:
    """Extract work experience entries"""
    experience = []

    # Look for experience section
    exp_match = re.search(
        r'(?:work\s+)?experience[:\s]*(.+?)(?=\n\s*(?:education|skills|certification|project|$))',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if not exp_match:
        return experience

    exp_section = exp_match.group(1)

    # Split into individual job entries (rough heuristic)
    # Look for date patterns or job titles
    entries = re.split(r'\n(?=\S+(?:\s+\S+)*\s+[-–])', exp_section)

    for entry in entries:
        if len(entry.strip()) > 10:
            lines = entry.strip().split('\n')
            job = {
                "company": "",
                "title": "",
                "dates": "",
                "description": ""
            }

            if lines:
                # First line often contains company/title
                first_line = lines[0]
                job["company"] = first_line.split("|")[0].strip() if "|" in first_line else first_line[:50]

            if len(lines) > 1:
                job["title"] = lines[1][:50]

            if len(lines) > 2:
                job["description"] = "\n".join(lines[2:])

            experience.append(job)

    return experience


def extract_education(text: str) -> List[Dict[str, str]]:
    """Extract education entries"""
    education = []

    # Look for education section
    edu_match = re.search(
        r'education[:\s]*(.+?)(?=\n\s*(?:skills|experience|certification|project|$))',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if not edu_match:
        return education

    edu_section = edu_match.group(1)
    entries = re.split(r'\n(?=\S)', edu_section)

    for entry in entries:
        if len(entry.strip()) > 5:
            degree_match = re.search(
                r'(?:Bachelor|Master|PhD|Associate|B\.S\.|M\.S\.|B\.A\.|M\.A\.|B\.E\.|M\.E\.|MBA|MA|BS|MS|BE)',
                entry,
                re.IGNORECASE
            )

            school_match = re.search(r'(?:from|at|University|College|Institute|School)\s+(.+?)(?:\n|$)', entry)

            education.append({
                "degree": degree_match.group(0) if degree_match else "",
                "school": school_match.group(1).strip() if school_match else entry.split('\n')[0][:50],
                "raw": entry.strip()[:200]
            })

    return education


def extract_skills(text: str) -> List[str]:
    """Extract skills"""
    skills = []

    # Look for skills section
    skills_match = re.search(
        r'(?:core\s+)?skills?[:\s]*(.+?)(?=\n\s*(?:experience|education|certification|project|$))',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if not skills_match:
        return skills

    skills_section = skills_match.group(1)

    # Split by common delimiters
    skill_list = re.split(r'[,•\-\|]|\n(?=\S)', skills_section)

    for skill in skill_list:
        skill_clean = skill.strip()
        if len(skill_clean) > 2 and len(skill_clean) < 50:
            skills.append(skill_clean)

    return skills[:30]  # Limit to 30 skills


def extract_certifications(text: str) -> List[str]:
    """Extract certifications and licenses"""
    certs = []

    cert_match = re.search(
        r'(?:certifications?|licenses?|credentials?)[:\s]*(.+?)(?=\n\s*(?:skills|experience|education|project|$))',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if not cert_match:
        return certs

    cert_section = cert_match.group(1)
    cert_list = re.split(r'[,•\-]|\n(?=\S)', cert_section)

    for cert in cert_list:
        cert_clean = cert.strip()
        if len(cert_clean) > 3 and len(cert_clean) < 100:
            certs.append(cert_clean)

    return certs[:15]


def extract_projects(text: str) -> List[Dict[str, str]]:
    """Extract projects"""
    projects = []

    proj_match = re.search(
        r'(?:projects?|portfolio)[:\s]*(.+?)(?=\n\s*(?:skills|experience|education|certification|$))',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if not proj_match:
        return projects

    proj_section = proj_match.group(1)
    entries = re.split(r'\n(?=\S+(?:\s+\S+)*\s*[:–-])', proj_section)

    for entry in entries:
        if len(entry.strip()) > 10:
            lines = entry.strip().split('\n')
            projects.append({
                "title": lines[0][:50] if lines else "",
                "description": "\n".join(lines[1:])[:200] if len(lines) > 1 else ""
            })

    return projects[:10]


def get_section_text(text: str, section: ResumeSection) -> str:
    """Get raw text for a specific section"""
    section_patterns = {
        ResumeSection.CONTACT: r'contact|phone|email|address',
        ResumeSection.SUMMARY: r'summary|objective|profile|about',
        ResumeSection.EXPERIENCE: r'experience|employment|work\s+history',
        ResumeSection.EDUCATION: r'education|academic',
        ResumeSection.SKILLS: r'skills?|competencies',
        ResumeSection.CERTIFICATIONS: r'certifications?|licenses?',
        ResumeSection.PROJECTS: r'projects?|portfolio',
    }

    pattern = section_patterns.get(section, "")
    if not pattern:
        return ""

    match = re.search(
        rf'{pattern}[:\s]*(.+?)(?=\n\s*(?:' +
        '|'.join([p for k, p in section_patterns.items() if k != section]) +
        r'|$))',
        text,
        re.IGNORECASE | re.DOTALL
    )

    return match.group(1).strip() if match else ""
