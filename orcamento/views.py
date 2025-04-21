from django.http import JsonResponse
from django.shortcuts import render, redirect
import json
import logging
from  orcamento.ia.agent import DeepSeekAgent
from sheet2api import Sheet2APIClient
from django.views.decorators.csrf import csrf_exempt, csrf_protect 

logger = logging.getLogger(__name__)

def index(request):
    return render(request, "index.html")

def transacoes(request):
    try:
        client = Sheet2APIClient(
            api_url="https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%25C3%25A1gina3"
        )
        rows = client.get_rows()
        
        # Processar os dados para o formato especificado
        transactions = []
        for row in rows:
            try:
                if not all(key in row for key in ["Data", "Tipo", "Valor", "Categoria"]):
                    continue
                    
                transactions.append({
                    "Valor": row["Valor"],  # Manter o formato exato, ex.: "R$ 699,00"
                    "Categoria": row["Categoria"],
                    "Data": row["Data"],  # Ex.: "06/02/2025"
                    "Tipo": row["Tipo"],
                    "Descricao": row.get("Descricao", "Sem descrição"),
                    "Observacoes": row.get("Observacoes", "")
                })
            except Exception as e:
                logger.error(f"Erro ao processar linha: {str(e)}")
                continue
                
        context = {
            "transactions": json.dumps(transactions)  # Passar como JSON para o frontend
        }
        
        return render(request, "transacoes.html", context)
        
    except Exception as e:
        logger.error(f"Erro ao carregar transações: {str(e)}")
        return render(request, "transacoes.html", {"error": str(e)})

@csrf_exempt
def save_expense(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validação dos campos
            required_fields = ["Valor", "Categoria", "Data", "Tipo"]
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse(
                        {"message": f"Campo {field} é obrigatório"}, status=400
                    )

            # Validação do valor (remover "R$" para verificar, mas salvar com "R$")
            try:
                valor_str = data["Valor"].replace("R$", "").replace(".", "").replace(",", ".").strip()
                valor = float(valor_str)
                if valor < 0:
                    return JsonResponse(
                        {"message": "O valor não pode ser negativo"}, status=400
                    )
                # Reformatar o valor para o formato brasileiro com "R$"
                data["Valor"] = f"R$ {valor:,.2f}".replace(".", ",")
            except ValueError:
                return JsonResponse({"message": "Valor inválido"}, status=400)

            # Salvar na planilha
            client = Sheet2APIClient(
                api_url="https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%25C3%25A1gina3"
            )
            client.create_row(data)

            return JsonResponse({"message": "Dados salvos com sucesso!"})

        except Exception as e:
            logger.error(f"Erro ao salvar dados: {str(e)}")
            return JsonResponse({"message": "Erro ao salvar dados"}, status=500)

    return JsonResponse({"message": "Método não permitido"}, status=405)

@csrf_exempt
def delete_transaction(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        client = Sheet2APIClient(
            api_url="https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%25C3%25A1gina3"
        )
        if action == 'add':
            data = {
                'Id': request.POST.get('Id'),
                'Valor': request.POST.get('Valor'),
                'Categoria': request.POST.get('Categoria'),
                'Data': request.POST.get('Data'),
                'Tipo': request.POST.get('Tipo')
            }
            client.create_row(data)
        elif action == 'delete':
            id_to_delete = request.POST.get('Id')
            rows = client.get_rows()
            for i, row in enumerate(rows):
                if str(row.get('Id')) == str(id_to_delete):
                    client.update_row(i + 2, {})
                    break
        return redirect('transacoes')
    return redirect('transacoes')

@csrf_exempt
def manage_transaction(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        client = Sheet2APIClient(
            api_url="https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%25C3%25A1gina3"
        )
        if action == 'add':
            data = {
                'Id': request.POST.get('Id'),
                'Valor': request.POST.get('Valor'),
                'Categoria': request.POST.get('Categoria'),
                'Data': request.POST.get('Data'),
                'Tipo': request.POST.get('Tipo')
            }
            client.create_row(data)
        elif action == 'delete':
            id_to_delete = request.POST.get('Id')
            rows = client.get_rows()
            for i, row in enumerate(rows):
                if str(row.get('Id')) == str(id_to_delete):
                    client.update_row(i + 1, {})  # Ajustado: i+1 pois o índice da linha é relativo, mesmo Id estando na coluna 5
                    break
        return redirect('transacoes')
    return redirect('transacoes')

@csrf_exempt
def ia_agent(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message:
                return JsonResponse({'error': 'Mensagem vazia'}, status=400)
            
            agent = DeepSeekAgent()
            response = agent.get_investment_advice(user_message)
            
            return JsonResponse({'response': response})
        
        except Exception as e:
            logger.error(f"Erro no agente IA: {str(e)}")
            return JsonResponse({'error': 'Erro interno'}, status=500)
    
    return render(request, "ia_agent.html")