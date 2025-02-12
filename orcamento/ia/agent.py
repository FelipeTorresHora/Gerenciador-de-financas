import os
import requests
from django.conf import settings

class DeepSeekAgent:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
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
                    "content": "Você é um especialista em finanças e investimentos. Forneça conselhos claros e práticos. Use termos simples e exemplos quando apropriado. Formate as respostas em HTML simples com parágrafos e listas."
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