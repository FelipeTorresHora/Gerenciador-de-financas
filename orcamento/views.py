from django.http import JsonResponse
from django.shortcuts import render
import json
import requests
from django.conf import settings

def index(request):
    return render(request, "index.html")

def save_table(request):
    if request.method == "POST":
        data = json.loads(request.body)
        # Envia os dados para o Sheet2API
        response = requests.post(settings.SHEET2API_URL, json=data)
        if response.status_code == 200:
            return JsonResponse({"message": "Dados salvos com sucesso!"})
        return JsonResponse({"error": "Erro ao salvar os dados."}, status=400)

def update_chart(request):
    # Busca os dados do Sheet2API
    response = requests.get(settings.SHEET2API_URL)
    if response.status_code == 200:
        data = response.json()
        categories = [item["category"] for item in data]
        values = [item["value"] for item in data]
        return JsonResponse({"categories": categories, "values": values})
    return JsonResponse({"error": "Erro ao buscar os dados."}, status=400)