import os
import requests

HF_API_KEY = os.getenv("HF_API_KEY")

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

def query_huggingface(prompt: str):
    payload = {"inputs": prompt}

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return "HuggingFace API error"

    result = response.json()

    try:
        return result[0]["generated_text"]
    except:
        return str(result)