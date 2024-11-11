import pandas as pd
import requests
import json
import tkinter as tk
from tkinter import messagebox
import base64
from dotenv import load_dotenv
import os

# load the environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_KEY")


# Initialize the Tkinter root
tk.Tk().withdraw()

# Function to check for truncated axes
def check_truncated_axes(data):
    # Convert the "Value" column to numeric, coercing errors to NaN, and drop NaN values
    data["Value"] = pd.to_numeric(data["Value"], errors='coerce').dropna()
    min_value = data["Value"].min()
    if min_value > 0:
        return "Warning: The axis may be truncated, which could mislead viewers."
    return "Axes appear to be properly scaled."

# Function to check for cherry-picking (omitted data)
def check_cherry_picking(sheet_data, chart_data):
    # Ensure both datasets are numeric for comparison
    sheet_data["Value"] = pd.to_numeric(sheet_data["Value"], errors='coerce').dropna()
    chart_data["Value"] = pd.to_numeric(chart_data["Value"], errors='coerce').dropna()
    
    sheet_range = (sheet_data["Value"].min(), sheet_data["Value"].max())
    chart_range = (chart_data["Value"].min(), chart_data["Value"].max())
    
    if chart_range[0] > sheet_range[0] or chart_range[1] < sheet_range[1]:
        return "Warning: The chart data may be cherry-picked, not reflecting the full dataset."
    return "Data appears representative of the entire dataset."

# Read the exported data
def load_data():
    with open('data/data_for_analysis.txt', 'r') as file:
        lines = file.readlines()

    # Parse chart and sheet data from the file
    chart_data_start = lines.index("Chart Data:\n") + 1
    full_data_start = lines.index("Full Data from Same Columns:\n") + 1
    
    # Extract and format chart data
    chart_data_lines = lines[chart_data_start:full_data_start-2]
    chart_data = pd.DataFrame(
        [line.strip().split('\t') for line in chart_data_lines],
        columns=["Date", "Value"]
    )

    # Extract and format full sheet data
    full_data_lines = lines[full_data_start:]
    full_data = pd.DataFrame(
        [line.strip().split('\t') for line in full_data_lines],
        columns=["Date", "Value"]
    )

    # Convert "Value" columns to numeric, with errors coerced to NaN, and drop NaN rows
    chart_data["Value"] = pd.to_numeric(chart_data["Value"], errors='coerce').dropna()
    full_data["Value"] = pd.to_numeric(full_data["Value"], errors='coerce').dropna()

    return full_data, chart_data

# Function to call GPT-4 API for deeper analysis
def call_gpt4_api(chart_img_path, sheet_data, chart_data, initial_analysis):
    def encode_image(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    
    # Encode the chart image
    chart_img_base64 = encode_image(chart_img_path)

    # Create a prompt for GPT-4
    prompt = f"""
    Initial analysis results:
    Axis Check: {initial_analysis['axis_check']}
    Cherry Picking Check: {initial_analysis['cherry_picking_check']}
    Chart: see attached image

    Analyze the following chart data and dataset for any additional ethical or aesthetic concerns. Your response will be used to provide feedback to the creator of the chart. Assume that the person reading your prompt doesn't have access to the initial warnings about the chart.
    If needed, you can refer to the full dataset for additional context. Keep an eye out for any potential issues that could mislead viewers or present a biased view of the data. Including but not limited to: misleading truncated axes, cherry-picking data, lack of context, missing data points, inconsistent or deceptive scale, use of 3D effects that distort proportions, inappropriate color schemes, poor color contrast, excessive complexity, missing labels or units, ambiguous or unclear legends, data smoothing that hides variability, selective highlighting, deceptive aggregation of data, over-emphasis on certain data points, data embellishments that distract from the message, manipulating time intervals, omitting baseline or zero-reference, excessive rounding of values, skewed sampling methods, inappropriate visual metaphor, use of colors that imply causation, unnecessary embellishments or "chartjunk," unequal bin sizes in histograms, bias through selective visual emphasis, failure to represent uncertainty, exaggerated differences in pie chart segments, misleading use of area/volume to represent quantity, absence of data sources or citations, misleading aspect ratio, selective inclusion of favorable data, omitting limitations of the data.
    Do not use markdown or anythng that would need to be further rendered.
    The output should also be for the chart creator, not the viewer of the chart. The goal is to provide feedback to the creator on how to improve the chart in terms of any ethical or aesthetic concerns.
    """

    print(f"Sheet Data: {sheet_data.to_json()}")
    print(f"Chart Data: {chart_data.to_json()}")
    print(f"Chart Image: {chart_img_path}")

    # Call the GPT-4 API, send prompt along with the actual image
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

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
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)


    # Write the response to a file
    with open('gpt4_response.txt', 'w') as file:
        file.write(f"GPT-4 API call successful. with info: {sheet_data.to_json()} {chart_data.to_json()} {chart_img_path}")
        file.write("\n")
        file.write(json.dumps(response.json(), indent=4))

    response = response.json()

    return response['choices'][0]['message']['content'] 

# Main function to run the analysis
def analyze_data(chart_img_path):
    full_data, chart_data = load_data()
    
    # Perform initial checks
    axis_check = check_truncated_axes(chart_data)
    cherry_picking_check = check_cherry_picking(full_data, chart_data)
    initial_analysis = {
        "axis_check": axis_check,
        "cherry_picking_check": cherry_picking_check
    }
    
    # Output initial results
    print("Initial analysis:")
    print(f"Axis Check: {initial_analysis['axis_check']}")
    print(f"Cherry Picking Check: {initial_analysis['cherry_picking_check']}")
    
    # Call GPT-4 API for deeper analysis
    api_response = call_gpt4_api(chart_img_path, full_data, chart_data, initial_analysis)
    
    # Output results from GPT-4 API
    print("Deeper analysis from GPT-4:")
    print(api_response)
    
    # Display a dialog box with the results
    messagebox.showinfo("GPT-4 API Results", api_response)
    # end program
    exit()

if __name__ == "__main__":
    chart_img_path = "data/chart.png"  # Set chart image path
    analyze_data(chart_img_path)