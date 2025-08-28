# 📧 IAemail - Classificador Inteligente de E-mails

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![IA](https://img.shields.io/badge/IA-Gemini%2BDeepSeek-orange)

Uma aplicação web que utiliza Inteligência Artificial para classificar e-mails em **Produtivos** ou **Improdutivos** e gerar respostas automáticas contextualizadas.

## 🚀 Funcionalidades

- ✅ **Classificação Automática**: Identifica se e-mails requerem ação ou são apenas informativos
- 💬 **Respostas Contextuais**: Gera respostas personalizadas usando IA generativa
- 📎 **Suporte a Arquivos**: Processa tanto texto direto quanto arquivos **TXT e PDF**
- 🔄 **Failover Inteligente**: Usa Gemini API como primária e DeepSeek como backup
- 🎨 **Interface Responsiva**: Design limpo e intuitivo para qualquer dispositivo

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python + Flask
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **IA**: Google Gemini API + DeepSeek API (fallback)
- **PDF Processing**: Adobe PDF Services API
- **Deploy**: Vercel (Frontend) + Hugging Face Spaces (Backend)
- **Versionamento**: Git + GitHub

## 📦 Como Executar Localmente

### Pré-requisitos
- Python 3.10+
- Conta no [Google AI Studio](https://aistudio.google.com/)
- Conta no [Adobe PDF Services](https://www.adobe.io/apis/documentcloud/dcsdk/pdf-services.html)

### Instalação
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/IAemail.git
cd IAemail

# Backend
cd Backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Configure as variáveis de ambiente no arquivo .env:
# GEMINI_API_KEY=sua_chave_gemini
# DEEPSEEK_API_KEY=sua_chave_deepseek  
# PDF_SERVICES_CLIENT_ID=sua_chave_adobe
# PDF_SERVICES_CLIENT_SECRET=sua_secret_adobe

# Execute o backend
python app.py

# Frontend (em outro terminal)
cd Frontend
python -m http.server 8000