import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def call_groq(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Error from Groq !!! "
    
    
def generate_insight_summary(data):
    try:
        categories_str = ", ".join(
            [f"{c['category']} ({c['count']})" for c in data["categories"]]
        )

        sentiments_str = ", ".join(
            [f"{k}: {v}" for k, v in data["sentiments"].items()]
        )

        prompt = f"""
        You are a business analyst.

        Analyze customer support data:

        Total Tickets: {data['total']}
        Categories: {categories_str}
        Sentiments: {sentiments_str}

        Give:
        1. Main issue
        2. Trend
        3. Recommendation

        Keep answer in 3 short lines.
        """

        result = call_groq(prompt)

        return result if result else "No insights generated."

    except Exception as e:
        print("SUMMARY ERROR:", e)
        return "Error generating summary."