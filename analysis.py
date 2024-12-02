import pandas as pd
import requests
import json
import base64
from dotenv import load_dotenv
import os

# load the environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_KEY")

# Function to check for truncated axes
def check_truncated_axes(data: pd.DataFrame) -> str:
    """
    Check if the axes of the chart are properly scaled.

    Args:
    - data: Data from the chart.

    Returns:
    - A message indicating whether the axes are properly scaled or if there is a warning.
    """
    # Convert the "Value" column to numeric, coercing errors to NaN, and drop NaN values
    data["Value"] = pd.to_numeric(data["Value"], errors='coerce').dropna()
    min_value = data["Value"].min()
    if min_value > 0:
        return "Warning: The axis may be truncated, which could mislead viewers."
    return "Axes appear to be properly scaled."

# Function to check for cherry-picking (omitted data)
def check_cherry_picking(sheet_data: pd.DataFrame, chart_data: pd.DataFrame) -> str:
    """
    Check if the chart data is cherry-picked from the full dataset.

    Args:
    - sheet_data: Data from the full dataset.
    - chart_data: Data from the chart.

    Returns:
    - A message indicating whether the chart data is representative of the full dataset or if there is a warning.
    """
    # Ensure both datasets are numeric for comparison
    sheet_data["Value"] = pd.to_numeric(sheet_data["Value"], errors='coerce').dropna()
    chart_data["Value"] = pd.to_numeric(chart_data["Value"], errors='coerce').dropna()
    
    # check range of values in both datasets
    sheet_range = (sheet_data["Value"].min(), sheet_data["Value"].max())
    chart_range = (chart_data["Value"].min(), chart_data["Value"].max())

    # check trendline of chart data
    chart_trend = "upward" if chart_data["Value"].iloc[-1] > chart_data["Value"].iloc[0] else "downward"
    # check trendline of sheet data
    sheet_trend = "upward" if sheet_data["Value"].iloc[-1] > sheet_data["Value"].iloc[0] else "downward"
    
    if chart_range[0] > sheet_range[0] or chart_range[1] < sheet_range[1]:
        return "Warning: The chart data may be cherry-picked, not reflecting the full dataset."
    
    if chart_trend != sheet_trend:
        return "Warning: The chart data may be cherry-picked, not reflecting the full dataset. Trendline is different."
    
    return "Data appears representative of the entire dataset."

def initial_checks(chart_data: pd.DataFrame, full_data: pd.DataFrame) -> dict:
    """
    Perform initial checks on the chart data.

    Args: 
    - chart_data: Data from the chart.
    - full_data: Data from the full dataset.

    Returns:
    - A dictionary containing the results of the initial checks.
    """
    axis_check = check_truncated_axes(chart_data)
    cherry_picking_check = check_cherry_picking(full_data, chart_data)
    return {
        "axis_check": axis_check,
        "cherry_picking_check": cherry_picking_check
    }

# Function to call GPT-4 API for deeper analysis
def call_gpt4_api(chart_img_base64: str, sheet_data: pd.DataFrame, chart_data: pd.DataFrame, initial_analysis: dict) -> str:
    """
    Call the GPT-4 API for deeper analysis.

    Args: 
    - chart_img_base64: Base64 encoded image of the chart.
    - sheet_data: Data from the full dataset.
    - chart_data: Data from the chart.
    - initial_analysis: Initial analysis results.

    Returns:
    - A response from the GPT-4 API. This response will contain feedback on the chart.
    """

    # Create a prompt for GPT-4
    prompt = f"""
    Initial analysis results:
    Axis Check: {initial_analysis['axis_check']}
    Cherry Picking Check: {initial_analysis['cherry_picking_check']}
    Chart Data: {chart_data.to_json()}
    Sheet Data: {sheet_data.to_json()}
    Chart: see attached image

    Analyze the following chart image, chart data (subset of complete dataset), and complete dataset for any additional ethical or aesthetic concerns. Your response will be used to provide feedback to the creator of the chart. Assume that the person reading your prompt doesn't have access to the initial warnings about the chart.
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
        "max_tokens": 500
    }

    # Make the API call
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # Write the response to a file
    with open('gpt4_response.txt', 'w') as file:
        file.write(f"GPT-4 API call successful. with info: {sheet_data.to_json()} {chart_data.to_json()} {chart_img_path}")
        file.write("\n")
        file.write(json.dumps(response.json(), indent=4))

    response = response.json()

    # Return the response from the API
    return response['choices'][0]['message']['content'] 

# Main function to run the analysis
def analyze_data(chart_b64: str, data: dict) -> str:
    """
    Analyze the chart data and call the GPT-4 API for deeper analysis.
    
    Args:
    - chart_b64: Base64 encoded image of the chart.
    - data: A dictionary containing the full data and chart data.
    
    Returns:
    - A string containing the results of the analysis.
    """
    full_data = pd.DataFrame(data["full_data"])
    chart_data = pd.DataFrame(data["chart_data"])
    
    # Perform initial checks
    initial_analysis = initial_checks(chart_data, full_data)
    
    # Output initial results
    print("Initial analysis:")
    print(f"Axis Check: {initial_analysis['axis_check']}")
    print(f"Cherry Picking Check: {initial_analysis['cherry_picking_check']}")
    
    # Call LLM (4o) for deeper analysis
    api_response = call_gpt4_api(chart_b64, full_data, chart_data, initial_analysis)
    
    # Output results from GPT-4 API
    print("Deeper analysis from LLM:")
    print(api_response)
    
    return api_response

if __name__ == "__main__":
    def encode_image(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
        
    # sample data
    data = {"full_data": {"Date":{"0":"2020-01-01","1":"2020-01-02","2":"2020-01-03","3":"2020-01-04","4":"2020-01-05","5":"2020-01-06","6":"2020-01-07","7":"2020-01-08","8":"2020-01-09","9":"2020-01-10","10":"2020-01-11","11":"2020-01-12"},"Value":{"0":10,"1":9,"2":8,"3":7,"4":6,"5":5,"6":5,"7":6,"8":7,"9":8,"10":9,"11":10}},
            "chart_data": {"Date":{"0":"2020-01-07","1":"2020-01-08","2":"2020-01-09","3":"2020-01-10","4":"2020-01-11","5":"2020-01-12"},"Value":{"0":5,"1":6,"2":7,"3":8,"4":9,"5":10}}}

    chart_img_path = "data/chart.png" 
    chart_img_base64 = encode_image(chart_img_path) 
    print(analyze_data(chart_img_base64, data))