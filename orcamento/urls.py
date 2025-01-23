from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('save/', views.save_table, name='save_table'),
    path('update-chart/', views.update_chart, name='update_chart'),
]
