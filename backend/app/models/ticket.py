from sqlalchemy import Column, String, Float, Text
from app.db.database import Base

class TicketDB(Base):
    __tablename__ = "tickets"

    ticket_id = Column(String, primary_key=True, index=True)
    message = Column(Text)
    cleaned_text = Column(Text)
    category = Column(String)
    sentiment = Column(String)
    issue = Column(Text)
    suggested_reply = Column(Text)
    product = Column(String)
    order_value = Column(Float)
    embedding = Column(Text)   