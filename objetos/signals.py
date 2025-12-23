from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Objeto, RegistroAcao

@receiver(post_save, sender=Objeto)
def registrar_create_update(sender, instance, created, **kwargs):
    if created:
        acao = 'CREATE'
        descricao = f'Criou o objeto "{instance}"'
    else:
        acao = 'UPDATE'
        descricao = f'Editou o objeto "{instance}"'

    RegistroAcao.objects.create(
        usuario=instance.user,
        acao=acao,
        modelo=sender.__name__,
        id_objeto=instance.id_objeto,
        descricao=descricao
    )


@receiver(post_delete, sender=Objeto)
def registrar_delete(sender, instance, **kwargs):
    RegistroAcao.objects.create(
        usuario=instance.user,
        acao='DELETE',
        modelo=sender.__name__,
        id_objeto=instance.id_objeto,
        descricao=f'Removeu o objeto "{instance}"'
    )