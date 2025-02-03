from django.http import JsonResponse
from django.shortcuts import render
import json
import logging
from sheet2api import Sheet2APIClient
from django.views.decorators.csrf import csrf_exempt
from calendar import monthrange

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


logger = logging.getLogger(__name__)

@csrf_exempt
def update_chart(request):
    try:
        # Configuração correta da API
        client = Sheet2APIClient(
            api_url="https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%C3%A1gina3"
        )
        
        # Obter dados SEM o parâmetro force_refresh
        rows = client.get_rows()  # Linha corrigida
        
        # Estruturas de dados
        annual_data = {str(year): 0 for year in range(2025, 2031)}
        monthly_data = {}
        category_data = {}
        daily_data = {}

        current_year = str(datetime.now().year)
        
        for row in rows:
            try:
                # Validação dos campos
                if not all(key in row for key in ["Data", "Valor", "Tipo", "Categoria"]):
                    continue

                # Processamento da data
                date_str = row['Data']
                day, month, year = date_str.split('/')
                
                # Converter valor
                valor = float(row['Valor'].replace('R$', '').replace(',', '.'))
                
                # Considerar apenas despesas
                if row['Tipo'].strip().lower() != 'despesa':
                    continue

                # Preencher estruturas de dados
                if year in annual_data:
                    annual_data[year] += valor
                
                key_month = f"{year}-{month}"
                if key_month not in monthly_data:
                    monthly_data[key_month] = 0
                monthly_data[key_month] += valor
                
                category = row['Categoria']
                if category not in category_data:
                    category_data[category] = 0
                category_data[category] += valor
                
                key_day = f"{day}/{month}/{year}"
                daily_data[key_day] = daily_data.get(key_day, 0) + valor

            except Exception as e:
                logger.error(f"Erro no processamento da linha: {str(e)}")
                continue

        return JsonResponse({
            'annual': annual_data,
            'monthly': monthly_data,
            'categories': category_data,
            'daily': daily_data,
            'last_update': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Erro geral: {str(e)}")
        return JsonResponse({"message": str(e)}, status=500)