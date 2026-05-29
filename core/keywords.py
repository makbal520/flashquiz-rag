from openai import OpenAI
import os
import json
#from core.client import get_client

client = OpenAI(
        api_key="sk-zw2iqM_gBO6gjwKqbuXy1g",  
        base_url="http://10.162.13.14:4000"  
    )#get_client()


def extract_keywords(vectorstore, num_keywords: int = 10) -> list:
    results = vectorstore.similarity_search("main concepts topics knowledge", k=5)
    context = "\n\n".join([r.page_content[:300] for r in results])

    prompt = f"""Analyze this document content and extract the {num_keywords} most important knowledge topics or concepts.
Return ONLY a JSON array of strings, nothing else. Example: ["Gradient Descent", "Backpropagation", "CNN"]

Document content:
{context}"""

    response = client.chat.completions.create(
        model="gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    # Debug: print full response to see what came back
    content = response.choices[0].message.content
    print(f"DEBUG keywords response: {content}")  

    # Guard against None
    if content is None:
        print("WARNING: model returned None, using fallback keywords")
        return ["Topic 1", "Topic 2", "Topic 3"]

    raw = content.strip()

    # Handle case where model wraps in ```json ... ```
    if "```" in raw:
        raw = raw.split("```")[1].replace("json", "").strip()

    try:
        keywords = json.loads(raw)
        return keywords
    except json.JSONDecodeError:
        print(f"WARNING: could not parse JSON: {raw}")
        # Fallback: split by comma if model returned plain text
        return [k.strip().strip('"') for k in raw.strip("[]").split(",")]