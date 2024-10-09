import os
import fitz  # PyMuPDF
import logging
from django.shortcuts import render
from .forms import PDFUploadForm
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

# Setup logging
logging.basicConfig(level=logging.INFO)

load_dotenv()


llm = ChatGroq(
    temperature=0, 
    groq_api_key='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', 
    model_name="llama-3.1-70b-versatile"
)

def clean_text(text):
    """Remove unwanted characters or formatting from text."""
    return text.replace('*', '').replace('\n', ' ').strip()

def extract_text_from_pdf(pdf_file):
    """Extract text from the provided PDF file."""
    text = ""
    try:
        with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        logging.error(f"Error reading PDF: {e}")
    return clean_text(text)

def pdf_qa_view(request):
    """Handle the PDF upload and question answering."""
    response = ""
    conversation = request.session.get('conversation', [])
    uploaded_file_name = request.session.get('uploaded_file_name', "")
    pdf_text = request.session.get('pdf_text', "")

    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)

        # Handle PDF upload
        if form.is_valid() and 'pdf_file' in request.FILES:
            pdf_file = request.FILES['pdf_file']
            uploaded_file_name = pdf_file.name
            pdf_text = extract_text_from_pdf(pdf_file)

            if pdf_text:
                request.session['pdf_text'] = pdf_text
                request.session['uploaded_file_name'] = uploaded_file_name
                request.session['conversation'] = []  # Clear conversation
                response = "PDF uploaded successfully. You can now ask questions."
            else:
                response = "The uploaded PDF is empty or cannot be read."

        # Handle questions
        elif 'question' in request.POST:
            question = request.POST.get('question')

            if pdf_text:
                prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", "You are a chatbot knowledgeable about the provided document."),
                        ("human", f"Question: {question}\nContext: {pdf_text}")
                    ]
                )
                output_parser = StrOutputParser()
                chain = prompt | llm | output_parser

                try:
                    answer = chain.invoke({'question': question, 'context': pdf_text})
                    answer = clean_text(answer)
                    conversation.append({'question': question, 'response': answer})
                    request.session['conversation'] = conversation
                except Exception as e:
                    response = f"Error while querying the API: {e}"
            else:
                response = "Please upload a PDF first."

    else:
        form = PDFUploadForm()

    return render(request, 'pdfapp/pdf_qa.html', {
        'form': form,
        'conversation': conversation,
        'response': response,
        'uploaded_file_name': uploaded_file_name,
    })
