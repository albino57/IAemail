# Arquivo: backend/app.py
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Isso é crucial para o frontend se comunicar com o backend!

@app.route('/')
def home():
    return "🔥 Backend da IAemail está funcionando! 🔥"

if __name__ == '__main__':
    app.run(debug=True)