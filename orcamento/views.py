from django.http import JsonResponse
from django.shortcuts import render
import json
import logging
from sheet2api import Sheet2APIClient
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

def index(request):
    return render(request, "index.html")

def transacoes(request):
    return render(request, "transacoes.html")

@csrf_exempt
def save_expense(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validação dos campos
            required_fields = ['Valor', 'Categoria', 'Data', 'Tipo']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'message': f'Campo {field} é obrigatório'}, status=400)

            # Validação do valor
            try:
                valor = float(data['Valor'])
                if valor < 0:
                    return JsonResponse({'message': 'O valor não pode ser negativo'}, status=400)
            except ValueError:
                return JsonResponse({'message': 'Valor inválido'}, status=400)

            # Salvar na planilha
            client = Sheet2APIClient(api_url='https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%25C3%25A1gina3')
            client.create_row(data)
            
            return JsonResponse({'message': 'Dados salvos com sucesso!'})

        except Exception as e:
            logger.error(f"Erro ao salvar dados: {str(e)}")
            return JsonResponse({'message': 'Erro ao salvar dados'}, status=500)

    return JsonResponse({'message': 'Método não permitido'}, status=405)

def update_chart(request):
    try:
        month = request.GET.get('month')
        year = request.GET.get('year')
        
        # Buscar dados da planilha
        client = Sheet2APIClient(api_url='https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%25C3%25A1gina3')
        rows = client.get_rows()
        
        # Filtrar por mês e ano se fornecidos
        filtered_rows = []
        for row in rows:
            try:
                # Verificar se a data está no formato correto e dividir
                date_parts = row['Data'].split('-')
                if len(date_parts) == 3:  # Verifica se a data tem dia, mês e ano
                    day, month_data, year_data = date_parts
                    if month and year:
                        # Filtrar por mês e ano
                        if month_data == month and year_data == year:
                            filtered_rows.append(row)
                    else:
                        # Se não houver filtro, incluir todas as linhas
                        filtered_rows.append(row)
            except (KeyError, AttributeError):
                # Ignorar linhas com dados inválidos ou sem data
                continue

        # Processar dados para os gráficos
        daily_data = {}
        category_data = {}
        monthly_total = 0

        for row in filtered_rows:
            # Dados diários
            date = row['Data']
            tipo = row['Tipo']
            
            # Limpar o valor e converter para float
            valor_str = row['Valor'].replace('R$', '').replace('.', '').replace(',', '.').strip()
            valor = float(valor_str)
            
            if date not in daily_data:
                daily_data[date] = {'Despesa': 0, 'Receita': 0}
            daily_data[date][tipo] += valor

            # Dados por categoria
            if tipo == 'Despesa':
                category = row['Categoria']
                category_data[category] = category_data.get(category, 0) + valor

            # Total mensal
            if tipo == 'Receita':
                monthly_total += valor

        return JsonResponse({
            'daily': daily_data,
            'categories': category_data,
            'monthly_total': monthly_total
        })

    except Exception as e:
        logger.error(f"Erro ao buscar dados: {str(e)}")
        return JsonResponse({'message': 'Erro ao buscar dados'}, status=500)