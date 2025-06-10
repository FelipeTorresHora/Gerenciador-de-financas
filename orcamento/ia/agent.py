import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import google.generativeai as genai

class GeminiAgent:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(384)  # Dimensão do modelo MiniLM
        self.documents = []

    def add_financial_profile(self, profile_data):
        """Adiciona o perfil financeiro ao índice FAISS."""
        profile_str = (
            f"Saldo: {profile_data['saldo']}, "
            f"Receitas: {profile_data['receitas']}, "
            f"Despesas: {profile_data['despesas']}, "
            f"Economia: {profile_data['economia']}, "
            f"Categorias: {profile_data['categorias']}"
        )
        embedding = self.embedding_model.encode([profile_str])[0]
        self.index.add(np.array([embedding]))
        self.documents.append(profile_data)

    def retrieve_context(self, query):
        """Recupera o contexto financeiro mais relevante."""
        query_embedding = self.embedding_model.encode([query])[0]
        _, indices = self.index.search(np.array([query_embedding]), k=1)
        return self.documents[indices[0][0]] if indices[0][0] < len(self.documents) else {}


    def get_investment_advice_with_context(self, user_message, context):
        prompt = f'''
        Atue como um especialista em finanças e investimentos. 
        Se a pessoa tem dívidas, sempre aconselhe primeiro a quitar todas suas dívidas para depois investir.
        Analise o perfil do usuário e sugira um investimento adequado (Arrojado, equilibrado ou conservador).
        Mostre várias formas de investir, como ações, criptomoedas, tesouro direto...
        Use termos simples e exemplos apropriados para a situação. 
        Formate as respostas em parágrafos explicativos(<p>) e listas (<ul><li>).
        
        **Contexto Financeiro do Usuário**:
        - Saldo Total: {context.get('saldo', 'R$ 0,00')}
        - Receitas Mensais: {context.get('receitas', 'R$ 0,00')}
        - Despesas Mensais: {context.get('despesas', 'R$ 0,00')}
        - Economia Atual: {context.get('economia', 'R$ 0,00')}
        - Principais Categorias de Gastos: {context.get('categorias', 'Nenhuma')}

        **Pergunta do Usuário**:
        {user_message}
        '''

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"<p>Erro ao consultar a API do Gemini: {str(e)}</p>"

    def get_investment_advice(self, user_message):
        # Para compatibilidade com chamadas antigas
        return self.get_investment_advice_with_context(user_message, {})