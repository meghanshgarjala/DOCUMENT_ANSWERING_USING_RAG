import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

st.title("DOCUMENT ANSWERING APPLICATION USING RAG")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

loader = PyPDFLoader("class8science.pdf")
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(data)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory="chroma_storage")

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.6, max_tokens=None, timeout=None)

system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

# Display chat history as chat messages
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["query"])
    with st.chat_message("assistant"):
        st.write(chat["answer"])

# Input box for new queries
if query := st.chat_input("Ask me anything:"):
    # Display the user's message
    with st.chat_message("user"):
        st.write(query)

    # Create the chains
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # Get the response
    response = rag_chain.invoke({"input": query})
    answer = response["answer"]

    # Display the assistant's response
    with st.chat_message("assistant"):
        st.write(answer)

    # Update chat history
    st.session_state.chat_history.append({"query": query, "answer": answer})
