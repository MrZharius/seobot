# writer.py
import openai
from config import *

openai.api_key = "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"

def build_prompt(article_type, keywords, length, style, lang):
    base = {
        "ad": "Напиши рекламную статью",
        "seo": "Напиши SEO-текст",
        "congrats": "Напиши поздравление",
    }
    styles = {
        "sell": "в продающем стиле",
        "friendly": "в дружелюбном стиле",
        "info": "в информационном стиле",
    }
    if lang == "en":
        base = {
            "ad": "Write an advertising article",
            "seo": "Write an SEO-optimized text",
            "congrats": "Write a congratulatory message",
        }
        styles = {
            "sell": "in a selling tone",
            "friendly": "in a friendly tone",
            "info": "in an informational tone",
        }

    prompt = f"{base.get(article_type, '')} на тему: {keywords}, {styles.get(style, '')}. Объем: около {length} символов."
    return prompt

async def generate_article(user_data):
    prompt = build_prompt(
        user_data["type"],
        user_data["keywords"],
        user_data["length"],
        user_data["style"],
        user_data.get("lang", DEFAULT_LANGUAGE)
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        article = response.choices[0].message["content"]
        return article
    except Exception as e:
        return f"Произошла ошибка при генерации текста: {e}"
