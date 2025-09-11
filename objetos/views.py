from django.shortcuts import render
from django.http import JsonResponse, Http404
from .models import Objeto

# Create your views here.
def dados_json_objeto(request, pk):

    try:
        objeto = Objeto.objects.get(pk=pk)
    except Objeto.DoesNotExist:
        raise Http404("Objeto não encontrado")
    
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