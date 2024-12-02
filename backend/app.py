from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from analysis import analyze_data
from pydantic import BaseModel
from typing import Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestBody(BaseModel):
    full_data: Any
    chart_data: Any
    chart_base64: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/process-data")
async def process_data(request_body: RequestBody):
    """
    Endpoint to process the provided data.
    """
    print("-"*50)
    print(request_body.full_data)
    print(request_body.chart_data)
    print("-"*50)
    full_data = request_body.full_data
    chart_data = request_body.chart_data
    chart_base64 = request_body.chart_base64

    data = {
        "full_data": full_data,
        "chart_data": chart_data
    }

    # Call the analysis function
    result = analyze_data(chart_base64, data)

    return result