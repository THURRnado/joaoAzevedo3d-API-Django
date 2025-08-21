from django.urls import path
from . import views

urlpatterns = [
    path("api/objeto/<int:pk>/", views.dados_json_objeto, name="dados_json_objeto"),
]
