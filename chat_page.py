import os
import streamlit as st
from streamlit_chat import message
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from dotenv import load_dotenv

load_dotenv()

# Getting the OpenAI API key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key is None:
    st.error("OpenAI API key not found. Please set it in the .env file.")
    st.stop()

CHAT_DOC_DIR = "data/chat_documents"
os.makedirs(CHAT_DOC_DIR, exist_ok=True)

def initialize_chat_index(file_content, file_name):
    # Saving uploaded file to the chat documents directory
    uploaded_file_path = os.path.join(CHAT_DOC_DIR, file_name)
    with open(uploaded_file_path, "wb") as f:
        f.write(file_content)

    # Loading the document for chat
    documents = SimpleDirectoryReader(CHAT_DOC_DIR).load_data()
    chat_index = VectorStoreIndex.from_documents(documents)
    return chat_index

def chat_page():
    st.header("Chat with your Privacy Document 💬")
    st.write("In this section you will be able to ask questions about your own privacy policy in a chat context.")
    st.write("Try yourself, make your policies better! :star-struck:")
    if "chat_index" not in st.session_state:
        st.session_state.chat_index = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Uploading the file for new document
    uploaded_file = st.file_uploader("Upload your company privacy document", type=["txt", "pdf", "docx"], key="chat_uploader")

    if uploaded_file is not None:
        file_content = uploaded_file.read()
        file_name = uploaded_file.name

        # Initializing a new index for the uploaded document
        st.session_state.chat_index = initialize_chat_index(file_content, file_name)
        st.session_state.chat_history = []

    if st.session_state.chat_index is not None:
        # Creating a query engine and asking question
        query_engine = st.session_state.chat_index.as_query_engine()
        user_input = st.text_input("Ask a question about the document:")

        if user_input:
            # Getting the response from the query engine
            response = query_engine.query(user_input)
            # Saving the question and response to the chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "bot", "content": str(response)})
            # Ensure the input box is cleared
            st.session_state["user_input"] = ""

    # Display the chat history
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            message(chat["content"], is_user=True)
        else:
            message(chat["content"], is_user=False)

if __name__ == "__main__":
    chat_page()



