from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    tone = Column(String, default="friendly")
    faqs = relationship("FAQEntry", back_populates="business")

class FAQEntry(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    embedding = Column(Text)  # we’ll store embeddings as JSON strings for now
    business_id = Column(Integer, ForeignKey("businesses.id"))
    business = relationship("Business", back_populates="faqs")
