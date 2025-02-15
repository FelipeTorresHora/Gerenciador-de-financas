import requests
import os
from dotenv import load_dotenv

class DeepSeekAgent:
    def __init__(self):
        load_dotenv()  # Carrega variáveis do .env
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1/chat/completions"

    def get_investment_advice(self, user_message):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": ''' Você é um especialista em finanças e investimentos. 
                    Se a pessoa tem dividas, sempre aconselhe primeiro a quitar todas suas dividas para depois investir.
                    Analise o perfil do usuário e sugira um investimento adequado (Arrojado, equilibrado ou conservador).
                    Mostre várias formas de investir, como ações, criptomoedas, tesouro direto...
                    Use termos simples e exemplos quando apropriado. 
                    Formate as respostas em HTML simples com parágrafos e listas.'''
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "temperature": 1.1
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Erro ao consultar a API: {str(e)}"