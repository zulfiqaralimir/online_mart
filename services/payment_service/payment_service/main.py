""" Payment Service for Musa's Online Mart """
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Payment Service"}
