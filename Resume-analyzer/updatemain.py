from flask import Flask, request, jsonify
import os
import shutil
import nltk
import fitz  # PyMuPDF
import pandas as pd
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))


def read_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc.pages():
        text += page.get_text()
    doc.close()
    return text


# Function to read DOCX file
def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)


# Function to preprocess text
def preprocess_text(text):
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)


# Function to calculate similarity
def calculate_similarity(resume_text, job_desc_text):
    vectorizer = TfidfVectorizer().fit_transform([resume_text, job_desc_text])
    cosine_sim = cosine_similarity(vectorizer)
    return cosine_sim[0, 1]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/calculate_similarity', methods=['POST'])
def calculate_similarity_api():
    try:
        # Creating temporary folder to save uploaded files
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        job_desc = request.form['job_description']
      
        processed_job_desc = preprocess_text(job_desc)

        uploaded_files = request.files.getlist("files")

        report_data = []

        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Process each file (PDF or DOCX), calculate similarity, and generate report
                if filename.lower().endswith('.pdf'):
                    resume_text = read_pdf(file_path)
                elif filename.lower().endswith('.docx'):
                    resume_text = read_docx(file_path)

                processed_resume = preprocess_text(resume_text)
                similarity = calculate_similarity(processed_resume, processed_job_desc)
                similarity_percentage = int(similarity * 100)

                # Append data to the list
                report_data.append({'Resume': filename, 'Similarity': f"{similarity_percentage}%"})

                # Cleaning up by deleting the temporary file
                os.remove(file_path)

        # Cleaning up by deleting the temporary folder
        shutil.rmtree(UPLOAD_FOLDER)

        # Convert the list to a DataFrame, export to Excel, and return the response
        report_df = pd.DataFrame(report_data)
        # Specify where you want to save the Excel file
        excel_file_path = 'similarity_report.xlsx'
        report_df.to_excel(excel_file_path, index=False)

        return jsonify({'similarity_report': report_data, 'excel_file_path': excel_file_path})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
