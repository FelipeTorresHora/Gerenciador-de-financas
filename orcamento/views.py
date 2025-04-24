import json
import logging
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from orcamento.ia.agent import GeminiAgent
from sheet2api import Sheet2APIClient
from django.views.decorators.csrf import csrf_exempt, csrf_protect

logger = logging.getLogger(__name__)

def index(request):
    return render(request, "index.html")

def transacoes(request):
    try:
        client = Sheet2APIClient(
            api_url="https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%C3%A1gina3"
        )
        rows = client.get_rows()
        
        transactions = []
        for row in rows:
            try:
                if not all(key in row for key in ["Data", "Tipo", "Valor", "Categoria"]):
                    continue
                    
                transactions.append({
                    "Valor": row["Valor"],
                    "Categoria": row["Categoria"],
                    "Data": row["Data"],
                    "Tipo": row["Tipo"],
                })
            except Exception as e:
                logger.error(f"Erro ao processar linha: {str(e)}")
                continue
                
        context = {
            "transactions": json.dumps(transactions)
        }
        
        return render(request, "transacoes.html", context)
        
    except Exception as e:
        logger.error(f"Erro ao carregar transações: {str(e)}")
        return render(request, "transacoes.html", {"error": str(e)})

@csrf_protect
def save_expense(request):
    client = Sheet2APIClient(
        api_url="https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%C3%A1gina3"
    )
    rows = client.get_rows()
    max_id = 0
    for row in rows:
        try:
            rid = int(row.get('Id', 0))
            max_id = max(max_id, rid)
        except (ValueError, TypeError):
            continue

    if request.method == 'GET':
        return JsonResponse({'next_id': str(max_id + 1)})

    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = {
                    'Valor': request.POST.get('Valor'),
                    'Categoria': request.POST.get('Categoria'),
                    'Data': request.POST.get('Data'),
                    'Tipo': request.POST.get('Tipo'),
                }
            data['Id'] = str(max_id + 1)

            # Validação dos campos
            for field in ['Valor', 'Categoria', 'Data', 'Tipo']:
                if not data.get(field):
                    logger.error(f"Campo {field} ausente ou vazio")
                    return JsonResponse({'message': f"Campo {field} é obrigatório"}, status=400)

            # Formatar Valor como número
            try:
                valor = float(data['Valor'].replace(',', '.').replace('R$', '').strip())
                data['Valor'] = f"R$ {valor:,.2f}".replace('.', ',')  # Formato "R$ 100,00"
            except (ValueError, AttributeError):
                logger.error("Formato inválido para Valor")
                return JsonResponse({'message': "Formato inválido para Valor"}, status=400)

            # Logar payload para depuração
            logger.info(f"Payload enviado ao Sheet2API: {data}")

            # Criar a linha usando requisição HTTP direta
            try:
                response = requests.post(
                    "https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%C3%A1gina3",
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                logger.info("Linha criada com sucesso")
            except requests.RequestException as e:
                logger.error(f"Erro ao criar linha no Sheet2API: {str(e)}")
                return JsonResponse({'message': f"Erro ao salvar na planilha: {str(e)}"}, status=500)

            return JsonResponse({'message': 'Transação salva com sucesso!', 'next_id': data['Id']})
        except Exception as e:
            logger.error(f"Erro geral em save_expense: {str(e)}")
            return JsonResponse({'message': f"Erro interno: {str(e)}"}, status=500)

    return JsonResponse({'message': 'Método não permitido'}, status=405)

@csrf_exempt
def delete_transaction(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        client = Sheet2APIClient(
            api_url="https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%C3%A1gina3"
        )
        if action == 'add':
            data = {
                'Id': request.POST.get('Id'),
                'Valor': request.POST.get('Valor'),
                'Categoria': request.POST.get('Categoria'),
                'Data': request.POST.get('Data'),
                'Tipo': request.POST.get('Tipo')
            }
            try:
                response = requests.post(
                    "https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%C3%A1gina3",
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Erro ao adicionar transação: {str(e)}")
        elif action == 'delete':
            id_to_delete = request.POST.get('Id')
            rows = client.get_rows()
            for i, row in enumerate(rows):
                if str(row.get('Id')) == str(id_to_delete):
                    try:
                        client.update_row(i + 2, {})
                    except Exception as e:
                        logger.error(f"Erro ao deletar transação: {str(e)}")
                    break
        return redirect('transacoes')
    return redirect('transacoes')

@csrf_exempt
def manage_transaction(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        client = Sheet2APIClient(
            api_url="https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%C3%A1gina3"
        )
        if action == 'add':
            data = {
                'Id': request.POST.get('Id'),
                'Valor': request.POST.get('Valor'),
                'Categoria': request.POST.get('Categoria'),
                'Data': request.POST.get('Data'),
                'Tipo': request.POST.get('Tipo')
            }
            try:
                response = requests.post(
                    "https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%C3%A1gina3",
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Erro ao adicionar transação: {str(e)}")
        elif action == 'delete':
            id_to_delete = request.POST.get('Id')
            rows = client.get_rows()
            for i, row in enumerate(rows):
                if str(row.get('Id')) == str(id_to_delete):
                    try:
                        client.update_row(i + 1, {})
                    except Exception as e:
                        logger.error(f"Erro ao deletar transação: {str(e)}")
                    break
        return redirect('transacoes')
    return redirect('transacoes')

def calculate_financial_profile(rows):
    """Calcula o perfil financeiro do usuário com base nas transações."""
    saldo = 0
    receitas = 0
    despesas = 0
    categorias = {}
    
    for row in rows:
        try:
            valor = float(row['Valor'].replace('R$', '').replace(',', '.').strip())
            if row['Tipo'] == 'Receita':
                receitas += valor
            elif row['Tipo'] == 'Despesa':
                despesas += valor
                categorias[row['Categoria']] = categorias.get(row['Categoria'], 0) + valor
        except (ValueError, KeyError):
            continue
    
    saldo = receitas - despesas
    economia = receitas * 0.1
    top_categorias = [f"{cat} (R$ {val:.2f})" for cat, val in sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:3]]
    
    return {
        'saldo': f"R$ {saldo:,.2f}".replace('.', ','),
        'receitas': f"R$ {receitas:,.2f}".replace('.', ','),
        'despesas': f"R$ {despesas:,.2f}".replace('.', ','),
        'economia': f"R$ {economia:,.2f}".replace('.', ','),
        'categorias': ', '.join(top_categorias)
    }
  
@csrf_exempt
def ia_agent(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message:
                return JsonResponse({'error': 'Mensagem vazia'}, status=400)
            
            agent = GeminiAgent()
            response = agent.get_investment_advice(user_message)
            
            return JsonResponse({'response': response})
        
        except Exception as e:
            logger.error(f"Erro no agente IA: {str(e)}")
            return JsonResponse({'error': 'Erro interno'}, status=500)
    
    return render(request, "ia_agent.html")    
    
