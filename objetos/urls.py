from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("api/objeto/<int:pk>/", views.dados_json_objeto, name="dados_json_objeto"),
    path("", views.home, name='home'),
    path("sobre/", views.about, name='about'),
    path("objetos/", views.listar_objetos, name='listar_objetos'),
    path("objetos/<int:pk>/", views.visualizar_objeto, name='visualizar_objeto'),
    path("objetos/adicionar", views.adicionar_objeto, name='adicionar_objeto'),
    path("objetos/<int:pk>/editar/", views.editar_objeto, name='editar_objeto'),
    path("objetos/<int:pk>/remover/", views.remover_objeto, name="remover_objeto"),
    path("objetos/pdf/", views.gerar_pdf_objetos, name="pdf_objetos"),

    path("relatorio/", views.relatorio_registros, name="relatorio_registros"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)