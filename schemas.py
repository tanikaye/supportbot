from pydantic import BaseModel
from typing import List

class FAQItem(BaseModel):
    question: str
    answer: str

class BusinessOnboardRequest(BaseModel):
    name: str
    email: str
    tone: str = "friendly"
    faqs: List[FAQItem]
