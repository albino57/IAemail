# Arquivo: backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  #Isso é crucial para o frontend se comunicar com o backend.

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")     #Variável recebe a chave API Gemini
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") #Variável recebe a chave API DeepSeek

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

#↓↓↓-API GEMINI---------------------------------------------------------------------------------------↓↓↓
def query_gemini(prompt, max_tokens=150):
    """Consulta a API do Google Gemini (FREE)."""
    if not GEMINI_API_KEY:
        print("Erro: Chave da Gemini não configurada.")
        return None

    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"Erro ao chamar Gemini API: {e}")
        return None
#↑↑↑-API GEMINI---------------------------------------------------------------------------------------↑↑↑

#↓↓↓-API DEEPSEEK---------------------------------------------------------------------------------------↓↓↓
def query_deepseek(prompt, max_tokens=150):
    """Consulta a API da DeepSeek (BACKUP)."""
    if not DEEPSEEK_API_KEY:
        print("Erro: Chave da DeepSeek não configurada.")
        return None

    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    } 

    try:
        response = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Erro ao chamar DeepSeek API: {e}")
        return None
#↑↑↑-API DEEPSEEK---------------------------------------------------------------------------------------↑↑↑

def query_ai(prompt, max_tokens=150):
    """Estratégia de failover: tenta Gemini primeiro, depois DeepSeek."""
    print("Tentando Gemini...")
    result = query_gemini(prompt, max_tokens)
    
    if result is not None:
        return result
    
    print("Gemini falhou. Tentando DeepSeek...")
    return query_deepseek(prompt, max_tokens)

@app.route('/')
def home():
    return "🔥Backend da IAemail está funcionando🔥"

# NOVA ROTA PARA ANALISAR O EMAIL
@app.route('/analyze', methods=['POST'])  # Aceita apenas POST.

def analyze_email():
    data = request.get_json() #Pega o JSON recebido e transforma em um dicionário Python
    email_text = data.get('text', '')  # Extrai o valor da chave 'text' do dicionário e não tiver 'text', retorna string vazio.

    #Validar se o texto não está vazio
    if not email_text.strip():
        # Se estiver vazio, retorna um erro JSON
        return jsonify({'error': 'O texto do e-mail não pode estar vazio.'}), 400

    #Prompt para CLASSIFICAR o e-mail
    classification_prompt = f"""
    Classifique o seguinte e-mail como 'Produtivo' ou 'Improdutivo'. 
    Responda APENAS com uma palavra: 'Produtivo' ou 'Improdutivo'.

    E-mail: \"\"\"{email_text}\"\"\"
    Classificação:
    """

    category = query_ai(classification_prompt, max_tokens=10)

    #Prompt para GERAR uma resposta baseada na classificação
    response_prompt = f"""
    Este e-mail foi classificado como '{category}'. Gere uma resposta automática, curta e adequada em português do Brasil.

    E-mail: \"\"\"{email_text}\"\"\"

    Resposta:
    """

    generated_response = query_ai(response_prompt, max_tokens=150)

    #Verifica se a API retornou algo
    if category is None or generated_response is None:
        return jsonify({'error': 'Erro ao processar sua solicitação com a IA.'}), 500

    #Retorna a resposta real da IA!
    return jsonify({
        'category': category,
        'response': generated_response
    })

if __name__ == '__main__':
    app.run(debug=True)