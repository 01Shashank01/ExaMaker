from flask import Flask, render_template, request, send_file
from model import generate_question_paper
from xhtml2pdf import pisa
from io import BytesIO
import PyPDF2

app = Flask(__name__)

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    extracted_text = ""
    for page in pdf_reader.pages:
        extracted_text += page.extract_text() or ""
    return extracted_text

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get uploaded PDF or text area content
        if 'pdf_file' in request.files and request.files['pdf_file'].filename != '':
            pdf_file = request.files['pdf_file']
            context = extract_text_from_pdf(pdf_file)
        else:
            context = request.form.get('context', '')

        # Get difficulty level
        difficulty = request.form.get('difficulty', 'easy')

        # Gather question configuration
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
            }
        }

        # Generate the question paper using the difficulty
        question_paper = generate_question_paper(context, question_requirements, difficulty=difficulty)

        return render_template('index.html', context=context, question_paper=question_paper)

    return render_template('index.html')

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
