from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Affiliate(Base):
    __tablename__ = "affiliates"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    network = Column(String(120), nullable=False)
    tracking_url = Column(String(500), nullable=False)

    product = relationship("Product", back_populates="affiliates")
