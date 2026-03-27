from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./test.db"  # change to postgres later

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()



def create_tables():
    from app.models.ticket import TicketDB 
    Base.metadata.create_all(bind=engine)


#  CALL IT IMMEDIATELY
create_tables()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()