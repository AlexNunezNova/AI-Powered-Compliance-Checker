import streamlit as st
import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
#from llama_index.legacy.readers.file.base import SimpleDirectoryReader
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

dotenv_path = Path('.env')
openai_api_key = os.getenv("OPENAI_API_KEY")


PERSIST_DIR = "data/storage"
PRE_EXISTING_DOC_DIR = "data/documents"
PRE_EXISTING_DOC_FILE = "GDPR_EN.docx"
CHAT_DOC_DIR = "data/chat_documents"

# Ensure directories exist
os.makedirs(PERSIST_DIR, exist_ok=True)
os.makedirs(PRE_EXISTING_DOC_DIR, exist_ok=True)
os.makedirs(CHAT_DOC_DIR, exist_ok=True)

# Loading the pre-existing document and creating the initial index 
def initialize_index():
    pre_existing_doc_path = os.path.join(PRE_EXISTING_DOC_DIR, PRE_EXISTING_DOC_FILE)
    if not os.path.exists(PERSIST_DIR) or not os.listdir(PERSIST_DIR):
        st.write("Initializing storage and indexing pre-existing document...")
        if not os.path.exists(pre_existing_doc_path):
            st.error(f"Pre-existing document {PRE_EXISTING_DOC_FILE} does not exist in {PRE_EXISTING_DOC_DIR}.")
            return None
        documents = SimpleDirectoryReader(PRE_EXISTING_DOC_DIR).load_data()
        index = VectorStoreIndex.from_documents(documents)
        # Store the index for later use
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        st.write("Index initialized and persisted.")
    else:
        st.write("Loading existing index from storage...")
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
        st.write("Index loaded.")
    return index

def reinitialize_index_with_new_document(file_content, file_name):
    st.write(f"Reinitializing index with the new document {file_name}...")
    # Save uploaded file to the documents directory
    uploaded_file_path = os.path.join(PRE_EXISTING_DOC_DIR, file_name)
    with open(uploaded_file_path, "wb") as f:
        f.write(file_content)
    
    # We are loading all documents again
    documents = SimpleDirectoryReader(PRE_EXISTING_DOC_DIR).load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    st.write("Document added and index reinitialized.")
    return index

def initialize_chat_index(file_content, file_name):
    st.write(f"Uploading you file {file_name}...")
    #Saving the uploaded file to the new chat documents directory
    uploaded_file_path = os.path.join(CHAT_DOC_DIR, file_name)
    with open(uploaded_file_path, "wb") as f:
        f.write(file_content)
    
    # Loading the document for chat purpose
    documents = SimpleDirectoryReader(CHAT_DOC_DIR).load_data()
    chat_index = VectorStoreIndex.from_documents(documents)
    st.write("You can chat now go ahead.")
    return chat_index

# Function to create a prompt template
def create_prompt_template():
    template = (
        "You will take the role of a Privacy Policy analyst. You are going to take as framework for your responses the GDPR "
        "(General Data Protection Regulation). Do not use any other regulation outside GDPR.\n"
        "A privacy policy document is uploaded to you.\n\n"
        "Analyzing this privacy policy in detail, tell me what aspects of this policy are:\n"
        "1) not in compliance with the GDPR\n"
        "2) what elements are lacking (For example, security measures or transparency measures)\n"
        "3) what elements can be improved\n"
        "4) which principles from the GDPR are insufficiently considered.\n\n"
        "Enumerate each of the elements you describe, indicate the article of GDPR that is used for analyzing every fault or improvement point, and please provide any relevant detail for the analysis."
    )
    return template


def main():
    st.title("Privacy Policy Analyzer")

    # Create tabs
    tab1, tab2 = st.tabs(["Chat with Document", "Index and Query"])

    with tab1:
        st.header("Chat with Document")
        
        uploaded_file = st.file_uploader("Upload your company privacy document", type=["txt", "pdf", "docx"], key="chat_uploader")
        
        if uploaded_file is not None:
            file_content = uploaded_file.read()
            file_name = uploaded_file.name
            
            # Initialize the new chat index
            chat_index = initialize_chat_index(file_content, file_name)
        
            if chat_index is not None:
                
                query_engine = chat_index.as_query_engine()
                
                
                question = st.text_input("Ask a question about the document:")
                
                if question:
                    # response from the query engine
                    response = query_engine.query(question)
                    # Display the response
                    st.write(f"Response: \n {response}")

    with tab2:
        st.header("Index and Query")
        
      
        index = initialize_index()
        
        if index is not None:
            
            uploaded_file = st.file_uploader("Upload your company privacy document", type=["txt", "pdf", "docx"], key="index_uploader")
            
            if uploaded_file is not None:
                file_content = uploaded_file.read()
                file_name = uploaded_file.name
                
                # Reinitialize the index with the uploaded document
                new_index = reinitialize_index_with_new_document(file_content, file_name)

                if new_index is not None:
                  
                    prompt = create_prompt_template()
                    
                    
                    query_engine = new_index.as_query_engine()
                    
                  
                    response = query_engine.query(prompt)
                    
                    # Display the response
                    st.write(f"Response: \n {response}")

if __name__ == "__main__":
    main()