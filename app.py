"""
Streamlit UI for RAG Chatbot with conversation history support
"""

import os
import time 
import tempfile
import streamlit as st
from rag_chatbot import RAGChatbot
from utils.document_base_manager import DocumentBaseManager


# Set page configuration
st.set_page_config(
    page_title="DBUSE",
    page_icon="🌙",
    layout="centered"
)

# CSS for styling
def get_css():
    return """
    <style>
        /* Remove hardcoded colors to respect theme */
        .stApp {
            color: var(--text-color);
        }
        
        /* Fully transparent backgrounds to respect theme */
        [data-testid="stSidebar"] {
            background-color: transparent !important;
        }
        
        /* Chat message containers */
        .stChatMessage {
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid var(--border-color-primary);
        }
        
        /* User messages */
        .stChatMessage[data-testid="user-message"] {
            background-color: rgba(66, 133, 244, 0.1);
        }
        
        /* Assistant messages */
        .stChatMessage[data-testid="assistant-message"] {
            background-color: rgba(240, 242, 246, 0.1);
        }
        
        /* Buttons */
        .stButton button {
            background-color: #4285F4;
            color: white;
            border: none;
        }
        
        .stButton button:hover {
            background-color: #3367D6;
        }
        
        /* Headers - inherit from theme */
        h1, h2, h3, p, label, div {
            color: inherit;
        }
        
        /* Code blocks */
        code, pre {
            background-color: var(--background-color);
            border: 1px solid var(--border-color-primary);
        }
        
        /* Fix file uploader text color */
        .stFileUploader label {
            color: inherit !important;
        }
        
        /* Input fields - transparent background to respect theme */
        .stTextInput input, 
        .stFileUploader, 
        .stSelectbox, 
        [data-baseweb="input"] {
            background-color: transparent !important;
            color: inherit !important;
            border-color: var(--border-color-primary) !important;
        }
        
        /* Citation styles */
        sup {
            font-size: 0.75em;
            vertical-align: super;
            line-height: 0;
        }
        
        .sources-section {
            margin-top: 20px;
            padding-top: 10px;
            border-top: 1px solid var(--border-color-primary);
            font-size: 0.9em;
        }
        
        .citation {
            color: #4285F4;
            font-weight: bold;
        }
    </style>
    """

# HTML components
def get_about_html():
    return """
    <div style="background-color: #F8F9FA; padding: 15px; border-radius: 6px; border: 1px solid #EAEAEA;">
        <h3 style="color: #333333;">About</h3>
        <p>This RAG Chatbot uses:</p>
        <ul>
            <li>LangChain for document processing</li>
            <li>ChromaDB for vector storage</li>
            <li>OpenAI API for question answering</li>
        </ul>
    </div>
    """

def get_chat_header_html():
    return """
    <div style="background-color: #F8F9FA; padding: 15px; border-radius: 6px; border: 1px solid #EAEAEA;">
        <h2 style="color: #333333;">Chat with your Documents</h2>
    </div>
    """

def get_config_header_html():
    return '<h3>Configuration</h3>'

def get_upload_header_html():
    return '<h3>Upload Documents</h3>'

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = None

if "documents_loaded" not in st.session_state:
    st.session_state.documents_loaded = False

if "document_base_manager" not in st.session_state:
    st.session_state.document_base_manager = DocumentBaseManager()

# Apply CSS styling
st.markdown(get_css(), unsafe_allow_html=True)

# Function to initialize the chatbot
def initialize_chatbot():
    api_key = st.session_state.openai_api_key.strip()
    if not api_key:
        st.error("Please enter your OpenAI API key.")
        return False
    
    try:
        # Check if we have a selected document base
        selected_base = st.session_state.get("current_base")

        # Initialize the chatbot with the provided API key
        st.session_state.chatbot = RAGChatbot(openai_api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Error initializing chatbot: {str(e)}")
        return False

# Function to process uploaded files
def process_uploaded_files(uploaded_files):
    if not st.session_state.chatbot:
        st.error("Please initialize the chatbot first.")
        return
    
    with st.spinner("Processing documents..."):
        temp_dir = tempfile.mkdtemp()
        file_paths = []
        
        # Save uploaded files to temporary directory
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(file_path)
        
        # Load documents into the chatbot
        try:
        # Use current document base if available
            document_base_name = st.session_state.get("current_base")
            
            num_chunks = st.session_state.chatbot.load_documents(
                file_paths=file_paths,
                document_base_name=document_base_name
            )
            st.session_state.documents_loaded = True
            st.success(f"Successfully processed {len(uploaded_files)} documents with {num_chunks} chunks.")
        except Exception as e:
            st.error(f"Error processing documents: {str(e)}")

# Function to handle asking questions
def ask_question(question):
    if not st.session_state.chatbot:
        return "Please initialize the chatbot with your OpenAI API key first."
    elif not st.session_state.documents_loaded:
        return "Please upload and process documents before asking questions."
    else:
        try:
            # Use the synchronous version for Streamlit compatibility
            # The internal context handling will be hidden from the UI
            answer = st.session_state.chatbot.ask_sync(question)
            return answer
        except Exception as e:
            return f"Error generating response: {str(e)}"

# Main app layout
st.title("🌙 DBUSE RAG Chatbot for Document Q&A")
st.markdown("""
This chatbot uses Retrieval-Augmented Generation (RAG) to answer questions based on your documents.
Upload PDF, Word, or Excel files, then ask questions about their content.
""")

# Sidebar for API key and file upload
with st.sidebar:
    if "document_bases" not in st.session_state:
        st.session_state.document_bases = st.session_state.document_base_manager.list_document_bases()

    document_bases = st.session_state.document_bases
    base_names = [base["name"] for base in document_bases]
    # Configuration header
    st.markdown(get_config_header_html(), unsafe_allow_html=True)
    
    # OpenAI API key input
    openai_api_key = st.text_input(
        "OpenAI API Key", 
        type="password",
        key="openai_api_key",
        help="Enter your OpenAI API key to use the chatbot."
    )
    
    # Initialize button
    init_button = st.button("Initialize Chatbot")
    if init_button:
        if initialize_chatbot():
            st.success("Chatbot initialized successfully!")
    
    st.divider()

    # Document Base Selection Section
    st.markdown("<h3>Document Bases</h3>", unsafe_allow_html=True)
    
    # Get available document bases
    document_bases = st.session_state.document_base_manager.list_document_bases()
    base_names = [base["name"] for base in document_bases]
    
    # Add selection dropdown
    selected_base = st.selectbox(
        "Select Document Base", 
        ["Create New"] + base_names,
        help="Select an existing document base or create a new one"
    )
    
    if selected_base == "Create New":
        # UI for creating a new document base
        new_base_name = st.text_input("New Document Base Name")
        new_base_desc = st.text_area("Description (optional)")
        
        if st.button("Create Document Base") and new_base_name:
            try:
                st.session_state.document_base_manager.create_document_base(new_base_name, new_base_desc)
                st.success(f"Created new document base: {new_base_name}")
                
                # Initialize chatbot with new document base if API key is set
                if st.session_state.get("openai_api_key"):
                    st.session_state.chatbot = RAGChatbot(
                        openai_api_key=st.session_state.openai_api_key,
                        document_base_name=new_base_name,
                        document_base_manager=st.session_state.document_base_manager
                    )
                    st.session_state.current_base = new_base_name
                    st.rerun()
            except ValueError as e:
                st.error(str(e))
    # Add this after displaying info about the selected document base
    if selected_base != "Create New":
        base_info = next((base for base in document_bases if base["name"] == selected_base), None)
        if base_info:
            st.info(f"Documents: {base_info['num_documents']}\nChunks: {base_info['num_chunks']}")
            
            # Add buttons in columns for better layout
            col1, col2 = st.columns(2)
            
            with col1:
                # Load button
                if st.button("Load Base"):
                    st.session_state.chatbot = RAGChatbot(
                        openai_api_key=st.session_state.openai_api_key,
                        document_base_name=selected_base,
                        document_base_manager=st.session_state.document_base_manager
                    )
                    
                    # Set documents_loaded based on whether retriever was initialized
                    if st.session_state.chatbot.retriever is not None:
                        st.session_state.documents_loaded = True
                        st.success(f"Loaded document base: {selected_base}")
                    else:
                        st.warning(f"Document base exists but contains no documents.")
                        st.session_state.documents_loaded = False
                    
                    st.session_state.current_base = selected_base
                    st.rerun()
            
            with col2:
                # Delete button
                if st.button("Delete Base", type="secondary"):
                    delete_confirmed = st.checkbox("Confirm deletion")
                    
                    if delete_confirmed:
                        try:
                            st.session_state.document_base_manager.delete_document_base(selected_base)
                            
                            # Reset if we were using this base
                            if st.session_state.get("current_base") == selected_base:
                                st.session_state.current_base = None
                                st.session_state.documents_loaded = False
                                if st.session_state.get("chatbot"):
                                    st.session_state.chatbot = None
                            
                            st.success(f"Deleted document base: {selected_base}")
                            st.session_state.document_bases = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting document base: {str(e)}")
    
    # File uploader
    st.markdown(get_upload_header_html(), unsafe_allow_html=True)
        
    uploaded_files = st.file_uploader(
        "Upload PDF, Word, or Excel files",
        type=["pdf", "docx", "xlsx", "xls"],
        accept_multiple_files=True
    )
    
    # Process button
    if uploaded_files:
        process_button = st.button("Process Documents")
        if process_button:
            process_uploaded_files(uploaded_files)
    
    # Clear documents button
    if st.session_state.documents_loaded:
        if st.button("Clear Documents"):
            if st.session_state.chatbot:
                st.session_state.chatbot.clear_documents()
                st.session_state.documents_loaded = False
                st.success("All documents have been cleared.")
    
    # Clear chat history
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        if st.session_state.chatbot:
            st.session_state.chatbot.clear_history()
        st.success("Chat history cleared.")

# Display chat messages from session state
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        if not st.session_state.chatbot:
            response = "Please initialize the chatbot with your OpenAI API key first."
        elif not st.session_state.documents_loaded:
            response = "Please upload and process documents before asking questions."
        else:
            # Initialize placeholder for the response
            message_placeholder = st.empty()
            
            try:
                # Simulate streaming in a Streamlit-friendly way
                # First, get the complete response
                with st.spinner("Thinking..."):
                    full_response = st.session_state.chatbot.ask_sync(prompt)
                
                # Then display it character by character to simulate streaming
                displayed_response = ""
                for char in full_response:
                    displayed_response += char
                    message_placeholder.markdown(displayed_response + "▌")
                    time.sleep(0.005)  # Small delay for streaming effect
                
                # Final display without cursor
                message_placeholder.markdown(full_response)
                response = full_response
            except Exception as e:
                response = f"Error generating response: {str(e)}"
                message_placeholder.markdown(response)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Instructions if no documents loaded
if not st.session_state.documents_loaded:
    st.info("👈 Please initialize the chatbot and upload documents to get started.")