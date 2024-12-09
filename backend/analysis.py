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
    except Exception as e:
        print(f"Error in axis check: {e}")
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
    except Exception as e:
        # If any error occurs, skip reporting
        print(f"Error in cherry-picking check: {e}")
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

def call_gpt4_api(chart_img_base64: str, sheet_data: pd.DataFrame, chart_data: pd.DataFrame, initial_analysis: dict, additional_info: str) -> str:
    # I know this section is a mess of if statements, don't kill me.
    prompt = "You are an expert in data visualization ethics and aesthetics. Attached is a chart that requires your feedback"

    if initial_analysis.get('axis_check', '') != '' or initial_analysis.get('cherry_picking_check', '') != '':
        prompt += "\n\nInitial analysis results:"
    if initial_analysis.get('axis_check', '') != '':
        prompt += f"\nAxis Check: {initial_analysis.get('axis_check', '')}"
    if initial_analysis.get('cherry_picking_check', '') != '':
        prompt += f"\nCherry Picking Check: {initial_analysis.get('cherry_picking_check', '')}"

    if chart_data is not None:
        prompt += f"\nchart_data: {chart_data.to_json()}"

    if sheet_data is not None:
        prompt += f"\nsheet_data: {sheet_data.to_json()}\n"
        
    prompt += """
    Chart: see attached image

    Your task is to provide constructive feedback to the chart's creator. The goal is to help them improve the chart so it does not mislead viewers, and so it adheres to best practices in ethical and aesthetic data visualization. Consider issues like truncated axes, cherry-picking of data, lack of context, missing data points, deceptive scales, confusing 3D effects, poor color choices, overcomplexity, missing labels, unclear legends, data smoothing that obscures important variation, selective highlighting that distorts the message, data embellishments, manipulations of time intervals, baseline omissions, rounding issues, sampling biases, inappropriate visual metaphors, and any form of chartjunk that detracts from clarity.

    If the chart is missing certain data or you cannot confirm certain issues due to incomplete information, focus on general best practices and potential pitfalls. The output should be given directly to the creator, guiding them on how to avoid any ethical or misleading practices and how to improve aesthetics, clarity, and honesty in their data visualization.

    Do not use markdown or formatting that requires further rendering. Keep the language direct, clear, and instructive. Do not reference the fact that the user is reading this prompt or that you are an AI. Simply offer advice and observations. If initial checks are empty or if you have no data to analyze, provide general recommendations.

    Seperate your feedback into two sections - one for ethical considerations and one for aesthetic considerations. Provide at least 3 points for each section. If there are any that overlap, only mention it in the ethical considerations section, but note that it also applies to aesthetics and highlight the connection. 

    If no chart data is provided or the full data isn't provided, don't mention anything about not having the data, just provide general advice based on the chart image alone.

    Again, it is imperative that you just provide a plain-text response. Do not include any markdown or formatting that requires further rendering. Keep the language direct, clear, and instructive. 
    For example, do not include **bold** or *italic* text or any other formatting that requires further rendering.
    """
    if additional_info:
        prompt += f"\nAdditional Information from User: {additional_info}"

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

    print("Calling API with payload:")
    # print payload for debugging but don't log the chart image base64 as it's too long
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_json = response.json()
    to_print = payload.copy()
    to_print['messages'][0]['content'][1]['image_url']['url'] = f"data:image/jpeg;base64, {chart_img_base64[:50]}, {len(chart_img_base64)} bytes"
    print(json.dumps(to_print, indent=2))
    print("Received API response:")
    print(json.dumps(response_json, indent=2))
    # Attempt to return the model's response
    try:
        return response_json['choices'][0]['message']['content']
    except Exception as e:
        # If we can't parse a correct response, return something generic
        return "No additional feedback could be generated, response: " + str(response_json) + " error: " + str(e)

def analyze_data(chart_b64: str, data: dict, additional_info: str) -> str:
    # Chart image is required. Data may be optional.
    full_data_df = None
    chart_data_df = None

    # Attempt to create DataFrames if provided
    try:
        if "full_data" in data and data["full_data"]:
            full_data_df = pd.DataFrame(data["full_data"])
    except Exception as e:
        print(f"Error creating full data DataFrame: {e}")

    try:
        if "chart_data" in data and data["chart_data"]:
            chart_data_df = pd.DataFrame(data["chart_data"])
    except Exception as e:
        print(f"Error creating chart data DataFrame: {e}")

    # Perform initial checks only if dataframes are present
    try:
        initial_analysis = initial_checks(chart_data_df, full_data_df)
    except Exception as e:
        print(f"Error in initial checks: {e}")
        # If checks fail, just set them empty
        initial_analysis = {"axis_check": "", "cherry_picking_check": ""}

    # If no data analysis is possible, we can still provide general advice via GPT-4.
    # But only call GPT if we have a chart image.
    if not chart_b64:
        return "No chart image provided. Unable to provide analysis."

    # Call GPT-4 API even if data is missing; it can give general advice.
    try:
        api_response = call_gpt4_api(chart_b64, full_data_df, chart_data_df, initial_analysis, additional_info)
        return api_response
    except Exception as e:
        # If GPT call fails, return a generic message
        print(f"Error in GPT-4 API call: {e}")
        return "Could not provide additional feedback at this time."