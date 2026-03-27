from fastapi import APIRouter, UploadFile, File, Depends
import pandas as pd
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.pipeline import run_pipeline
from app.services.storage_service import store_dataframe
router = APIRouter()

@router.post("")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        df = pd.read_csv(file.file)

        processed_df = run_pipeline(df)
        store_dataframe(processed_df, db)


        return {
            "status": "success",
            "rows_processed": len(processed_df)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }