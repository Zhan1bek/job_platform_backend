from openai import OpenAI

from companies.models import Vacancy

client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

def evaluate_resume_for_vacancy(resume, vacancy: Vacancy) -> str:
    prompt = (
        "Ты HR-эксперт. Проанализируй, насколько резюме соответствует вакансии. "
        "Верни JSON с полями: score (0-10), strengths, weaknesses, advice.\n\n"
        f"Вакансия:\n{vacancy.title}\n{vacancy.description}\n\n"
        f"Резюме:\n{resume.full_name}, {resume.title}\n"
        f"{resume.summary}\nОпыт: {resume.experience}\nНавыки: {resume.skills}\n"
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты HR-эксперт и карьерный консультант."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}


def recommend_jobs_for_resume(resume, all_vacancies) -> str:
    vacancy_list = "\n\n".join(
        f"{v.title}:\n{v.description}" for v in all_vacancies[:10]
    )

    prompt = (
        "Ты карьерный помощник. Проанализируй резюме и порекомендуй топ-3 вакансии из списка. "
        "Объясни, почему они подходят. Ответ в виде списка: вакансия + причина.\n\n"
        f"Резюме:\n{resume.full_name}, {resume.title}\n{resume.summary}\n{resume.skills}\n\n"
        f"Вакансии:\n{vacancy_list}"
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты ассистент по карьерному развитию."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}


def career_advice(resume) -> str:
    prompt = (
        "Ты карьерный коуч. Проанализируй резюме и предложи конкретные шаги для улучшения "
        "карьерных перспектив: навыки, курсы, позиции, индустрии. Верни список рекомендаций.\n\n"
        f"{resume.full_name}, {resume.title}\n"
        f"{resume.summary}\nНавыки: {resume.skills}\nОпыт: {resume.experience}\nОбразование: {resume.education}"
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты карьерный коуч."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9
        )
        return response.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}