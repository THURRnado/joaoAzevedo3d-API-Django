from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Objeto, RegistroAcao
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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


def is_admin(user):
    return user.is_staff or user.is_superuser


# Create your views here.
def dados_json_objeto(request, pk):

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

    return JsonResponse(data, json_dumps_params={"ensure_ascii": False})


@login_required
def gerar_pdf_objetos(request):
    try:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="objetos.pdf"'

        doc = SimpleDocTemplate(response, pagesize=A4)
        story = []

        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        text_style = styles["Normal"]
        bold_style = styles["Heading4"]

        # Título
        story.append(Paragraph("Objetos João Azevedo", title_style))
        story.append(Spacer(1, 20))

        # Loop dos objetos
        for index, obj in enumerate(Objeto.objects.all()):
            
            # Alternância de cor (cinza leve e azul claro)
            bg_color = colors.whitesmoke if index % 2 == 0 else colors.Color(0.85, 0.92, 1)

            # Imagem
            if obj.img_object:
                img = Image(obj.img_object.path, width=1.5*inch, height=1.5*inch)
            else:
                img = Paragraph("<i>Sem imagem</i>", text_style)

            # Dados do objeto (agora num único Paragraph para centralizar)
            info = Paragraph(
                f"""
                <b>Nome:</b> {obj.name}<br/>
                <b>Descrição:</b> {obj.description or '---'}<br/>
                <b>Data do objeto:</b> {obj.dt_object.strftime('%d/%m/%Y') if obj.dt_object else '---'}
                """,
                text_style
            )

            # Tabela centralizada verticalmente
            bloco = Table(
                [[img, info]],
                colWidths=[120, 400],
                rowHeights=[120]  # ajuda a manter centro vertical
            )

            bloco.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), bg_color),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # <--- centralização vertical
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))

            story.append(bloco)
            story.append(Spacer(1, 15))

        doc.build(story)
        return response

    except Exception as e:
        print(str(e))
        messages.error(request, 'Ocorreu um erro ao gerar o PDF.')
        return redirect('listar_objetos')


@login_required
def home(request):
    return render(request, 'objetos/principal/home.html', {})


@login_required
def about(request):
    return render(request, 'objetos/principal/about.html', {})


@login_required
def listar_objetos(request):
    try:
        objetos_list = Objeto.objects.all()

        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        if data_inicio in (None, '', 'None'):
            data_inicio = None

        if data_fim in (None, '', 'None'):
            data_fim = None

        if data_inicio:
            objetos_list = objetos_list.filter(dt_object__gte=data_inicio)

        if data_fim:
            objetos_list = objetos_list.filter(dt_object__lte=data_fim)

        objetos_list = objetos_list.order_by('dt_object')

        paginator = Paginator(objetos_list, 9)
        page_number = request.GET.get('page')
        objetos = paginator.get_page(page_number)

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
        print(e)
        messages.error(
            request,
            'Ocorreu um erro ao filtrar os objetos.'
        )
        return redirect('home')
    

@login_required
def visualizar_objeto(request, pk):
    objeto = get_object_or_404(Objeto, pk=pk)
    return render(request, "objetos/dados/visualizar_objeto.html", {"objeto": objeto})
    

@login_required
def adicionar_objeto(request):
    try:
        form = ObjetoForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect("listar_objetos")

        return render(request, "objetos/dados/form_objeto.html", {"form": form})
    except Exception as e:
        print(str(e))
        messages.error(request, "Erro ao adicionar objeto. Tente novamente mais tarde.")
        return redirect("listar_objetos")


@login_required
def editar_objeto(request, pk):
    try:
        if is_admin(request.user):
            objeto = get_object_or_404(Objeto, pk=pk)
        else:
            objeto = get_object_or_404(
                Objeto,
                pk=pk,
                user=request.user
            )

        if request.method == "POST":
            form = ObjetoForm(request.POST, request.FILES, instance=objeto)
            if form.is_valid():
                form.save()
                messages.success(request, 'Informações do objeto editadas com sucesso.')
                return redirect("listar_objetos")
        else:
            form = ObjetoForm(instance=objeto)

        return render(request, "objetos/dados/form_objeto.html", {
            "form": form,
            "objeto": objeto
        })
    except Exception as e:
        print(str(e))
        messages.error(request, "Erro ao editar objeto. Tente novamente mais tarde.")
        return redirect("listar_objetos")


@login_required
def remover_objeto(request, pk):

    try:
        if is_admin(request.user):
            objeto = get_object_or_404(Objeto, pk=pk)
        else:
            objeto = get_object_or_404(
                    Objeto,
                    pk=pk,
                    user=request.user
                )

        if request.method == "POST":
            try:
                objeto.delete()
                messages.success(request, "Objeto removido com sucesso!")
                return redirect("listar_objetos")
            except Exception as e:
                print(str(e))
                messages.error(request, "Erro ao remover o objeto. Tente novamente.")
                return redirect("listar_objetos")

        # Caso o usuário tente acessar via GET, enviamos uma confirmação
        return render(request, "objetos/dados/confirmar_remocao.html", {"objeto": objeto})
    except Exception as e:
        print(str(e))
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

        return render(request, "objetos/relatorio/registroacao_list.html", {
            "registros": registros
        })
    except Exception as e:
        print(str(e))
        messages.error(request, "Erro ao tentar visualizar relatório. Tente novamente mais tarde.")
        return redirect("home")