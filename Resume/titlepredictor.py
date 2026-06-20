import os
import json
from groq import Groq
from django.conf import settings

current_dir = os.path.dirname(__file__)
category_mapping_path = os.path.join(current_dir, 'category_mapping_rf_sentencebert.json')

with open(category_mapping_path, 'r') as f:
    category_mapping = json.load(f)

CATEGORIES = list(category_mapping.values())
# -> ["AI / Machine Learning", "Backend Development", "Cybersecurity",
#     "DevOps / Cloud Engineering", "Frontend Development",
#     "Mobile Development", "QA / Test Engineering"]

client = Groq(api_key=settings.GROQ_API_KEY)
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")


def jobtitleclassify(phrase):
    categories_str = "\n".join(f"- {c}" for c in CATEGORIES)

    prompt = f"""Classify the following job-related phrase into exactly one of these categories:
{categories_str}

Phrase: "{phrase}"

Respond with only the category name exactly as written above, nothing else."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=20,
    )

    result = response.choices[0].message.content.strip()

    if result not in CATEGORIES:
        for cat in CATEGORIES:
            if cat.lower() in result.lower() or result.lower() in cat.lower():
                return cat
        return result  # fell through with no match — decide what to do here

    return result



def experiencemapper(value):

    if (value <= 2):
        return "basic"
    elif(value <= 5):
        return "intermediate"
    else:
        return "hard"


