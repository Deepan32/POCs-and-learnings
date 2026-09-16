from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Float, Integer
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class ProductService(BaseModel):
    __tablename__ = "product_services"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, default="General")
    price = Column(Float, nullable=True, default=0.0)
    currency = Column(String(10), default="INR", nullable=False)
    image_url = Column(String(500), nullable=True)
    sku = Column(String(100), nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)
    tags = Column(String(255), nullable=True)
    order_index = Column(Integer, default=0, nullable=False)

    workspace = relationship("Workspace", back_populates="products")
