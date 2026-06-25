# step1:Setup FastAPI backend
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

#step2: Receive and validate request from Frontend
class Query(BaseModel):
    message: str 




@app.post("/ask")
async def ask(query: Query):
    #ai agent
 
#step3:  Send response to the frontend
    
    return "This is the response"


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)