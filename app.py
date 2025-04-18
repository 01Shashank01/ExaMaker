from flask import Flask, render_template, request
from model import generate_question_paper

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        context = request.form.get('context', '')

        # Collect user-defined question requirements from form
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

        question_paper = generate_question_paper(context, question_requirements)

        return render_template('index.html', context=context, question_paper=question_paper)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
