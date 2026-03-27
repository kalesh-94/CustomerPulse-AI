from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.insight_service import get_insights

router = APIRouter()

@router.get("")
def insights(db: Session = Depends(get_db)):
    return get_insights(db)