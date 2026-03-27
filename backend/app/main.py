from fastapi import FastAPI
from app.api import upload, tickets, insights


app = FastAPI(title="CustomerPulse AI")

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
app.include_router(insights.router, prefix="/insights", tags=["Insights"])



@app.get("/")
def root():
    return {"message": "CustomerPulse AI is running !!!!"}