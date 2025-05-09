from openai import OpenAI
from resumes.models import Resume

client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)


def find_best_resumes_for_vacancy(vacancy, resumes):
    resumes_text = "\n\n".join([
        f"{r.full_name}, {r.title}, {r.summary}, {r.skills}, {r.experience}" for r in resumes
    ])

    prompt = (
        "Ты HR-специалист. У тебя есть вакансия и список резюме. "
        "Выбери топ-3 лучших резюме, которые наиболее соответствуют требованиям вакансии. "
        "Объясни для каждого кандидата, почему он подходит. "
        "Верни ответ в виде списка: имя + причина.\n\n"
        f"Вакансия: {vacancy.title}\n{vacancy.description}\n\n"
        f"Резюме:\n{resumes_text}"
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты опытный HR."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}
