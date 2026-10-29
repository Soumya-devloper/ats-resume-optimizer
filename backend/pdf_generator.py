"""
PDF Generator - Create ATS-friendly PDF from resume text
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re


def generate_ats_friendly_pdf(resume_text: str, output_path: str) -> str:
    """
    Generate an ATS-friendly PDF from resume text.

    Args:
        resume_text: The resume text content
        output_path: Where to save the PDF

    Returns:
        Path to the generated PDF
    """
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    # Build story (content)
    story = []

    # Get styles
    styles = getSampleStyleSheet()

    # Create custom styles for ATS compatibility
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor='black',
        spaceAfter=6,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )

    section_style = ParagraphStyle(
        'CustomSection',
        parent=styles['Heading2'],
        fontSize=11,
        textColor='black',
        spaceAfter=4,
        spaceBefore=6,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        borderPadding=2
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor='black',
        spaceAfter=3,
        leading=12,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )

    # Parse and format resume content
    sections = parse_resume_sections(resume_text)

    for section_name, section_content in sections:
        # Add section header
        story.append(Paragraph(section_name.upper(), section_style))

        # Add section content
        if isinstance(section_content, list):
            for item in section_content:
                if isinstance(item, dict):
                    # For structured items (jobs, education)
                    for key, value in item.items():
                        if value:
                            formatted = f"<b>{key}:</b> {value}"
                            story.append(Paragraph(formatted, body_style))
                else:
                    # For simple text items
                    story.append(Paragraph(item, body_style))
        else:
            # For plain text sections
            story.append(Paragraph(section_content, body_style))

        story.append(Spacer(1, 0.1*inch))

    # Build PDF
    doc.build(story)

    return output_path


def parse_resume_sections(resume_text: str) -> list:
    """
    Parse resume text into sections for better formatting.

    Returns:
        List of (section_name, section_content) tuples
    """
    sections = []

    # Define section patterns
    section_patterns = [
        (r'contact\s+info(?:rmation)?', 'CONTACT INFORMATION'),
        (r'professional\s+(?:summary|objective|profile|overview)', 'PROFESSIONAL SUMMARY'),
        (r'(?:work\s+)?experience', 'EXPERIENCE'),
        (r'education', 'EDUCATION'),
        (r'(?:technical\s+)?skills?', 'SKILLS'),
        (r'(?:certifications?|licenses?|credentials?)', 'CERTIFICATIONS'),
        (r'projects?', 'PROJECTS'),
    ]

    # Extract each section
    for pattern, section_name in section_patterns:
        match = re.search(
            rf'{pattern}\s*[:.\s]*(.+?)(?=\n\s*[A-Z][A-Z\s]{2,}|$)',
            resume_text,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            content = match.group(1).strip()
            sections.append((section_name, format_section_content(section_name, content)))

    # If no structured sections found, return the whole text
    if not sections:
        sections.append(("RESUME", resume_text))

    return sections


def format_section_content(section_name: str, content: str) -> str:
    """
    Format section content appropriately based on section type.
    """
    section_name_lower = section_name.lower()

    if 'experience' in section_name_lower:
        return format_experience_section(content)
    elif 'education' in section_name_lower:
        return format_education_section(content)
    elif 'skills' in section_name_lower:
        return format_skills_section(content)
    elif 'contact' in section_name_lower:
        return format_contact_section(content)
    else:
        return content.strip()


def format_experience_section(content: str) -> list:
    """Format experience entries"""
    items = []

    # Split by common patterns (dates, company names, etc.)
    entries = re.split(r'\n(?=\S+(?:\s+\S+)*\s+[-–]|\d{1,2}/\d{1,2})', content)

    for entry in entries:
        if len(entry.strip()) > 10:
            lines = entry.strip().split('\n')
            job_dict = {}

            # Try to parse lines
            if len(lines) >= 1:
                # First line: Company and dates
                first_line = lines[0]
                if '|' in first_line:
                    parts = first_line.split('|')
                    job_dict['Company'] = parts[0].strip()
                    if len(parts) > 1:
                        job_dict['Dates'] = parts[1].strip()
                else:
                    job_dict['Company'] = first_line

            if len(lines) >= 2:
                job_dict['Position'] = lines[1].strip()

            if len(lines) > 2:
                job_dict['Description'] = ' '.join(lines[2:]).strip()

            if job_dict:
                items.append(job_dict)

    return items if items else [content.strip()]


def format_education_section(content: str) -> list:
    """Format education entries"""
    items = []

    entries = re.split(r'\n(?=\S)', content)

    for entry in entries:
        if len(entry.strip()) > 5:
            lines = entry.strip().split('\n')
            edu_dict = {}

            # Extract degree
            degree_match = re.search(
                r'(?:Bachelor|Master|PhD|Associate|B\.S\.|M\.S\.|B\.A\.|M\.A\.|B\.E\.|M\.E\.|MBA|MA|BS|MS|BE)',
                entry,
                re.IGNORECASE
            )
            if degree_match:
                edu_dict['Degree'] = degree_match.group(0)

            # Extract school
            if lines:
                school = lines[0]
                if len(school) > 3:
                    edu_dict['School'] = school

            if len(lines) > 1:
                edu_dict['Details'] = ' '.join(lines[1:]).strip()

            if edu_dict:
                items.append(edu_dict)

    return items if items else [content.strip()]


def format_skills_section(content: str) -> list:
    """Format skills as bullet points"""
    items = []

    # Split by common delimiters
    skills = re.split(r'[,•\-\|]|\n', content)

    for skill in skills:
        skill_clean = skill.strip()
        if len(skill_clean) > 2 and len(skill_clean) < 50:
            items.append(skill_clean)

    return items[:30] if items else [content.strip()]


def format_contact_section(content: str) -> str:
    """Format contact information"""
    lines = content.strip().split('\n')
    formatted_lines = []

    for line in lines:
        line_clean = line.strip()
        if line_clean:
            formatted_lines.append(line_clean)

    return ' | '.join(formatted_lines)


def create_simple_pdf(resume_text: str, output_path: str) -> str:
    """
    Create a minimal ATS-friendly PDF with no special formatting.
    This is the safest approach for ATS compatibility.

    Args:
        resume_text: The resume text
        output_path: Output file path

    Returns:
        Path to generated PDF
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Create canvas
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Set margins
    left_margin = 0.5 * inch
    top_margin = 0.5 * inch
    line_height = 14  # Points

    # Add text
    c.setFont("Helvetica", 10)

    y = height - top_margin
    x = left_margin

    # Split text into lines and add to canvas
    lines = resume_text.split('\n')

    for line in lines:
        # Handle page breaks
        if y < 0.5 * inch:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - top_margin

        # Clean line and add to canvas
        if line.strip():
            c.drawString(x, y, line[:120])  # Limit line length

        y -= line_height

    c.save()
    return output_path
