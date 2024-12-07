import pandas as pd
import requests
import json
import base64
from dotenv import load_dotenv
import os

# load the environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_KEY")

def check_truncated_axes(data: pd.DataFrame) -> str:
    try:
        data["Value"] = pd.to_numeric(data["Value"], errors='coerce')
        data = data.dropna(subset=["Value"])
        if data.empty:
            # If no valid numeric data, skip this check
            return ""
        min_value = data["Value"].min()
        if min_value > 0:
            return "Warning: The axis may be truncated, potentially misleading the viewer."
        return "Axes appear properly scaled."
    except Exception:
        # If any error occurs, skip reporting
        return ""

def check_cherry_picking(sheet_data: pd.DataFrame, chart_data: pd.DataFrame) -> str:
    try:
        # Ensure both datasets are numeric for comparison
        sheet_data["Value"] = pd.to_numeric(sheet_data["Value"], errors='coerce')
        chart_data["Value"] = pd.to_numeric(chart_data["Value"], errors='coerce')
        sheet_data = sheet_data.dropna(subset=["Value"])
        chart_data = chart_data.dropna(subset=["Value"])

        if sheet_data.empty or chart_data.empty:
            # If no valid numeric data, skip this check
            return ""

        sheet_range = (sheet_data["Value"].min(), sheet_data["Value"].max())
        chart_range = (chart_data["Value"].min(), chart_data["Value"].max())

        chart_trend = "upward" if chart_data["Value"].iloc[-1] > chart_data["Value"].iloc[0] else "downward"
        sheet_trend = "upward" if sheet_data["Value"].iloc[-1] > sheet_data["Value"].iloc[0] else "downward"

        if chart_range[0] > sheet_range[0] or chart_range[1] < sheet_range[1]:
            return "Warning: The chart data may be cherry-picked, not reflecting the full dataset."

        if chart_trend != sheet_trend:
            return "Warning: The chart data may be cherry-picked, as the overall trend differs from the full dataset."

        return "Data appears representative of the entire dataset."
    except Exception:
        # If any error occurs, skip reporting
        return ""

def initial_checks(chart_data: pd.DataFrame, full_data: pd.DataFrame) -> dict:
    results = {
        "axis_check": "",
        "cherry_picking_check": ""
    }
    # Perform checks only if data is present and valid
    if chart_data is not None and not chart_data.empty:
        results["axis_check"] = check_truncated_axes(chart_data)
    if full_data is not None and not full_data.empty and chart_data is not None and not chart_data.empty:
        results["cherry_picking_check"] = check_cherry_picking(full_data, chart_data)
    return results

def call_gpt4_api(chart_img_base64: str, sheet_data: pd.DataFrame, chart_data: pd.DataFrame, initial_analysis: dict) -> str:
    # Create a robust prompt for GPT-4
    # No markdown or special formatting, just text.
    prompt = f"""
You are an expert in data visualization ethics and aesthetics. You have a chart image and optionally some chart data and a full dataset.

Initial analysis results:
Axis Check: {initial_analysis.get('axis_check', '')}
Cherry Picking Check: {initial_analysis.get('cherry_picking_check', '')}

Chart Data: {chart_data.to_json() if chart_data is not None else "No Chart Data Provided"}
Sheet Data: {sheet_data.to_json() if sheet_data is not None else "No Full Data Provided"}
Chart: see attached image

Your task is to provide constructive feedback to the chart's creator. The goal is to help them improve the chart so it does not mislead viewers, and so it adheres to best practices in ethical and aesthetic data visualization. Consider issues like truncated axes, cherry-picking of data, lack of context, missing data points, deceptive scales, confusing 3D effects, poor color choices, overcomplexity, missing labels, unclear legends, data smoothing that obscures important variation, selective highlighting that distorts the message, data embellishments, manipulations of time intervals, baseline omissions, rounding issues, sampling biases, inappropriate visual metaphors, and any form of chartjunk that detracts from clarity.

If the chart is missing certain data or you cannot confirm certain issues due to incomplete information, focus on general best practices and potential pitfalls. The output should be given directly to the creator, guiding them on how to avoid any ethical or misleading practices and how to improve aesthetics, clarity, and honesty in their data visualization.

Do not use markdown or formatting that requires further rendering. Keep the language direct, clear, and instructive. Do not reference the fact that the user is reading this prompt or that you are an AI. Simply offer advice and observations. If initial checks are empty or if you have no data to analyze, provide general recommendations.
"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    # Construct payload
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{chart_img_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_json = response.json()

    # Attempt to return the model's response
    try:
        return response_json['choices'][0]['message']['content']
    except:
        # If we can't parse a correct response, return something generic
        return "No additional feedback could be generated, response: " + str(response_json)

def analyze_data(chart_b64: str, data: dict) -> str:
    # Chart image is required. Data may be optional.
    full_data_df = None
    chart_data_df = None

    # Attempt to create DataFrames if provided
    try:
        if "full_data" in data and data["full_data"]:
            full_data_df = pd.DataFrame(data["full_data"])
    except:
        pass

    try:
        if "chart_data" in data and data["chart_data"]:
            chart_data_df = pd.DataFrame(data["chart_data"])
    except:
        pass

    # Perform initial checks only if dataframes are present
    try:
        initial_analysis = initial_checks(chart_data_df, full_data_df)
    except:
        # If checks fail, just set them empty
        initial_analysis = {"axis_check": "", "cherry_picking_check": ""}

    # If no data analysis is possible, we can still provide general advice via GPT-4.
    # But only call GPT if we have a chart image.
    if not chart_b64:
        return "No chart image provided. Unable to provide analysis."

    # Call GPT-4 API even if data is missing; it can give general advice.
    try:
        api_response = call_gpt4_api(chart_b64, full_data_df, chart_data_df, initial_analysis)
        return api_response
    except Exception as e:
        # If GPT call fails, return a generic message
        print(f"Error in GPT-4 API call: {e}")
        return "Could not provide additional feedback at this time."