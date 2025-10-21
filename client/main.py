import os
import requests
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="Sales Analysis Client",
    description="Client to request sales data and analyze it with Gemini AI.",
    version="1.0.0"
)

# Configure Gemini AI with API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Make sure it exists in the .env file")
genai.configure(api_key=GEMINI_API_KEY)

# Server data endpoint URL
SERVER_URL = "http://127.0.0.1:8000"

@app.get("/analyze-sales", tags=["Analysis"])
def analyze_sales():
    """
    Endpoint to fetch data from the server and analyze it using Gemini.
    """
    # 1. Request data from the server
    try:
        print(f"Fetching data from server at {SERVER_URL}...")
        payload = {
            "password": "xxx",
            "username": "xxx"
        }
        getTokenFromServer = requests.post("{}/{}".format(SERVER_URL, "token"), json=payload, headers={'Content-Type': 'application/json'})
        response_server = requests.get("{}/{}".format(SERVER_URL,"get-sales-data"), headers={'Authorization': 'Bearer {}'.format(getTokenFromServer.json()['access_token']),})
        response_server.raise_for_status()  # Will error if status code is not 2xx
        sales_data = response_server.json()
        print("Successfully retrieved data from server.")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
        raise HTTPException(status_code=503, detail=f"Cannot connect to data server: {e}")

    # 2. Send data to Gemini for analysis
    try:
        print("Sending data to Gemini for analysis...")
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Create a clear prompt for Gemini
        prompt = f"""
        You are an expert data analyst.
        Here is the sales data in JSON format:
        {sales_data}

        Please provide a brief analysis of the data. Include the following points:
        1. Which product sold the most (based on 'Jumlah')?
        2. What is the total revenue from all transactions?
        3. Give one insight or business recommendation based on this data.
        
        Present the answer in JSON format.
        """
        
        response_gemini = model.generate_content(prompt)
        
        # Clean Gemini's output (sometimes includes markdown)
        cleaned_response = response_gemini.text.strip().replace("```json", "").replace("```", "")
        
        print("Successfully received analysis from Gemini.")
        return JSONResponse(content={"gemini_analysis": cleaned_response})

    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while communicating with Gemini: {str(e)}")
