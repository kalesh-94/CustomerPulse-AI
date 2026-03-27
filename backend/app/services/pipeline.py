from app.utils.cleaning import clean_dataframe, clean_text
from app.services.embedding_service import generate_embeddings
from app.services.storage_service import store_single_ticket
from app.services.ai_service import simple_sentiment, analyze_ticket_ai, simple_category
import uuid
import numpy as np
import faiss




# ---------------- BATCH PIPELINE ----------------
def run_pipeline(df, db=None):
    # Step 1: Cleaning
    df = clean_dataframe(df)

    # Step 2: Basic enrichment
    df["category"] = df["cleaned_text"].apply(simple_category)
    df["sentiment"] = df["cleaned_text"].apply(simple_sentiment)

    # Step 3: Embeddings
    embeddings = generate_embeddings(df["cleaned_text"].tolist())
    df["embedding"] = embeddings.tolist()

    # Step 4: FAISS indexing
    emb_np = np.array(df["embedding"].tolist()).astype("float32")
    index = faiss.IndexFlatL2(emb_np.shape[1])
    index.add(emb_np)
    faiss.write_index(index, "faiss_index.bin")

    # Step 5: OPTIONAL DB storage (if db provided)
    if db:
        for _, row in df.iterrows():
            ticket = {
                "message": row.get("message", ""),
                "cleaned_text": row["cleaned_text"],
                "category": row["category"],
                "sentiment": row["sentiment"],
                "issue": row.get("cleaned_text", "")[:100],
                "suggested_reply": "",
                "embedding": row["embedding"]
            }
            store_single_ticket(ticket, db)

    return df


# ---------------- REAL-TIME PIPELINE ----------------
def process_single_ticket(ticket_data, db):
    message = ticket_data.get("message", "")

    if not message:
        return {"status": "error", "message": "Empty message"}

    # Step 1: Clean
    cleaned = clean_text(message)

    # Step 2: Embedding
    embedding = generate_embeddings([cleaned])[0].tolist()

    # Step 3: AI Analysis (HYBRID)
    ai_data = analyze_ticket_ai(cleaned)  # safe + optimized
    t_id = str(uuid.uuid4())
    # Step 4: Prepare ticket
    ticket = {
        "ticket_id": t_id,
        "message": message,
        "cleaned_text": cleaned,
        "category": ai_data["category"],
        "sentiment": ai_data["sentiment"],
        "issue": ai_data["issue"],
        "suggested_reply": ai_data["suggested_reply"],
        "embedding": embedding
    }

    # Step 5: Store in DB
    

    ticket_id = store_single_ticket(ticket, db)

    return {
    "status": "success",
    "ticket_id": ticket_id,
    "category": ai_data["category"],
    "sentiment": ai_data["sentiment"], 
    "suggested_reply": ai_data["suggested_reply"]
    }