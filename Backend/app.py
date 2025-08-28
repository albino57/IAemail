# Arquivo: backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS #comunicação entre domínios distintos
import requests #biblioteca do Python para fazer requisições HTTP
import os
import io
from dotenv import load_dotenv #biblioteca que lê e carrega variáveis em arquivo .env (segurança)
#↓↓Bibliotecas da ADOBE - conversão PDF↓↓
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult
#↑↑Bibliotecas da ADOBE - conversão PDF↑↑
import zipfile
import json

load_dotenv()

app = Flask(__name__)
CORS(app)  #Isso é crucial para o frontend se comunicar com o backend.

#↓↓-Função para ler ZIP-↓↓
def extract_text_from_zip(zip_content):
    """Extrai texto do ZIP retornado pela Adobe"""
    try:
        # Cria um arquivo ZIP em memória a partir dos bytes
        zip_file = zipfile.ZipFile(io.BytesIO(zip_content))
        
        # Encontra e lê o arquivo structuredData.json
        for file_name in zip_file.namelist():
            if file_name.endswith('structuredData.json'):
                with zip_file.open(file_name) as json_file:
                    data = json.load(json_file)
                    # Extrai TODO o texto do JSON
                    text = ""
                    for element in data.get('elements', []):
                        if 'Text' in element:
                            text += element['Text'] + "\n"
                    return text.strip()
        
        return "Texto não encontrado no ZIP"
    except Exception as e:
        print(f"Erro ao extrair texto do ZIP: {str(e)}")
        return None
#↑↑-Função para ler ZIP-↑↑

#↓↓↓-API ADOBE---------------------------------------------------------------------------------------↓↓↓
def extract_text_with_adobe(file_content):
    try:
        # 1. Configura as credenciais
        credentials = ServicePrincipalCredentials(
            client_id=os.getenv('PDF_SERVICES_CLIENT_ID'),
            client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET')
        )
        
        # 2. Cria instância do PDF Services
        pdf_services = PDFServices(credentials=credentials)
        
        # 3. Faz upload do arquivo para a nuvem da Adobe
        input_asset = pdf_services.upload(
            input_stream=file_content, 
            mime_type=PDFServicesMediaType.PDF
        )
        
        # 4. Configura parâmetros de extração (só texto)
        extract_pdf_params = ExtractPDFParams(
            elements_to_extract=[ExtractElementType.TEXT],
        )
        
        # 5. Cria e executa o job
        extract_pdf_job = ExtractPDFJob(
            input_asset=input_asset, 
            extract_pdf_params=extract_pdf_params
        )
        
        location = pdf_services.submit(extract_pdf_job)
        result = pdf_services.get_job_result(location, ExtractPDFResult)
        
        # 6. Baixa o resultado (ZIP)
        result_asset = result.get_result().get_resource()
        stream_asset = pdf_services.get_content(result_asset)
        zip_content = stream_asset.get_input_stream()
        
        # 7. Extrai o texto do ZIP (você precisará implementar)
        text = extract_text_from_zip(zip_content)
        return text
        
    except Exception as e:
        print(f"Erro na extração Adobe: {str(e)}")
        return None
#↑↑↑-API ADOBE---------------------------------------------------------------------------------------↓↓↓

#↓↓↓-API GEMINI---------------------------------------------------------------------------------------↓↓↓
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")     #Variável recebe a chave API Gemini
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

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
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") 
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
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
    return "🔥Backend IAemail está funcionando🔥"


#↓↓-Função para processar o PDF-↓↓
@app.route('/analyze_file', methods=['POST'])
def analyze_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio.'}), 400

    text = ""
    try:
        if file.filename.endswith('.pdf'):
            try:
                file_content = file.read()  # Lê o conteúdo do arquivo PDF
                text = extract_text_with_adobe(file_content)
                if text is None:
                    return jsonify({'error': 'Falha ao extrair texto do PDF.'}), 500
            except Exception as e:
                return jsonify({'error': f'Erro ao processar PDF: {str(e)}'}), 500
            
        elif file.filename.endswith('.txt'):
            text = file.read().decode('utf-8')# Lê texto diretamente do TXT
        else:
            return jsonify({'error': 'Formato de arquivo não suportado.'}), 400
        
        return jsonify({
            'text': text  # Retorna o texto extraído para o frontend
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao processar o arquivo: {str(e)}'}), 500
#↑↑-Função para processar o PDF-↑↑


#↓↓-Função da comunicação entre o frontend JS, python e API IA-----------------------------------↓↓
@app.route('/analyze', methods=['POST'])  #Nova rota para analisar o email que aceita apenas 'POST'.
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
#↑↑-Função da comunicação entre o frontend JS, python e API IA-----------------------------------↑↑

if __name__ == '__main__':
    app.run(debug=True)