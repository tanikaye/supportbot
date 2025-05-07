# FastAPI app setup and imports
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import openai
from sqlalchemy.orm import Session
from schemas import BusinessOnboardRequest  # Pydantic model for onboarding data
from database import SessionLocal  # DB session connection
from models import Business, FAQEntry  # SQLAlchemy models for tables
import json  # Used to convert embedding list to string
from utils import cosine_similarity


# === Embedding function ===
def get_embedding(text: str) -> str:
    """
    Calls OpenAI's Embeddings API and returns a JSON string of the vector.
    """
    try:
        response = openai.Embedding.create(
            input=[text],
            model="text-embedding-ada-002"
        )
        vector = response['data'][0]['embedding']
        print(f"✅ Generated embedding for: '{text[:30]}...' → First 3 values: {vector[:3]}")
        return json.dumps(vector)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")


# === Load environment variables and API key ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")  # Get your OpenAI key from .env

app = FastAPI()

# === Simple chatbot endpoint ===

class ChatRequest(BaseModel):
    message: str  # incoming message from frontend
    business_id: int
    similarity_threshold: float = 0.80

@app.get("/")
def read_root():
    return {"message": "SupportBot API is running"}  # health check route

# === Dependency for DB session ===
def get_db():
    db = SessionLocal()  # creates a database session
    try:
        yield db
    finally:
        db.close()

@app.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    user_message = request.message
    threshold = request.similarity_threshold
    user_embedding = get_embedding(user_message)

    faqs = db.query(FAQEntry).filter(FAQEntry.business_id == request.business_id).all()

    best_faq = None
    best_score = -1

    for faq in faqs:
        if faq.embedding is None:
            continue
        faq_embedding = json.loads(faq.embedding)
        score = cosine_similarity(json.loads(user_embedding), faq_embedding)
        if score > best_score:
            best_score = score
            best_faq = faq

    if best_score >= threshold:
        system_prompt = f"You are a support assistant. Use this business FAQ to help answer questions:\n\nQ: {best_faq.question}\nA: {best_faq.answer}"
        matched_question = best_faq.question
        matched_answer = best_faq.answer
    else:
        system_prompt = "You are a support assistant. The user asked something, but no relevant FAQ was found. Respond helpfully but briefly."
        matched_question = best_faq.question if best_faq else None
        matched_answer = None

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message["content"]
        return {
            "reply": reply,
            "matched_faq": matched_question,
            "score": best_score,
            "used_faq": bool(score > threshold)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# === Onboard new business and store FAQ entries ===
@app.post("/onboard")
def onboard_business(data: BusinessOnboardRequest, db: Session = Depends(get_db)):
    """
    Stores a business's info and their FAQ entries (with embeddings) in the DB.
    """
    # 1. Save the business info to the database
    business = Business(name=data.name, email=data.email, tone=data.tone)
    db.add(business)
    db.commit()
    db.refresh(business)  # now business.id is populated

    # 2. Loop through each FAQ and save it with an embedding
    for faq in data.faqs:
        embedding = get_embedding(faq.answer)  # generate vector from the answer
        entry = FAQEntry(
            question=faq.question,
            answer=faq.answer,
            embedding=embedding,  # already JSON string
            business_id=business.id  # link this FAQ to the business
        )
        db.add(entry)

    db.commit()  # save all FAQ entries

    return {"message": "Business onboarded successfully", "business_id": business.id}
