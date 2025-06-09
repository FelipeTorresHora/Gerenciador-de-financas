# Gerenciador de Orçamento

Um aplicativo web para gerenciamento de finanças pessoais com recursos de categorização de despesas, metas de gastos, e assistente financeiro baseado em IA.

## 📋 Sobre o Projeto

O Gerenciador de Orçamento é uma aplicação web desenvolvida com Django que permite ao usuário:

- Registrar receitas e despesas
- Visualizar saldo financeiro e balanço mensal
- Estabelecer metas de gastos por categoria
- Obter análises e recomendações financeiras através de um assistente de IA

## 🚀 Stack Tecnológica

### Backend
- **Python 3.8+**
- **Django 5.1.4** - Framework web
- **Sheet2API** - Armazenamento de dados em planilhas (como backend)
- **Sentence Transformers** - Para processamento de linguagem natural
- **FAISS** - Para indexação vetorial e busca eficiente
- **Google Gemini AI** - Para o assistente financeiro

### Frontend
- **HTML5 / CSS3**
- **Tailwind CSS** - Framework de estilos
- **JavaScript** - Vanilla JS para interatividade
- **Font Awesome** - Para ícones

## 📦 Pré-requisitos

- Python 3.8+
- pip (Gerenciador de pacotes Python)
- Chave de API do Google Gemini AI

## ⚙️ Instalação e Configuração

1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/gerenciador-orcamento.git
cd gerenciador-orcamento
```

2. **Configure o ambiente virtual**

```bash
# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Windows
venv\Scripts\activate
# No macOS/Linux
source venv/bin/activate
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
GEMINI_API_KEY=sua_chave_api_aqui
```

5. **Iniciar o servidor de desenvolvimento**

```bash
python manage.py migrate
python manage.py runserver
```

Após iniciar o servidor, acesse o aplicativo em: http://localhost:8000

## 🔧 Estrutura do Projeto

```
gerenciador_orcamento/     # Configuração principal do Django
  ├── settings.py          # Configurações do projeto
  ├── urls.py              # Rotas principais
  └── wsgi.py              # Configuração WSGI
  
orcamento/                 # Aplicativo principal
  ├── ia/                  # Módulos de IA
  │   └── agent.py         # Agente de IA Gemini
  ├── static/              # Arquivos estáticos
  │   ├── css/             # Estilos CSS
  │   └── js/              # JavaScript
  ├── templates/           # Templates HTML
  │   ├── index.html       # Página inicial
  │   ├── transacoes.html  # Página de transações
  │   └── ia_agent.html    # Página do assistente IA
  ├── urls.py              # Rotas da aplicação
  └── views.py             # Controladores da aplicação
```

## 🗄️ Armazenamento de Dados

O projeto utiliza o Sheet2API como backend de dados, conectando-se a uma planilha online para armazenar e recuperar informações financeiras. Isso elimina a necessidade de configurar um banco de dados tradicional.

## 🤖 Assistente de IA

O assistente financeiro integra a API Google Gemini para fornecer:

- Recomendações de investimento
- Análise de gastos
- Dicas para economia de dinheiro

A funcionalidade RAG (Retrieval Augmented Generation) permite que o assistente forneça recomendações personalizadas com base no histórico financeiro do usuário.

## 📱 Funcionalidades

### Página Inicial
- Visualização de saldo, receitas, despesas e economias
- Metas de gastos por categoria com barras de progresso
- Ações rápidas para acessar outras funcionalidades

### Gerenciador de Transações
- Formulário para adicionar novas transações (receitas ou despesas)
- Visualização em tabela de todas as transações
- Categorização de gastos

### Assistente Financeiro IA
- Interface de chat para conversar com o assistente
- Recomendações de investimento baseadas no perfil financeiro
- Sugestões para melhorar a saúde financeira