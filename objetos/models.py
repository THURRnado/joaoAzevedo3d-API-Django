from django.db import models
from django.urls import reverse

# Create your models here.
class Objeto(models.Model):

    name = models.CharField(max_length=255, null=False, verbose_name="Nome do objeto")
    description = models.TextField(null="True", blank=True, verbose_name="Descrição")
    img_object = models.ImageField(upload_to='objetos/', null=True, blank=True, verbose_name="Descrição")
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="Usuário")
    dt_create = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    dt_modified = models.DateTimeField(auto_now=True, verbose_name="Data de modificação")
    dt_object = models.DateField(verbose_name="Data do objeto")

    class Meta:
        verbose_name = "Objeto"
        verbose_name_plural = "Objetos"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})