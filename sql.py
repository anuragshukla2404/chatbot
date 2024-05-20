from sqlalchemy import create_engine, text
from typing import List, Dict, Optional
from flask import Flask, request, jsonify, render_template_string
import openai
import json
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')  # Ensure that the environment variable is read safely

# Setup database engine
DATABASE_URL = "mysql+pymysql://root:123456@localhost/chatbot"
engine = create_engine(DATABASE_URL)

def execute_sql(sql_query: str, params: Optional[Dict] = None) -> List[Dict]:
    if params is None:
        params = {}
    
    with engine.connect() as connection:
        result = connection.execute(text(sql_query), params)
        # Convert results into a list of dictionaries to use outside the 'with' scope
        rows = [{'name': row[0]} for row in result]
    
    # Optionally print rows for debugging, though consider logging them instead in production
    print(rows)
    return rows


def generate_sql(prompt: str) -> str:
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",  # Updated to use a more recent model available or specify your chosen model
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error with OpenAI service: {e}")
        return "Error generating SQL"

@app.route('/', methods=['GET'])
def home():
    html_form = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ask a Question</title>
    </head>
    <body>
        <h1>Ask a Question</h1>
        <form action="/answer" method="post">
            <input type="text" name="question" placeholder="Type your question here" required>
            <input type="submit" value="Submit">
        </form>
    </body>
    </html>
    """
    return render_template_string(html_form)

@app.route('/answer', methods=['POST'])
      
def answer():
    question = request.form['question']
    response = handle_query(question)
    print("Generated SQL:", response) 
    return jsonify({'Your Question': question, 'Answer': response})  
    
def handle_query(question: str):
    sql_query = generate_sql("Translate this question into SQL: " + question)
    print("Generated SQL:", sql_query) 
    result = execute_sql(sql_query)
    return result if result else "No data found or error"
    


if __name__ == '__main__':
    app.run(debug=True)

