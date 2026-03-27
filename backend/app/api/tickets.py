from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.pipeline import process_single_ticket

router = APIRouter()

@router.post("")
def create_ticket(data: dict, db: Session = Depends(get_db)):
    ticket = process_single_ticket(data, db)
    return ticket