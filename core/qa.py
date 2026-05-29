from openai import OpenAI
import os

from core.client import get_client
client = get_client()

def ask_document(question: str, vectorstore, chat_history: list = []) -> dict:
    results = vectorstore.similarity_search(question, k=2)
    context = "\n\n".join([r.page_content[:300] for r in results])

    messages = [
        {"role": "system", "content": "You are a study assistant. Answer based ONLY on the provided content. If the answer is not in the content, say 'I could not find this in the document'."}
    ]
    messages.extend(chat_history)
    messages.append({
        "role": "user",
        "content": f"Content:\n{context}\n\nQuestion: {question}"
    })

    response = client.chat.completions.create(
        model="gpt-oss-120b",
        messages=messages,
        temperature=0,
    )

    answer = response.choices[0].message.content
    chat_history.append({"role": "user", "content": question})
    chat_history.append({"role": "assistant", "content": answer})

    return {"answer": answer, "chat_history": chat_history}