from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('save-expense/', views.save_expense, name='save_expense'),
    path('transacoes/', views.transacoes, name='transacoes'),  
    path('ia-agent/', views.ia_agent, name='ia_agent'),
]