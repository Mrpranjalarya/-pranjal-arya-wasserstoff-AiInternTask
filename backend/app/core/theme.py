from openai import OpenAI
from app.config import settings

import openai
openai.api_key = settings.OPENAI_API_KEY

def detect_themes_from_responses(responses: list[str]) -> list[str]:
    prompt = (
        "You are a research assistant. Given the following document-based answers, "
        "identify coherent themes (e.g., regulations, fraud, compliance). "
        "List the themes in bullet points.\n\n"
    )

    prompt += "\n".join([f"Document Answer: {resp}" for resp in responses])
    prompt += "\n\nReturn just a bullet list of themes."

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    content = completion.choices[0].message.content
    return content.strip().split("\n")
