from openai import OpenAI
import os
import time

from core.client import get_client
client = get_client()

def generate_flashcard(topic: str, vectorstore, num_questions: int = 3) -> str:
    results = vectorstore.similarity_search(topic, k=2)
    context = "\n\n".join([r.page_content[:300] for r in results])

    prompt = f"""Based on this content, generate {num_questions} flashcards.

Content:
{context}

Format:
Q: [question]
A: [answer]

Topic focus: {topic}"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "You are a study assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            if "rate" in str(e).lower() and attempt < 2:
                print(f"Rate limit hit, waiting 30 seconds... (attempt {attempt + 1}/3)")
                time.sleep(30)
            else:
                raise e
            

