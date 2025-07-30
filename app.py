#app.py

import streamlit as st
import json
from summarizer import get_protocol_summary


#page configuration

#set title and icon that appears in browser tab
st.set_page_config(page_title="TrialSage Summarizer",
                   page_icon="⚕️",
                   layout="wide")

#application header
st.title("⚕️TrialSage: AI Clinical Trial Summarizer")
st.markdown("""
Welcome to TrialSage! This tool leverages the Google Gemini model to analyze a full clinical trial protocol
and extract key components into a structured easy to read summary.
            
How to use:
1.  Upload a clinical trial protocol in a plain text ('.txt') format.
2.  Click the "Generate Summary" button.
3.  View and download the structured JSON summary.""")

#file uploader widget
uploaded_file = st.file_uploader("Upload your protocol text file", type=['txt'])
#create a widget that allows users to drag and drop or browse for a file. Restricted
#to .txt files for simplicity and to avoid PDF processing in the app.

#main application logic
if uploaded_file is not None:  
#only runs after a user has successfuly uploaded a file
    protocol_text = uploaded_file.getvalue().decode("utf-8")
    st.subheader("Uploaded Protocol Review")
    st.text_area("Showing the first 1000 characters of the uploaded file...",
                 protocol_text[:1000], height=150)
    
    #use button to trigger API call. Avoids running expensive summarization
    #process every time app runs.
    if st.button("Generate Summary", type="primary"):
        #shows loading msg while API call is in progress
        with st.spinner("The AI agent is reading and analyzing the protocol... This " \
        "may take a moment"):
                                #call same function from summarizer.py
            summary_json_str = get_protocol_summary(protocol_text)

            #error handling and displaying results
            if summary_json_str:
                try:
                    #convert to JSON string for AI into Python dictionary
                    summary_data = json.loads(summary_json_str)

                    st.subheader("Summary Generation Complete!")

                    #st.json() is Streamlit command that displays JSON 'well'
                    st.json(summary_data, expanded=True) #shows full JSON by default

                    #fulfill exportable summaries deliverable with a download button
                    st.download_button(label="Download Summary as JSON",
                                       data=json.dumps(summary_data, indent=2),
                                       file_name=f"{uploaded_file.name.split('.')[0]}_summary.json",
                                       mime="application/json",
                                       )
                except json.JSONDecodeError:
                    st.error("The AI returned a response that could not be analyzed " \
                    "as JSON. This can happen with very complex or unusual documents. Here's the raw " \
                    "text from the AI:")
                    st.text_area("Raw AI Output", summary_json_str)

            else:
                st.error("Failed to generate a summary. The API might have " \
                "encountered an error or a timeout. Please try again.")

else:
    #display msg on initial screen before any file is uploaded
    st.info("Please upload a protocol file to begin the summarization process.")