from fastapi import FastAPI
from analysis import analyze_data

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/analyze_data")
def analyze_data_endpoint(chart_img_path: str):
    return analyze_data(chart_img_path)