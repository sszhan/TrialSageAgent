#summarizer.py

import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv() #load environment vars from the .env file

api_key = os.getenv("GEMINI_API_KEY")  #reads key from .env file
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please check your .env file.")

genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

def get_protocol_summary(protocol_text: str) -> str | None:
    """Uses the Gemini API to summarize a clinical trial protocol into a
        JSON string."""
    
    #starting zero-shot prompt
    prompt = f"""
    You are an expert medical researcher specializing in clinical trial protocols.
    Your task is to analyze the following clinical trial protocol text and extract key information.
    Provide the output *only* as a structured JSON object. Do not include any explanatory text, comments, or markdown formatting like ```json ... ```.

    The JSON object must have the following keys:
    - "study_objective": A summary of the main goal of the study. Locate the section titled "study_objective". Extract sentences related to primary goal of the study.
    - "inclusion_criteria": Locate the section titled "inclusion_criteria". A list of strings, where each string is a key inclusion criterion.
    - "exclusion_criteria": Locate the section titled "exclusion_criteria". A list of strings, where each string is a key exclusion criterion.
    - "primary_endpoints": Locate the section titled "primary_endpoints". A list of strings, for the primary outcome measures.
    - "secondary_endpoints": Locate the section titled "secondary_endpoints". A list of strings, for the secondary outcome measures.

    Here is the protocol text to analyze:
    ---
    {protocol_text}
    ---
    
    Now, generate the JSON summary.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()  #clean JSON string based on prompt
    
    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}")
        return None
    
def test_summarizer():
    """Function to test the summarizer on one local file."""

    test_file_name = "Prot_000.txt"
    test_file_path = os.path.join("data", "processed_text", test_file_name)
                #creates full path to the file

    print(f"--- Attempting to summarize: {test_file_name} ---")
    
    try:
        with open(test_file_path, 'r', encoding='utf-8') as f:
            protocol_text = f.read()
        
        summary_json_str = get_protocol_summary(protocol_text)
                        #call main function that talks to Gemini API

        #check what API returns
        if summary_json_str:
            print("Successfully received a response from Gemini.")
            #try to analyze the response as JSON to see if it's well formed

            try:
                summary_data = json.loads(summary_json_str)
                print("--- Formatted JSON Summary ---")
                print(json.dumps(summary_data, indent=2))
            
            except json.JSONDecodeError: #if AI includes text like 'Here is your JSON:'
                print("Warning: The AI's response was not a valid JSON.")
                print("--- Here is the raw text from the AI so you can debug your prompt ---")
                print(summary_json_str)
        
        else:  #if get_protocol_summary returned None due to API error
            print("Failed to get a summary. The API call may have failed.")
    

    except FileNotFoundError:
        print(f"error: Test file not found at '{test_file_path}'.")
        print("Please make sure the file exists and the name is correct.")
        
        return #stop function if file isn't found

if __name__ == "__main__":
    test_summarizer()