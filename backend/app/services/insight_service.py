from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.ticket import TicketDB
from app.services.llm_service import generate_insight_summary

def get_insights(db: Session):
    try:
        # ---------------- TOTAL ----------------
        total = db.query(TicketDB).count()

        # ---------------- SENTIMENT ----------------
        sentiments_raw = db.query(
            TicketDB.sentiment,
            func.count()
        ).group_by(TicketDB.sentiment).all()

        sentiments = {
            sentiment: count
            for sentiment, count in sentiments_raw
        }

        # ---------------- CATEGORY ----------------
        categories_raw = db.query(
            TicketDB.category,
            func.count()
        ).group_by(TicketDB.category).all()

        categories = [
            {"category": category, "count": count}
            for category, count in categories_raw
        ]

        # ---------------- REVENUE ----------------
        revenue = db.query(func.sum(TicketDB.order_value)).scalar() or 0

        # ---------------- SAMPLE TICKETS ----------------
        sample = db.query(TicketDB).order_by(TicketDB.ticket_id.desc()).limit(5).all()

        sample_tickets = [
            {
            "ticket_id": t.ticket_id,
            "message": t.message,
            "category": t.category,
            "sentiment": t.sentiment,
            "suggested_reply": t.suggested_reply 
        }
            for t in sample
        ]
        
        summary = generate_insight_summary({
        "total": total,
        "categories": categories,
        "sentiments": sentiments
        })

        return {
            "total_tickets": total,
            "sentiment_distribution": sentiments,
            "category_distribution": categories,
            "revenue": revenue,
            "sample_tickets": sample_tickets, 
            "summary": summary
        }

    except Exception as e:
        return {"error": str(e)}