from django.http import JsonResponse
from django.shortcuts import render
import json
import logging
from sheet2api import Sheet2APIClient
from django.views.decorators.csrf import csrf_exempt
from calendar import monthrange
from orcamento.ia.agent import DeepSeekAgent

logger = logging.getLogger(__name__)


def index(request):
    return render(request, "index.html")


def transacoes(request):
    return render(request, "transacoes.html")


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

            # Validação do valor
            try:
                valor = float(data["Valor"])
                if valor < 0:
                    return JsonResponse(
                        {"message": "O valor não pode ser negativo"}, status=400
                    )
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


def update_chart(request):
    try:
        month = request.GET.get("month")
        year = request.GET.get("year")

        client = Sheet2APIClient(
            api_url="https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%25C3%25A1gina3"
        )
        rows = client.get_rows()

        daily_data = {}
        category_data = {}
        monthly_total = 0

        for row in rows:
            try:
                if not all(key in row for key in ["Data", "Tipo", "Valor", "Categoria"]):
                    continue

                # Corrigido: Split por '-' para datas no formato DD-MM-YYYY
                date_str = row["Data"]
                day, month_data, year_data = date_str.split("/")

                # Filtro por mês/ano
                if month and year:
                    if int(month_data) != int(month) or int(year_data) != int(year):
                        continue

                tipo = row["Tipo"].strip().lower()
                if tipo in ["receita", "receitas"]:
                    tipo = "Receita"
                elif tipo in ["despesa", "despesas"]:
                    tipo = "Despesa"
                else:
                    continue

                valor_str = (
                    row["Valor"]
                    .replace("R$", "")
                    .replace(".", "")
                    .replace(",", ".")
                    .strip()
                )
                valor = float(valor_str)

                # Formato da chave mantido como DD/MM/YYYY
                date_key = f"{day}/{month_data}/{year_data}"
                if date_key not in daily_data:
                    daily_data[date_key] = {"Despesa": 0, "Receita": 0}
                daily_data[date_key][tipo] += valor

                if tipo == "Despesa":
                    category = row["Categoria"]
                    category_data[category] = category_data.get(category, 0) + valor

                if tipo == "Receita":
                    monthly_total += valor

            except Exception as e:
                logger.error(f"Erro na linha {row}: {str(e)}")
                continue

        # Movido para fora do loop: Preenchimento dos dias do mês
        if month and year:
            _, last_day = monthrange(int(year), int(month))
            ordered_daily = {}
            for day in range(1, last_day + 1):
                # Formata dia e mês com dois dígitos
                formatted_day = f"{day:02d}"
                formatted_month = f"{int(month):02d}"
                date_key = f"{formatted_day}/{formatted_month}/{year}"
                ordered_daily[date_key] = daily_data.get(
                    date_key, {"Despesa": 0, "Receita": 0}
                )
            daily_data = ordered_daily
        else:
            sorted_dates = sorted(
                daily_data.keys(),
                key=lambda x: tuple(map(int, x.split("/")[::-1]))
            )
            daily_data = {date: daily_data[date] for date in sorted_dates}

        return JsonResponse({
            "daily": daily_data,
            "categories": category_data,
            "monthly_total": monthly_total
        })

    except Exception as e:
        logger.error(f"Erro geral: {str(e)}")
        return JsonResponse({"message": "Erro ao buscar dados"}, status=500)
    
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