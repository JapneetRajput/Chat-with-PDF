from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()
genai.configure(api_key="AIzaSyAhlaWdtv__3QhH8bL-kD4dEN0Mrrvn1Ts")

app = Flask(__name__)


def get_pdf_text(pdf_path):
    text = ""
    print(pdf_path)
    with open(pdf_path, 'rb') as f:
        pdf_reader = PdfReader(f)
        for page in pdf_reader.pages:
            text += page.extract_text()
    print(text)
    return text


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


def get_conversational_chain():

    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro",
                                   temperature=0.3)

    prompt = PromptTemplate(template=prompt_template,
                            input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain


def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    new_db = FAISS.load_local("faiss_index", embeddings)
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()

    response = chain.invoke(
        {"input_documents": docs, "question": user_question})
    print(response)
    return response


# folder_paths = ["C:\\Users\\Arjun\\Downloads\\12th CBSE NCERT\\Chemistry"]

# for folder_path in folder_paths:
#     # Check if the folder exists
#     if os.path.isdir(folder_path):
#         # Get all files in the folder
#         text = ""
#         for filename in os.listdir(folder_path):
#             # Check if the file is a PDF
#             if filename.endswith(".pdf"):
#                 # Construct the full path to the PDF
#                 pdf_path = os.path.join(folder_path, filename)
#                 # Pass the PDF path to your function
#                 text += get_pdf_text(pdf_path)
#         text_chunks = get_text_chunks(text)
#         get_vector_store(text_chunks)
#     else:
#         print(f"Folder '{folder_path}' does not exist.")


@app.route('/ask', methods=['POST'])
def process_user_input():
    # Get user question from the request body
    user_question = request.json.get('question')
    if not user_question:
        return jsonify({'error': 'Missing question in request body'}), 400

    # Process the user question and generate response
    try:
        response = user_input(user_question)
    except Exception as e:
        response = f"Error processing your request: {str(e)}"

    return jsonify({'response': response})


if __name__ == '__main__':
    app.run(debug=True)
