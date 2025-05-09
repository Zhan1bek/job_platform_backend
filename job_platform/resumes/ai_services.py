from openai import OpenAI
import json

from companies.models import Vacancy
from resumes.models import Resume

client = OpenAI(
    api_key="sk-or-v1-....",
    base_url="https://openrouter.ai/api/v1"
)

def clean_ai_json(raw_response: str) -> dict:
    """Attempts to parse AI response safely even if wrapped in ```json ...```."""
    try:
        raw = raw_response.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        elif raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        return json.loads(raw)
    except Exception as e:
        return {"error": f"Invalid JSON from AI: {e}", "raw": raw_response}


def evaluate_resume_for_vacancy(resume: Resume, vacancy: Vacancy) -> dict:
    prompt = (
        "You are an expert recruiter. Evaluate how well this resume fits the job vacancy below.\n"
        "Return the result in valid JSON format with fields:\n"
        "{\n"
        "  \"score\": int (0 to 10),\n"
        "  \"match_summary\": string,\n"
        "  \"strengths\": [list],\n"
        "  \"weaknesses\": [list],\n"
        "  \"advice\": string\n"
        "}\n\n"
        f"Vacancy:\nTitle: {vacancy.title}\nDescription: {vacancy.description}\n\n"
        f"Resume:\nName: {resume.full_name}\nTitle: {resume.title}\n"
        f"Summary: {resume.summary}\nExperience: {resume.experience}\nSkills: {resume.skills}"
    )
    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in recruitment."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return clean_ai_json(response.choices[0].message.content)
    except Exception as e:
        return {"error": f"Error code: 401 - {e}"}


def recommend_jobs_for_resume(resume: Resume, vacancies) -> dict:
    job_text = "\n\n".join(f"{v.title}: {v.description}" for v in vacancies[:10])
    prompt = (
        "You are a smart career assistant. From the following job list, choose the top 3 jobs that best match the resume. "
        "Return response in JSON:\n"
        "{\n"
        "  \"recommendations\": [\n"
        "    {\"title\": \"string\", \"reason\": \"string\"}, ...\n"
        "  ]\n"
        "}\n\n"
        f"Resume:\n{resume.full_name}, {resume.title}\n{resume.summary}\nSkills: {resume.skills}\n\n"
        f"Jobs:\n{job_text}"
    )
    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a career advisor bot."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return clean_ai_json(response.choices[0].message.content)
    except Exception as e:
        return {"error": f"Error code: 401 - {e}"}


def career_advice(resume: Resume) -> dict:
    prompt = (
        "You're a professional career coach. Analyze the resume and give:\n"
        "- skills_to_improve (list)\n"
        "- recommended_courses (list)\n"
        "- suggested_positions (list)\n"
        "- industries (list)\n\n"
        "Return in JSON format like:\n"
        "{\n"
        "  \"skills_to_improve\": [\"...\"],\n"
        "  \"recommended_courses\": [\"...\"],\n"
        "  \"suggested_positions\": [\"...\"],\n"
        "  \"industries\": [\"...\"]\n"
        "}\n\n"
        f"Resume:\nName: {resume.full_name}\nTitle: {resume.title}\n"
        f"Summary: {resume.summary}\nSkills: {resume.skills}\n"
        f"Experience: {resume.experience}\nEducation: {resume.education}"
    )
    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a career coach bot."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.75
        )
        return clean_ai_json(response.choices[0].message.content)
    except Exception as e:
        return {"error": f"Error code: 401 - {e}"}
