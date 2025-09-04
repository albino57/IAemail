# 📧 IAemail - Classificador Inteligente de E-mails

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![IA](https://img.shields.io/badge/IA-Gemini%2BDeepSeek-orange)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Uma aplicação web que utiliza Inteligência Artificial para classificar e-mails em **Produtivos** ou **Improdutivos** e gerar respostas automáticas contextualizadas.

### 🌐 Acesse a Aplicação: [iaemail.vercel.app](https://iaemail.vercel.app/)

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
1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/albino57/IAemail.git
    cd IAemail
    ```
2.  **Configure o Backend:**
    ```bash
    cd Backend
    # Crie e ative o ambiente virtual
    python -m venv venv
    .\venv\Scripts\activate
    # Instale as dependências
    pip install -r requirements.txt
    # Configure suas chaves de API
    cp .env.example .env 
    ```
    Agora, abra o arquivo `.env` e preencha com suas chaves.

3.  **Configure o Frontend:**
    * Verifique se a URL da API no arquivo `Frontend/script.js` está apontando para `http://localhost:7860`.

4.  **Execute a Aplicação:**
    * **Terminal 1 (Backend):**
        ```bash
        cd Backend
        python app.py
        ```
    * **Terminal 2 (Frontend):**
        ```bash
        cd Frontend
        python -m http.server 8000
        ```
    Acesse `http://localhost:8000` no seu navegador.

## 📜 Licença
Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.