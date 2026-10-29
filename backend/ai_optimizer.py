"""
AI Optimizer - Use LLM to optimize resume for ATS and job match
"""

import os
import json
import re
from typing import Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"  # Using gpt-4o-mini for better balance of cost and quality


def optimize_resume(
    resume_text: str,
    job_description: str,
    auto_iterate: bool = True,
    target_score: float = 85.0,
    max_iterations: int = 5,
    user_feedback: Optional[str] = None,
    version_number: int = 1
) -> Dict[str, any]:
    """
    Optimize resume using AI based on job description.

    Args:
        resume_text: Original resume text
        job_description: Target job description
        auto_iterate: Whether to automatically iterate for improvement
        target_score: Target ATS score to achieve
        max_iterations: Maximum iterations for auto-improvement
        user_feedback: Optional user feedback for refinement
        version_number: Version number for tracking

    Returns:
        Dictionary with optimized resume and improvements list
    """
    improvements = []
    current_resume = resume_text
    iteration = 0

    # Initial optimization
    result = optimize_single_pass(
        current_resume,
        job_description,
        user_feedback,
        version_number
    )

    optimized = result["optimized_resume"]
    improvements.extend(result["improvements"])
    iteration += 1

    # Auto-iterate if enabled
    if auto_iterate and iteration < max_iterations:
        # Import here to avoid circular dependency
        from ats_scorer import calculate_ats_score

        current_score = calculate_ats_score(optimized, job_description)["total_score"]

        while current_score < target_score and iteration < max_iterations:
            # Get feedback on what needs improvement
            feedback = generate_improvement_feedback(
                optimized,
                job_description,
                current_score,
                target_score
            )

            # Refine based on feedback
            result = optimize_single_pass(
                optimized,
                job_description,
                feedback,
                version_number + iteration
            )

            optimized = result["optimized_resume"]
            improvements.extend(result["improvements"])
            iteration += 1

            # Check new score
            current_score = calculate_ats_score(optimized, job_description)["total_score"]

    return {
        "optimized_resume": optimized,
        "improvements": list(set(improvements)),  # Remove duplicates
        "iterations": iteration,
        "version": version_number + iteration - 1
    }


def optimize_single_pass(
    resume_text: str,
    job_description: str,
    feedback: Optional[str] = None,
    version_number: int = 1
) -> Dict[str, any]:
    """
    Single pass optimization using AI.
    """
    # Build the prompt
    if feedback:
        prompt = build_refinement_prompt(resume_text, job_description, feedback, version_number)
    else:
        prompt = build_optimization_prompt(resume_text, job_description, version_number)

    try:
        # Call OpenAI
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert ATS (Applicant Tracking System) resume optimizer.
Your goal is to improve resumes to match job descriptions while maintaining authenticity and accuracy.
Focus on:
1. Adding relevant keywords from the job description
2. Restructuring content for ATS parsing
3. Using action verbs and quantifiable results
4. Improving formatting for ATS compatibility
5. Ensuring proper section organization

Always maintain the candidate's actual experience and qualifications.
Output ONLY valid JSON with no additional text."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )

        # Parse response
        response_text = response.choices[0].message.content
        result = json.loads(response_text)

        return {
            "optimized_resume": result.get("optimized_resume", resume_text),
            "improvements": result.get("improvements", []),
            "explanation": result.get("explanation", "")
        }

    except json.JSONDecodeError:
        print("Error parsing JSON response from OpenAI")
        return {
            "optimized_resume": resume_text,
            "improvements": [],
            "explanation": "Error parsing optimization response"
        }
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        raise


def build_optimization_prompt(
    resume_text: str,
    job_description: str,
    version_number: int = 1
) -> str:
    """
    Build the initial optimization prompt.
    """
    return f"""Optimize this resume for the following job description. Return a JSON object.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Instructions:
1. Analyze the job description for key skills, requirements, and keywords
2. Improve the resume by:
   - Adding relevant keywords from the job description (naturally, not keyword stuffing)
   - Reorganizing sections for better ATS parsing
   - Enhancing descriptions with action verbs and metrics
   - Ensuring clear section headers (Experience, Education, Skills, etc.)
3. Keep all actual information accurate - don't fabricate experience
4. Improve formatting for ATS compatibility

Return a JSON object with this exact structure:
{{
    "optimized_resume": "The complete optimized resume text",
    "improvements": ["Improvement 1", "Improvement 2", ...],
    "explanation": "Brief explanation of changes"
}}"""


def build_refinement_prompt(
    resume_text: str,
    job_description: str,
    feedback: str,
    version_number: int
) -> str:
    """
    Build a refinement prompt based on user feedback.
    """
    return f"""Refine this resume based on the provided feedback. Return a JSON object.

CURRENT RESUME (Version {version_number}):
{resume_text}

JOB DESCRIPTION:
{job_description}

FEEDBACK/FOCUS AREAS:
{feedback}

Instructions:
1. Address the feedback provided
2. Focus on the specific improvement areas mentioned
3. Keep changes natural and authentic
4. Maintain all accurate information
5. Improve ATS compatibility

Return a JSON object with this exact structure:
{{
    "optimized_resume": "The complete refined resume text",
    "improvements": ["Improvement 1", "Improvement 2", ...],
    "explanation": "Brief explanation of changes"
}}"""


def generate_improvement_feedback(
    resume_text: str,
    job_description: str,
    current_score: float,
    target_score: float
) -> str:
    """
    Generate AI feedback on what to improve next.
    """
    prompt = f"""Analyze this resume and job description. Provide specific feedback on what to improve.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Current ATS Score: {current_score}/100
Target Score: {target_score}/100

Provide 3-5 specific, actionable improvements to increase the ATS score.
Focus on the gap between current and target score.
Be concise and specific."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an ATS optimization expert. Provide specific, actionable feedback."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error generating improvement feedback: {e}")
        return "Focus on adding more relevant keywords and quantifiable metrics."


def extract_keywords_from_jd(job_description: str) -> List[str]:
    """
    Extract key skills and requirements from job description.
    """
    prompt = f"""Extract the top 15 technical and professional skills/keywords from this job description.
Return as a JSON array of strings.

JOB DESCRIPTION:
{job_description}

Return ONLY a valid JSON array like: ["skill1", "skill2", ...]"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Extract keywords from job descriptions. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=300
        )

        keywords = json.loads(response.choices[0].message.content)
        return keywords if isinstance(keywords, list) else []

    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return []


def generate_summary(
    resume_text: str,
    job_description: str
) -> str:
    """
    Generate a professional summary tailored to the job.
    """
    prompt = f"""Generate a professional summary (2-3 sentences) for this resume based on the job description.
The summary should highlight relevant experience and align with the job requirements.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return ONLY the summary text, no JSON needed."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Generate professional summaries for resumes. Be concise and impactful."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=300
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating summary: {e}")
        return ""
