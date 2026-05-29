from openai import OpenAI
import os
from core.client import get_client
client = get_client()

def evaluate_answer(question: str, user_answer: str, correct_answer: str, vectorstore) -> dict:
    # Get extra context from document
    results = vectorstore.similarity_search(question, k=2)
    context = "\n\n".join([r.page_content[:200] for r in results])

    prompt = f"""You are a strict but fair academic evaluator.

Question: {question}
Model Answer: {correct_answer}
Document Context: {context}
Student Answer: {user_answer}

Evaluate the student's answer. Respond in this exact JSON format:
{{
  "score": <number 1-10>,
  "feedback": "<2-3 sentences: what they got right and what's missing>",
  "model_answer": "<clear concise model answer based on document>"
}}"""

    response = client.chat.completions.create(
        model="gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    import json
    raw = response.choices[0].message.content.strip()
    return json.loads(raw)