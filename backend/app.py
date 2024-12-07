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
    full_data: Any = None
    chart_data: Any = None
    additional_info: Any = None
    chart_base64: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/process-data")
async def process_data(request_body: RequestBody):
    # Only chart_base64 is truly required. full_data and chart_data may be absent or empty.
    full_data = request_body.full_data if request_body.full_data else {}
    chart_data = request_body.chart_data if request_body.chart_data else {}
    additional_info = request_body.additional_info if request_body.additional_info else None
    chart_base64 = request_body.chart_base64

    data = {
        "full_data": full_data,
        "chart_data": chart_data
    }

    print("Received data:")
    print(data)
    print("Received chart base64:")
    print(chart_base64[:50])
    result = analyze_data(chart_base64, data, additional_info)
    return result