# Arquivo: backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS #comunicação entre domínios distintos
import requests #biblioteca do Python para fazer requisições HTTP
import os
from dotenv import load_dotenv #biblioteca que lê e carrega variáveis em arquivo .env (segurança)

load_dotenv()

app = Flask(__name__)
CORS(app)  #Isso é crucial para o frontend se comunicar com o backend.

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")     #Variável recebe a chave API Gemini
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") 

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

@app.route('/') #Função para saber se a rota básica está funcionando.
def home():
    return "🔥Backend da IAemail está funcionando🔥"

# NOVA ROTA PARA ANALISAR O EMAIL
@app.route('/analyze', methods=['POST'])  # Aceita apenas POST.

#↓↓↓-Função da comunicação entre o frontend JS, python e API IA-----------------------------------↓↓↓
def analyze_email():
    data = request.get_json() #Pega o JSON recebido e transforma em um dicionário Python
    email_text = data.get('text', '')  # Extrai o valor da chave 'text' do dicionário e se não tiver 'text', retorna string vazio.

    #Validar se o texto não está vazio
    if not email_text.strip():
        # Se estiver vazio, retorna um erro JSON
        return jsonify({'error': 'O texto do e-mail não pode estar vazio.'}), 400

    #Prompt para o e-mail
    unified_prompt = f"""
    Classifique o e-mail abaixo como 'Produtivo' ou 'Improdutivo' e gere uma resposta automática curta e adequada em português do Brasil.

    Retorne APENAS no seguinte formato, sem comentários extras:
    Categoria: [Produtivo/Improdutivo]
    Resposta: [sua resposta aqui]

    E-mail: \"\"\"{email_text}\"\"\"
    """

    #Faz apenas uma chamada para a IA
    ai_response = query_ai(unified_prompt, max_tokens=200)

    #Extraindo a categoria e a resposta do texto que voltou
    if ai_response:
        
        #Divide a resposta em linhas
        lines = ai_response.split('\n')
        category = None
        response_text = None
    
        for line in lines:
            if line.startswith('Categoria:'): #Se achar 'Categoria:'
                category = line.replace('Categoria:', '').strip() #Aqui lê a palavra depois da Categoria
            elif line.startswith('Resposta:'):
                response_text = line.replace('Resposta:', '').strip()
    
        #Verifica se encontrou ambas as respostas e retorna para o JS
        if category and response_text:
            return jsonify({
                'category': category,
                'response': response_text
            })
        else:
            return jsonify({'error': 'Não foi possível processar a resposta da IA.'}), 500
    else:
        return jsonify({'error': 'Erro ao processar sua solicitação com a IA.'}), 500
#↑↑↑-Função da comunicação entre o frontend JS, python e API IA-----------------------------------↑↑↑

if __name__ == '__main__':
    app.run(debug=True)