import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_resume_feedback(resume_text: str, jd_text: str, missing_skills: list) -> str:
    """
    Uses GPT to generate personalized resume improvement suggestions.
    """
    prompt = f"""
    You are an expert career coach. A candidate applied for the following job:

    JOB DESCRIPTION:
    {jd_text}

    CANDIDATE RESUME:
    {resume_text}

    Missing Skills (from analysis): {", ".join(missing_skills)}

    Please give structured, actionable feedback to the candidate.
    Focus on:
    1. How well their resume matches the JD.
    2. What missing skills/certifications they should add.
    3. How they can improve their projects/achievements.
    4. Resume writing suggestions (clarity, keywords, formatting).
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4o" if available
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=400
    )

    return response.choices[0].message.content
