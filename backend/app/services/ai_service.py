import os
import requests
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.services.model_loader import embedding_model as embedder
from app.services.llm_service import call_groq

# Embedding model
dim = embedder.get_sentence_embedding_dimension()
index = faiss.IndexFlatL2(dim)

id_map = {}
current_id = 0

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def generate_embedding(text: str):
    return np.array(embedder.encode([text])).astype("float32")

def add_to_faiss(ticket_id, embedding, meta):
    global current_id
    index.add(embedding)
    id_map[current_id] = {"ticket_id": ticket_id, **meta}
    current_id += 1

def ask_ollama(prompt: str):
    try:
        res = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=30
        )
        return res.json().get("response", "")
    except:
        return ""

# Lightweight logic (reduce LLM calls)


def simple_sentiment(text):
    text = text.lower()

    if any(x in text for x in ["bad", "worst", "angry", "hate", "frustrated", "delay", "issue", "problem"]):
        return "Negative"
    
    if any(x in text for x in ["good", "great", "happy", "satisfied", "awesome"]):
        return "Positive"

    return "Neutral"


# ---------------- CATEGORY (ENHANCED RULE-BASED) ----------------
def simple_category(text: str) -> str:
    text = text.lower()

    category_keywords = {
        "Refund": [
            "refund", "money back", "return", "returned", "cancel order",
            "cancellation", "not refunded", "refund not processed"
        ],
        "Delivery": [
            "delivery", "delayed", "late", "not delivered", "shipment",
            "shipping", "courier", "arrived late", "delay"
        ],
        "Payment": [
            "payment", "charged", "transaction", "upi", "credit card",
            "debit card", "failed payment", "double charged", "billing"
        ],
        "Technical": [
            "error", "bug", "issue", "not working", "crash",
            "failed", "problem", "app issue", "system error"
        ]
    }

    # Priority-based matching
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in text:
                return category

    return "Other"




def analyze_ticket_ai(text: str, use_llm: bool = True):

    # -------- FAST BASE --------
    category = simple_category(text)
    sentiment = simple_sentiment(text)

    issue = text[:100]

    # -------- LLM ENHANCEMENT --------
    if use_llm:
        try:
            # Issue extraction
            issue_prompt = f"""
            Extract the main customer issue in ONE short sentence.

            Text: {text}
            """
            issue_llm = call_groq(issue_prompt)
            if issue_llm:
                issue = issue_llm

        except:
            pass

    # -------- ALWAYS LLM FOR REPLY --------
    reply_prompt = f"""
    Generate a professional customer support reply but should be short and sweet.

    Customer issue:
    {text}
    """

    reply = call_groq(reply_prompt)

    return {
        "category": category,
        "sentiment": sentiment,
        "issue": issue,
        "suggested_reply": reply or "We are looking into it."
    }