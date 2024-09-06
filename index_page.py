import streamlit as st
import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

PERSIST_DIR = "data/storage"
PRE_EXISTING_DOC_DIR = "data/documents"
PRE_EXISTING_DOC_FILE = "GDPR_EN.docx"

# Ensure directories exist
os.makedirs(PERSIST_DIR, exist_ok=True)
os.makedirs(PRE_EXISTING_DOC_DIR, exist_ok=True)

# Loading the pre-existing document and creating the initial index 
def initialize_index():
    pre_existing_doc_path = os.path.join(PRE_EXISTING_DOC_DIR, PRE_EXISTING_DOC_FILE)
    if not os.path.exists(PERSIST_DIR) or not os.listdir(PERSIST_DIR):
        #st.write("Initializing storage and indexing pre-existing document...")
        if not os.path.exists(pre_existing_doc_path):
            st.error(f"Pre-existing document {PRE_EXISTING_DOC_FILE} does not exist in {PRE_EXISTING_DOC_DIR}.")
            return None
        documents = SimpleDirectoryReader(PRE_EXISTING_DOC_DIR).load_data()
        index = VectorStoreIndex.from_documents(documents)
        # Store the index for later use
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        #st.write("Index initialized and persisted.")
    else:
        #st.write("Loading existing index from storage...")
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
        #st.write("Index loaded.")
    return index

def reinitialize_index_with_new_document(file_content, file_name):
    #st.write(f"Reinitializing index with the new document {file_name}...")
    # Save uploaded file to the documents directory
    uploaded_file_path = os.path.join(PRE_EXISTING_DOC_DIR, file_name)
    with open(uploaded_file_path, "wb") as f:
        f.write(file_content)
    
    # We are loading all documents again
    documents = SimpleDirectoryReader(PRE_EXISTING_DOC_DIR).load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
   # st.write("Document added and index reinitialized.")
    return index

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

def index_page():
    st.header("Analysis Of Company Privacy Policy 📊")
    st.write("This is a privacy policy analyst powered by Artificial Intelligence.\nHere you will find out if your privacy policy is compliant with the GDPR or not. ")
    st.write("More specifically, you will find comments  concerning:")
    st.write("1) Elements not in compliance with the GDPR.\n 2) What elements are lacking (For example, security measures or transparency measures).\n 3)Wwhat elements can be improved.\n4) Which principles from the GDPR are insufficiently considered.")
    st.write("Also, you can have idea in which way you can improve your company's privacy policy")
    
            
        
    if "index" not in st.session_state:
        st.session_state.index = initialize_index()

    if "index_response" not in st.session_state:
        st.session_state.index_response = ""

    if st.session_state.index is not None:
        # File uploader for new document
        uploaded_file = st.file_uploader("Upload your company privacy document", type=["txt", "pdf", "docx"], key="index_uploader")
        
        if uploaded_file is not None:
            file_content = uploaded_file.read()
            file_name = uploaded_file.name
            
            # Reinitialize the index with the uploaded document
            st.session_state.index = reinitialize_index_with_new_document(file_content, file_name)

            if st.session_state.index is not None:
                # Create a prompt using the template
                prompt = create_prompt_template()
                
                # Create a query engine
                query_engine = st.session_state.index.as_query_engine()
                
                # Get the response from the query engine
                st.session_state.index_response = query_engine.query(prompt)
                
    if st.session_state.index_response:
        st.write(f"Analysis of Your Company Policies: \n {st.session_state.index_response}")
        st.warning("Attention: This is an AI pre-assessment and should not be considered professional advice. If you are not a privacy professional, please contact one in order to evaluate your policy documents based on this application.")