from flask import Flask, request, jsonify
import os
import nltk
import fitz  # PyMuPDF
import pandas as pd
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Download NLTK stopwords and punkt if not already present
nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))


# Function to read PDF file
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


@app.route('/calculate_similarity', methods=['POST'])
def calculate_similarity_api():
    try:
        data = request.get_json()
        job_desc = data['job_description']
        folder_path = data['folder_path']

        if not os.path.exists(folder_path):
            return jsonify({'error': 'Invalid folder path'}), 400

        processed_job_desc = preprocess_text(job_desc)

        # Create a list to store report data
        report_data = []

        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith('.pdf') or file_name.lower().endswith('.docx'):
                file_path = os.path.join(folder_path, file_name)

                if file_name.lower().endswith('.pdf'):
                    resume_text = read_pdf(file_path)
                elif file_name.lower().endswith('.docx'):
                    resume_text = read_docx(file_path)

                processed_resume = preprocess_text(resume_text)
                similarity = calculate_similarity(processed_resume, processed_job_desc)
                similarity_percentage = int(similarity * 100)

                # Append data to the list
                report_data.append({'Resume': file_name, 'Similarity': f"{similarity_percentage}%"})

        # Convert the list to a DataFrame
        report_df = pd.DataFrame(report_data)

        # Export the DataFrame to an Excel file
        excel_file_path = os.path.join(folder_path, 'similarity_report.xlsx')
        report_df.to_excel(excel_file_path, index=False)

        # Return the JSON response with the Excel file path
        return jsonify({'similarity_report': report_data, 'excel_file_path': excel_file_path})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
