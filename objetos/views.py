from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Objeto
from utils.exceptions import ServiceError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ObjetoForm
from django.core.paginator import Paginator


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
def home(request):
    return render(request, 'objetos/home.html', {})


@login_required
def about(request):
    return render(request, 'objetos/about.html', {})


@login_required
def listar_objetos(request):
    try:
        objetos_list = Objeto.objects.all().order_by('-dt_create')
        paginator = Paginator(objetos_list, 9) 
        page_number = request.GET.get('page')
        objetos = paginator.get_page(page_number)

        return render(request, 'objetos/listar_objetos.html', {'objetos': objetos})

    except Exception as e:
        print(str(e))
        messages.error(request, 'Ocorreu um erro. Não foi possível concluir essa operação, tente novamente mais tarde.')
        return redirect("home")
    

@login_required
def visualizar_objeto(request, pk):
    objeto = get_object_or_404(Objeto, pk=pk)
    return render(request, "objetos/visualizar_objeto.html", {"objeto": objeto})
    

@login_required
def adicionar_objeto(request):
    try:
        form = ObjetoForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect("listar_objetos")

        return render(request, "objetos/form_objeto.html", {"form": form})
    except Exception as e:
        print(str(e))
        messages.error(request, "Erro ao adicionar objeto. Tente novamente.")
        return redirect("listar_objetos")


@login_required
def editar_objeto(request, pk):
    objeto = get_object_or_404(Objeto, pk=pk)
    form = ObjetoForm(request.POST or None, request.FILES or None, instance=objeto)

    return render(request, "objetos/form_objeto.html", {"form": form, "objeto": objeto})


@login_required
def remover_objeto(request, pk):
    objeto = get_object_or_404(Objeto, pk=pk)

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
    return render(request, "objetos/confirmar_remocao.html", {"objeto": objeto})