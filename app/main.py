from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import tickets

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with Vercel domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets.router)

@app.get("/")
def root():
    return {"message": "Ticket Manager API is running"}
