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
    
    if request.method == 'GET':
       
        return redirect('/transacoes/')

    if request.method == 'POST':
        try:
            
            rows = client.get_rows()
            max_id = 0
            for row in rows:
                try:
                    rid = int(row.get('Id', 0))
                    max_id = max(max_id, rid)
                except (ValueError, TypeError):
                    continue

            
            data = {
                'Id': str(max_id + 1),
                'Valor': request.POST.get('Valor'),
                'Categoria': request.POST.get('Categoria'),
                'Data': request.POST.get('Data'),
                'Tipo': request.POST.get('Tipo'),
            }

            # Validação dos campos
            for field in ['Valor', 'Categoria', 'Data', 'Tipo']:
                if not data.get(field):
                    logger.error(f"Campo {field} ausente ou vazio")
                    return redirect('/transacoes/') 

            # Formatar Valor como número
            try:
                valor = float(data['Valor'].replace(',', '.').replace('R$', '').strip())
                data['Valor'] = f"R$ {valor:,.2f}".replace('.', ',')  
            except (ValueError, AttributeError):
                logger.error("Formato inválido para Valor")
                return redirect('/transacoes/') 

           
            logger.info(f"Payload enviado ao Sheet2API: {data}")

            
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
                return redirect('/transacoes/') 

            
            return redirect('/transacoes/')

        except Exception as e:
            logger.error(f"Erro geral em save_expense: {str(e)}")
            return redirect('/transacoes/')

    
    return redirect('/transacoes/')


def calculate_financial_profile(rows):
    """Calcula o perfil financeiro do usuário com base nas transações."""
    saldo = 0
    receitas = 0
    despesas = 0
    categorias = {}
    
    for row in rows:
        try:

            if not all(key in row for key in ["Valor", "Tipo", "Categoria"]):
                continue

            valor_str = row.get('Valor', '0').strip()

            if not valor_str:
                continue
            
            valor = float(valor_str.replace('R$', '').replace('.', '').replace(',', '.').strip())

            tipo_transacao = row.get('Tipo', '').strip().lower()
            
            if tipo_transacao == 'receita':
                receitas += valor
            elif tipo_transacao == 'despesa':
                despesas += valor
                
                categoria = row.get('Categoria', 'Outros').strip()
                categorias[categoria] = categorias.get(categoria, 0) + valor

        except (ValueError, KeyError, AttributeError) as e:
            
            logger.warning(f"Linha ignorada devido a erro de formato: {row}. Erro: {e}")
            continue
    
    saldo = receitas - despesas
    economia = saldo  
    
    top_categorias = [f"{cat} (R$ {val:,.2f})" for cat, val in sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:3]]
    
    return {
        'saldo': f"R$ {saldo:,.2f}",
        'receitas': f"R$ {receitas:,.2f}",
        'despesas': f"R$ {despesas:,.2f}",
        'economia': f"R$ {economia:,.2f}",
        'categorias': ', '.join(top_categorias).replace('.', ',') }
  
@csrf_exempt
def ia_agent(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            if not user_message:
                return JsonResponse({'error': 'Mensagem vazia'}, status=400)

            client = Sheet2APIClient(api_url="https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%C3%A1gina3")
            rows = client.get_rows()

            profile = calculate_financial_profile(rows)

            agent = GeminiAgent()
            agent.add_financial_profile(profile)

            
            context = agent.retrieve_context(user_message)
            response = agent.get_investment_advice_with_context(user_message, context)

            return JsonResponse({'response': response})

        except Exception as e:
            logger.error(f"Erro no RAG advice: {str(e)}")
            return JsonResponse({'error': f"Erro interno: {str(e)}"}, status=500)
            
   
    return render(request, "ia_agent.html")