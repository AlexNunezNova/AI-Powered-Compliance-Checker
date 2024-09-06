import streamlit as st
from dotenv import load_dotenv
import os
from chat_page import chat_page
from index_page import index_page
from pathlib import Path
from dotenv import load_dotenv
from home_page import new_homepage

load_dotenv()

dotenv_path = Path('.env')
openai_api_key = os.getenv("OPENAI_API_KEY")


# Navigation
def main():
    st.sidebar.title("Navigation:")
    page = st.sidebar.radio("Go to",["Home 🏠", "Chat with Your Privacy Document 💬", "Policy Analysis 📊"])

    if page == "Home 🏠":
        new_homepage()
    elif page == "Chat with Your Privacy Document 💬":
        chat_page()
    elif page == "Policy Analysis 📊":
        index_page()

if __name__ == "__main__":
    main()
