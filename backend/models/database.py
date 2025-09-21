from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./resumes.db"  # SQLite for MVP

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ResumeEvaluation(Base):
    __tablename__ = "resume_evaluations"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, index=True)
    job_role = Column(String, index=True)
    relevance_score = Column(Float)
    missing_skills = Column(Text)
    verdict = Column(String)
    feedback = Column(Text)

Base.metadata.create_all(bind=engine)
