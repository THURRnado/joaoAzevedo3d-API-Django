from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Objeto, RegistroAcao
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .forms import ObjetoForm
from django.http import HttpResponse
from django.core.paginator import Paginator
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import logging
import os


logger = logging.getLogger('objetos')


def is_admin(user):
    return user.is_staff or user.is_superuser


# Create your views here.
def dados_json_objeto(request, pk):
    try:
        objeto = get_object_or_404(Objeto, pk=pk)
        
        image_url = request.build_absolute_uri(objeto.img_object.url) if objeto.img_object else None

        data = {
            "id": objeto.id,
            "name": objeto.name,
            "description": objeto.description,
            "image": image_url,
            "user": objeto.user.username,
            "dt_object": objeto.dt_object.strftime("%Y-%m-%d"),
            "dt_create": objeto.dt_create.strftime("%Y-%m-%d %H:%M:%S"),
            "dt_modified": objeto.dt_modified.strftime("%Y-%m-%d %H:%M:%S"),
        }

        logger.info(f'JSON do objeto {pk} solicitado por usuário {request.user.username}')
        return JsonResponse(data, json_dumps_params={"ensure_ascii": False})
    
    except Exception as e:
        logger.error(f'Erro ao gerar JSON do objeto {pk}: {e}', exc_info=True)
        return JsonResponse({'error': 'Erro ao carregar dados'}, status=500)


@login_required
def gerar_pdf_objetos(request):
    try:
        logger.info(f'Iniciando geração de PDF por usuário {request.user.username}')
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="objetos.pdf"'

        doc = SimpleDocTemplate(response, pagesize=A4)
        story = []

        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        text_style = styles["Normal"]

        # Título
        story.append(Paragraph("Objetos João Azevedo", title_style))
        story.append(Spacer(1, 20))

        # Buscar objetos com select_related para otimizar
        objetos = Objeto.objects.select_related('user').all()
        logger.debug(f'Total de {objetos.count()} objetos para incluir no PDF')

        # Loop dos objetos
        for index, obj in enumerate(objetos):
            
            # Alternância de cor
            bg_color = colors.whitesmoke if index % 2 == 0 else colors.Color(0.85, 0.92, 1)

            # Imagem com tratamento de erro
            if obj.img_object and os.path.exists(obj.img_object.path):
                try:
                    img = Image(obj.img_object.path, width=1.5*inch, height=1.5*inch)
                except Exception as img_error:
                    logger.warning(f'Erro ao carregar imagem do objeto {obj.id}: {img_error}')
                    img = Paragraph("<i>Erro ao carregar imagem</i>", text_style)
            else:
                img = Paragraph("<i>Sem imagem</i>", text_style)

            # Dados do objeto
            info = Paragraph(
                f"""
                <b>Nome:</b> {obj.name}<br/>
                <b>Descrição:</b> {obj.description or '---'}<br/>
                <b>Data do objeto:</b> {obj.dt_object.strftime('%d/%m/%Y') if obj.dt_object else '---'}
                """,
                text_style
            )

            # Tabela
            bloco = Table(
                [[img, info]],
                colWidths=[120, 400],
                rowHeights=[120]
            )

            bloco.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), bg_color),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))

            story.append(bloco)
            story.append(Spacer(1, 15))

        doc.build(story)
        logger.info(f'PDF gerado com sucesso por usuário {request.user.username}')
        return response

    except Exception as e:
        logger.error(f'Erro ao gerar PDF: {e}', exc_info=True)
        messages.error(request, 'Ocorreu um erro ao gerar o PDF.')
        return redirect('listar_objetos')


@login_required
def home(request):
    logger.debug(f'Usuário {request.user.username} acessou home')
    return render(request, 'objetos/principal/home.html', {})


@login_required
def about(request):
    logger.debug(f'Usuário {request.user.username} acessou about')
    return render(request, 'objetos/principal/about.html', {})


def validar_data(data_str):
    if not data_str or data_str in ('None', ''):
        return None
    
    try:
        return datetime.strptime(data_str, '%Y-%m-%d').date()
    except (ValueError, TypeError) as e:
        logger.warning(f'Data inválida fornecida: {data_str} - {e}')
        return None


@login_required
def listar_objetos(request):
    try:
        # Otimizar query com select_related
        objetos_list = Objeto.objects.select_related('user').all()

        # Filtros de data
        data_inicio_str = request.GET.get('data_inicio')
        data_fim_str = request.GET.get('data_fim')

        data_inicio = validar_data(data_inicio_str)
        data_fim = validar_data(data_fim_str)

        if data_inicio:
            objetos_list = objetos_list.filter(dt_object__gte=data_inicio)
            logger.debug(f'Filtro data_inicio aplicado: {data_inicio}')

        if data_fim:
            objetos_list = objetos_list.filter(dt_object__lte=data_fim)
            logger.debug(f'Filtro data_fim aplicado: {data_fim}')

        objetos_list = objetos_list.order_by('dt_object')

        # Paginação
        paginator = Paginator(objetos_list, 9)
        page_number = request.GET.get('page')
        objetos = paginator.get_page(page_number)

        logger.info(
            f'Listagem de objetos: página {objetos.number}/{paginator.num_pages}, '
            f'total {paginator.count} objetos'
        )

        return render(
            request,
            'objetos/dados/listar_objetos.html',
            {
                'objetos': objetos,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
            }
        )

    except Exception as e:
        logger.error(f'Erro ao listar objetos: {e}', exc_info=True)
        messages.error(request, 'Ocorreu um erro ao filtrar os objetos.')
        return redirect('home')
    

@login_required
def visualizar_objeto(request, pk):
    try:
        objeto = get_object_or_404(Objeto, pk=pk)
        logger.info(f'Usuário {request.user.username} visualizou objeto {pk}')
        return render(request, "objetos/dados/visualizar_objeto.html", {"objeto": objeto})
    except Exception as e:
        logger.error(f'Erro ao visualizar objeto {pk}: {e}', exc_info=True)
        messages.error(request, 'Erro ao visualizar objeto.')
        return redirect('listar_objetos')
    

@login_required
def adicionar_objeto(request):
    try:
        form = ObjetoForm(request.POST or None, request.FILES or None)
        
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            
            logger.info(
                f'Objeto {obj.id} criado por usuário {request.user.username}: {obj.name}'
            )
            messages.success(request, 'Objeto adicionado com sucesso!')
            return redirect("listar_objetos")

        return render(request, "objetos/dados/form_objeto.html", {"form": form})
    
    except (ValidationError, IntegrityError) as e:
        logger.warning(f'Erro de validação ao adicionar objeto: {e}')
        messages.error(request, "Dados inválidos. Verifique e tente novamente.")
        return redirect("listar_objetos")
    
    except Exception as e:
        logger.error(f'Erro inesperado ao adicionar objeto: {e}', exc_info=True)
        messages.error(request, "Erro ao adicionar objeto. Tente novamente mais tarde.")
        return redirect("listar_objetos")


@login_required
def editar_objeto(request, pk):
    try:
        # Verificar permissões
        if is_admin(request.user):
            objeto = get_object_or_404(Objeto, pk=pk)
        else:
            objeto = get_object_or_404(Objeto, pk=pk, user=request.user)

        if request.method == "POST":
            form = ObjetoForm(request.POST, request.FILES, instance=objeto)
            
            if form.is_valid():
                form.save()
                logger.info(
                    f'Objeto {pk} editado por usuário {request.user.username}'
                )
                messages.success(request, 'Informações do objeto editadas com sucesso.')
                return redirect("listar_objetos")
        else:
            form = ObjetoForm(instance=objeto)

        return render(request, "objetos/dados/form_objeto.html", {
            "form": form,
            "objeto": objeto
        })
    
    except (ValidationError, IntegrityError) as e:
        logger.warning(f'Erro de validação ao editar objeto {pk}: {e}')
        messages.error(request, "Dados inválidos. Verifique e tente novamente.")
        return redirect("listar_objetos")
    
    except Exception as e:
        logger.error(f'Erro ao editar objeto {pk}: {e}', exc_info=True)
        messages.error(request, "Erro ao editar objeto. Tente novamente mais tarde.")
        return redirect("listar_objetos")


@login_required
def remover_objeto(request, pk):
    try:
        # Verificar permissões
        if is_admin(request.user):
            objeto = get_object_or_404(Objeto, pk=pk)
        else:
            objeto = get_object_or_404(Objeto, pk=pk, user=request.user)

        if request.method == "POST":
            nome_objeto = str(objeto)
            objeto.delete()
            
            logger.info(
                f'Objeto {pk} ({nome_objeto}) removido por usuário {request.user.username}'
            )
            messages.success(request, "Objeto removido com sucesso!")
            return redirect("listar_objetos")

        # GET - mostrar confirmação
        return render(request, "objetos/dados/confirmar_remocao.html", {"objeto": objeto})
    
    except Exception as e:
        logger.error(f'Erro ao remover objeto {pk}: {e}', exc_info=True)
        messages.error(request, "Erro ao tentar remover objeto. Tente novamente mais tarde.")
        return redirect("listar_objetos")
    

@login_required
def relatorio_registros(request):
    try:
        total = RegistroAcao.objects.count()

        if total > 100:
            registros_antigos = (
                RegistroAcao.objects
                .order_by("dt_create")[:20]
            )
            registros_antigos.delete()

        registros = RegistroAcao.objects.order_by("-dt_create")

        logger.info(
            f'Relatório de registros acessado por {request.user.username}: '
        )

        return render(request, "objetos/relatorio/registroacao_list.html", {
            "registros": registros
        })
    except Exception as e:
        logger.error(f'Erro ao visualizar relatório: {e}', exc_info=True)
        messages.error(request, "Erro ao tentar visualizar relatório. Tente novamente mais tarde.")
        return redirect("home")