import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from .env file
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the Gemini Flash model
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

def generate_question_paper(context, question_requirements, difficulty="easy"):
    # Build the prompt
    prompt = (
        "You are an expert exam assistant. Based on the following study material, "
        f"generate an exam-style question paper of {difficulty} difficulty.\n\n"
        "Instructions:\n"
    )

    for q_type, config in question_requirements.items():
        count = config.get("count", 0)
        marks = config.get("marks", None)
        if count > 0:
            if marks:
                prompt += f"- {count} {q_type} questions ({marks} marks each)\n"
            else:
                prompt += f"- {count} {q_type} questions\n"

    prompt += (
        "\nGuidelines:\n"
        "- For MCQs, provide 4 options (a, b, c, d) and indicate the correct one.\n"
        "- Frame questions clearly and align them with the given content.\n"
        "- Ensure questions are academically appropriate.\n"
        "- Provide the correct answers below the question paper.\n"
        "\nStudy Material:\n"
        f"\"\"\"\n{context}\n\"\"\"\n\n"
        "Return the output in two sections:\n"
        "1. Question Paper\n"
        "2. Answer Key\n"
    )

    try:
        response = model.generate_content(prompt)
        output = response.text.strip()

        # Split the output into two parts: questions and answers
        if "Answer Key" in output:
            question_part, answer_part = output.split("Answer Key", 1)
            question_paper = question_part.strip()
            answer_key = "Answer Key\n" + answer_part.strip()
        else:
            question_paper = output
            answer_key = "❌ Answer key not found in the response."

        return question_paper, answer_key

    except Exception as e:
        print("❌ Error during content generation:", e)
        return "Failed to generate question paper.", ""

# -------------------------------
# 🧪 Run this block for testing
# -------------------------------
if __name__ == "__main__":
    sample_context = """
Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods with the help of chlorophyll. 
It generally involves the intake of carbon dioxide and the release of oxygen. The process occurs mainly in the leaves of plants, inside organelles called chloroplasts.
"""

    sample_requirements = {
        "Fill in the blanks": {"count": 4, "marks": 1},
        "One-word answer": {"count": 3, "marks": 1},
        "True/False": {"count": 2, "marks": 1},
        "Short answer": {"count": 2, "marks": 3},
        "Long answer": {"count": 1, "marks": 5},
        "MCQ": {"count": 3, "marks": 2}
    }

    print("🧠 Generating Question Paper with Answers...")
    qp, ak = generate_question_paper(sample_context, sample_requirements, difficulty="intermediate")
    print("\n📄 Question Paper:\n", qp)
    print("\n✅ Answer Key:\n", ak)
