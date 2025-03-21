from flask import Flask, request, jsonify
import pdfplumber
from fuzzywuzzy import process

app = Flask(__name__)

# Load the SEBI PDF File Path
PDF_PATH = "sebi_guidelines.pdf"

def extract_answer(query):
    """Extract relevant text from the SEBI PDF using pdfplumber and fuzzy matching."""
    text = ""

    # Open PDF and extract text
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Debug: Print extracted text (first 1000 characters)
    print("Extracted PDF Text:\n", text[:1000])

    query_lower = query.lower()

    # Split text into lines
    lines = text.split("\n")

    # Get best matching line using fuzzy search
    best_match, score = process.extractOne(query_lower, lines)

    # Return best match if similarity score is above threshold
    if score > 60:  # Adjust threshold if needed
        return best_match
    else:
        return "Sorry, I couldn't find an exact answer in the SEBI guidelines."

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming webhook requests from Dialogflow."""
    req = request.get_json()
    
    # Extract user query
    query_text = req["queryResult"]["queryText"]

    # Get the best answer from the PDF
    answer = extract_answer(query_text)

    response = {
        "fulfillmentText": answer  # Send extracted text as response
    }
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
