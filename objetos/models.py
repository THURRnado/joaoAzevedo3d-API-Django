from django.db import models
from django.urls import reverse
from django.conf import settings


class Objeto(models.Model):

    name = models.CharField(max_length=255, null=False, unique=True, verbose_name="Nome do objeto")
    id_objeto = models.CharField(max_length=50, null=True, blank=True, unique=True, verbose_name="ID do objeto")
    description = models.TextField(null=True, blank=True, verbose_name="Descrição")
    img_object = models.ImageField(upload_to='objetos/', null=True, blank=True, verbose_name="Descrição")
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Usuário")
    dt_create = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    dt_modified = models.DateTimeField(auto_now=True, verbose_name="Data de modificação")
    dt_object = models.DateField(verbose_name="Data do objeto", null=True, blank=True)

    class Meta:
        verbose_name = "Objeto"
        verbose_name_plural = "Objetos"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})
    

class RegistroAcao(models.Model):
    ACOES = (
        ('CREATE', 'Criação'),
        ('UPDATE', 'Edição'),
        ('DELETE', 'Remoção'),
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    acao = models.CharField(max_length=10, choices=ACOES)
    modelo = models.CharField(max_length=100)
    id_objeto = models.PositiveIntegerField(null=True, blank=True)
    descricao = models.TextField()
    dt_create = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de ação"
        verbose_name_plural = "Registro de ações"

    def __str__(self):
        return f'{self.usuario} - {self.acao} - {self.modelo}'