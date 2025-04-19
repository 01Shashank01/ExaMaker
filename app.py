from flask import Flask, render_template, request, send_file
from model import generate_question_paper
from xhtml2pdf import pisa
from io import BytesIO
import PyPDF2
import os

app = Flask(__name__)

STATIC_NOTES_PATH = 'static/notes'

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    extracted_text = ""
    for page in pdf_reader.pages:
        extracted_text += page.extract_text() or ""
    return extracted_text

def list_subjects_and_chapters():
    subjects = {}
    for subject in os.listdir(STATIC_NOTES_PATH):
        subject_path = os.path.join(STATIC_NOTES_PATH, subject)
        if os.path.isdir(subject_path):
            chapters = [
                os.path.splitext(f)[0]
                for f in os.listdir(subject_path)
                if f.lower().endswith('.pdf')
            ]
            chapters.sort()
            subjects[subject] = chapters
    return subjects

@app.route('/', methods=['GET', 'POST'])
def home():
    subjects_data = list_subjects_and_chapters()
    context = ""
    question_paper = ""

    if request.method == 'POST':
        selected_subject_raw = request.form.get('subject')
        selected_chapter_raw = request.form.get('chapter')

        # Convert user-friendly names to actual folder names
        selected_subject = selected_subject_raw.replace(" ", "_") if selected_subject_raw else ""
        selected_chapter = selected_chapter_raw.replace(" ", "_") if selected_chapter_raw else ""

        if selected_subject and selected_chapter:
            chapter_file = selected_chapter + ".pdf"
            chapter_path = os.path.join(STATIC_NOTES_PATH, selected_subject, chapter_file)
            print("📁 Looking for chapter PDF at:", chapter_path)

            if os.path.exists(chapter_path):
                with open(chapter_path, 'rb') as pdf_file:
                    context = extract_text_from_pdf(pdf_file)
                    print("✅ Extracted context length:", len(context))
            else:
                print("❌ PDF file does NOT exist.")
        elif 'pdf_file' in request.files and request.files['pdf_file'].filename != '':
            pdf_file = request.files['pdf_file']
            context = extract_text_from_pdf(pdf_file)
            print("✅ Extracted from uploaded PDF, length:", len(context))
        else:
            context = request.form.get('context', '')
            print("✍ Using manually typed context, length:", len(context))

        # Difficulty level
        difficulty = request.form.get('difficulty', 'easy')

        # Question config
        question_requirements = {
            "Fill in the blanks": {
                "count": int(request.form.get('fill_count', 0)),
                "marks": int(request.form.get('fill_marks', 0))
            },
            "One-word answer": {
                "count": int(request.form.get('oneword_count', 0)),
                "marks": int(request.form.get('oneword_marks', 0))
            },
            "True/False": {
                "count": int(request.form.get('tf_count', 0)),
                "marks": int(request.form.get('tf_marks', 0))
            },
            "Short answer": {
                "count": int(request.form.get('short_count', 0)),
                "marks": int(request.form.get('short_marks', 0))
            },
            "Long answer": {
                "count": int(request.form.get('long_count', 0)),
                "marks": int(request.form.get('long_marks', 0))
            },
            "MCQ": {
                "count": int(request.form.get('mcq_count', 0)),
                "marks": int(request.form.get('mcq_marks', 0))
            }
        }

        if context.strip():
            question_paper = generate_question_paper(context, question_requirements, difficulty=difficulty)
        else:
            question_paper = "❌ No valid content found for generating question paper."

    return render_template(
        'index.html',
        context=context,
        question_paper=question_paper,
        subjects_data=subjects_data
    )

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    question_paper = request.form.get('pdf_content', '')
    pdf_io = BytesIO()
    html_content = f"<html><body><pre>{question_paper}</pre></body></html>"
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_io)

    if pisa_status.err:
        return "Error while generating PDF", 500

    pdf_io.seek(0)
    return send_file(pdf_io, download_name="question_paper.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
