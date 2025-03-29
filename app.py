import streamlit as st
import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
import pandas as pd
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from langchain.schema import Document 

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY", None)

# Initialize embeddings and FAISS
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Ensure 'documents' folder exists
UPLOAD_FOLDER = "documents"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure 'faiss_index' exists as a directory
FAISS_INDEX_FOLDER = "faiss_index"
if os.path.exists(FAISS_INDEX_FOLDER) and not os.path.isdir(FAISS_INDEX_FOLDER):
    os.remove(FAISS_INDEX_FOLDER)  # Remove file if it exists
os.makedirs(FAISS_INDEX_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"txt", "pdf", "docx", "csv", "xlsx"}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# Function to check allowed file types
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to load documents
def load_documents(directory):
    docs = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        try:
            if filename.endswith(".txt"):
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                docs.append(Document(page_content=content, metadata={"source": filepath}))

            elif filename.endswith(".pdf"):
                loader = PyPDFLoader(filepath)
                docs.extend(loader.load())

            elif filename.endswith(".docx"):
                loader = Docx2txtLoader(filepath)
                docs.extend(loader.load())

            elif filename.endswith(".csv"):
                loader = CSVLoader(filepath)
                docs.extend(loader.load())

            elif filename.endswith(".xlsx"):
                df = pd.read_excel(filepath, sheet_name=None)  # Load all sheets
                for sheet, data in df.items():
                    content = data.to_string(index=False)  # Convert to string
                    docs.append(Document(page_content=content, metadata={"source": f"{filepath} - {sheet}"}))

        except Exception as e:
            print(f"Error loading {filename}: {e}")
    return docs

# Function to process documents and load FAISS vector store
def process_documents():
    raw_docs = load_documents(UPLOAD_FOLDER)
    if not raw_docs:
        st.error("No valid documents found. Please upload a valid file.")
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents(raw_docs)

    vectorstore = FAISS.from_documents(split_docs, embedding=embeddings)
    vectorstore.save_local(FAISS_INDEX_FOLDER)
    st.session_state.vectorstore = vectorstore
    return vectorstore.as_retriever()

st.title("Chat with Document Upload")

uploaded_file = st.file_uploader("Upload your document", type=ALLOWED_EXTENSIONS)

if uploaded_file:
    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(uploaded_file.name))
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.session_state.chat_history = []  # Clear chat history on new upload
    retriever = process_documents()
    if retriever:
        st.success(f"File '{uploaded_file.name}' uploaded and processed.")

# Load FAISS index if it exists
if os.path.exists(os.path.join(FAISS_INDEX_FOLDER, "index.faiss")):
    st.session_state.vectorstore = FAISS.load_local(FAISS_INDEX_FOLDER, embeddings, allow_dangerous_deserialization=True)

for chat in st.session_state.chat_history:
    st.markdown(f"**You:** {chat['user_input']}")
    st.markdown(f"**AI:** {chat['ai_response']}")

user_query = st.text_input("Ask a question about the document:")

if user_query and st.session_state.vectorstore:
    retriever = st.session_state.vectorstore.as_retriever()
    retrieved_info = retriever.invoke(user_query)

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=api_key)
    prompt = f"Docs:\n{retrieved_info}\n\nUser: {user_query}\nAI:"
    response = llm.predict(prompt)

    st.session_state.chat_history.append({"user_input": user_query, "ai_response": response})
    st.markdown(f"**AI Response:** {response}")
