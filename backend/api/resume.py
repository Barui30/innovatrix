from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from ..models.database import SessionLocal, ResumeEvaluation
from ..utils.parsing import extract_text_from_pdf, extract_text_from_docx
from ..utils.scoring import final_score, extract_missing_skills
from ..utils.llm_feedback import generate_resume_feedback

router = APIRouter()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/evaluate_resume/")
async def evaluate_resume(
    student_name: str = Form(...),
    job_role: str = Form(...),
    jd_text: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Step 1: Extract resume text
    if file.filename.endswith(".pdf"):
        resume_text = await file.read()
        resume_text = extract_text_from_pdf(resume_text)
    elif file.filename.endswith(".docx"):
        resume_text = await file.read()
        resume_text = extract_text_from_docx(resume_text)
    else:
        return {"error": "Unsupported file format"}

    # Step 2: Calculate missing skills
    missing_skills = extract_missing_skills(resume_text, jd_text)

    # Step 3: Calculate score
    score = final_score(resume_text, jd_text)

    # Step 4: Generate AI feedback
    feedback = generate_resume_feedback(resume_text, jd_text, missing_skills)

    # Step 5: Verdict
    verdict = "Strong Match" if score > 70 else "Needs Improvement"

    # Step 6: Save in DB
    evaluation = ResumeEvaluation(
        student_name=student_name,
        job_role=job_role,
        score=score,
        verdict=verdict,
        feedback=feedback,
        missing_skills=", ".join(missing_skills),
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    return {
        "student_name": student_name,
        "job_role": job_role,
        "relevance_score": score,
        "missing_skills": missing_skills,
        "verdict": verdict,
        "feedback": feedback,
    }
