from sqlalchemy import text
import json
import uuid


# ---------------- CREATE TABLE ----------------
def create_table(db):
    db.execute(text("""
    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id TEXT PRIMARY KEY,
        message TEXT,
        cleaned_text TEXT,
        category TEXT,
        sentiment TEXT,
        issue TEXT,
        suggested_reply TEXT,
        embedding TEXT
    )
    """))
    db.commit()


# ---------------- STORE SINGLE TICKET ----------------
def store_single_ticket(ticket, db):
    create_table(db)

    ticket_id = ticket.get("ticket_id", str(uuid.uuid4()))

    db.execute(text("""
    INSERT INTO tickets (
        ticket_id,
        message,
        cleaned_text,
        category,
        sentiment,
        issue,
        suggested_reply,
        embedding
    )
    VALUES (
        :ticket_id,
        :message,
        :cleaned_text,
        :category,
        :sentiment,
        :issue,
        :suggested_reply,
        :embedding
    )
    """), {
        "ticket_id": ticket_id,
        "message": ticket.get("message", ""),
        "cleaned_text": ticket.get("cleaned_text", ""),
        "category": ticket.get("category", "Other"),
        "sentiment": ticket.get("sentiment", "Neutral"),
        "issue": ticket.get("issue", ""),
        "suggested_reply": ticket.get("suggested_reply", ""),
        "embedding": json.dumps(ticket.get("embedding", []))
    })

    db.commit()

    return ticket_id


# ---------------- STORE DATAFRAME ----------------
def store_dataframe(df, db):
    create_table(db)

    for _, row in df.iterrows():
        ticket_id = str(uuid.uuid4())

        db.execute(text("""
        INSERT INTO tickets (
            ticket_id,
            message,
            cleaned_text,
            category,
            sentiment,
            issue,
            suggested_reply,
            embedding
        )
        VALUES (
            :ticket_id,
            :message,
            :cleaned_text,
            :category,
            :sentiment,
            :issue,
            :suggested_reply,
            :embedding
        )
        """), {
            "ticket_id": ticket_id,
            "message": row.get("message", ""),
            "cleaned_text": row.get("cleaned_text", ""),
            "category": row.get("category", "Other"),
            "sentiment": row.get("sentiment", "Neutral"),
            "issue": row.get("cleaned_text", "")[:100],
            "suggested_reply": "",
            "embedding": json.dumps(row.get("embedding", []))
        })

    db.commit()


# ---------------- INSIGHTS ----------------
def get_insights(db):
    try:
        total = db.execute(text("SELECT COUNT(*) FROM tickets")).scalar()

        top_issues = db.execute(text("""
        SELECT category, COUNT(*) as count
        FROM tickets
        GROUP BY category
        ORDER BY count DESC
        LIMIT 5
        """)).fetchall()

        sentiment = db.execute(text("""
        SELECT sentiment, COUNT(*) as count
        FROM tickets
        GROUP BY sentiment
        """)).fetchall()

        sample = db.execute(text("""
        SELECT ticket_id, message, category, sentiment
        FROM tickets
        ORDER BY ROWID DESC
        LIMIT 5
        """)).fetchall()

        return {
            "total_tickets": total,
            "top_issues": [dict(row._mapping) for row in top_issues],
            "sentiment_distribution": {
                row[0]: row[1] for row in sentiment
            },
            "sample_tickets": [dict(row._mapping) for row in sample]
        }

    except Exception as e:
        return {"error": str(e)}