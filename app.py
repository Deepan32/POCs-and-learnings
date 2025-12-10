# app.py
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- Database Setup ---
DATABASE_URL = "sqlite:///./meta_ads.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    budget = Column(Float)
    status = Column(String)
    audience = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Models ---
class CampaignCreate(BaseModel):
    id: str
    name: str
    budget: float
    status: str
    audience: Optional[str] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    budget: Optional[float] = None
    status: Optional[str] = None
    audience: Optional[str] = None

# --- Router Setup ---
router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

@router.get("/", response_model=List[CampaignCreate])
def list_campaigns(db: Session = Depends(get_db)):
    return db.query(Campaign).all()

@router.post("/", response_model=CampaignCreate)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    existing = db.query(Campaign).filter(Campaign.id == campaign.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Campaign ID already exists")
    new_campaign = Campaign(**campaign.dict())
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    return new_campaign

@router.get("/{campaign_id}", response_model=CampaignCreate)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.put("/{campaign_id}", response_model=CampaignCreate)
def update_campaign(campaign_id: str, update: CampaignUpdate, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(campaign, field, value)
    db.commit()
    db.refresh(campaign)
    return campaign

@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    db.delete(campaign)
    db.commit()
    return {"detail": "Campaign deleted"}

@router.get("/{campaign_id}/analytics")
def campaign_analytics(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {
        "ctr": 0.045,
        "impressions": 12000,
        "spend": campaign.budget * 0.1
    }

# --- FastAPI App ---
app = FastAPI(title="Meta Ads MCP Server")
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Meta Ads MCP Server is running 🚀"}
