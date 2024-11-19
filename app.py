from fastapi import FastAPI
from analysis import analyze_data
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

class DataSchema(BaseModel):
    Date: Dict[str, str]
    Value: Dict[str, int]

class RequestBody(BaseModel):
    full_data: DataSchema
    chart_data: DataSchema
    chart_base64: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/process-data")
async def process_data(request_body: RequestBody):
    """
    Endpoint to process the provided data.
    """
    full_data = request_body.full_data
    chart_data = request_body.chart_data
    chart_base64 = request_body.chart_base64

    data = {
        "full_data": full_data.model_dump(),
        "chart_data": chart_data.model_dump()
    }

    # Call the analysis function
    result = analyze_data(chart_base64, data)

    return result