from django import forms
from .models import Objeto

class ObjetoForm(forms.ModelForm):
    class Meta:
        model = Objeto
        fields = [
            "id_objeto",
            "name",
            "description",
            "img_object",
            "dt_object",
        ]

        widgets = {
            "id_objeto": forms.TextInput(attrs={
                "class": "w-full p-2 border rounded-lg focus:ring focus:ring-blue-300",
                "placeholder": "ID do objeto"
            }),
            "name": forms.TextInput(attrs={
                "class": "w-full p-2 border rounded-lg focus:ring focus:ring-blue-300",
                "placeholder": "Nome do objeto..."
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full p-2 border rounded-lg h-28 focus:ring focus:ring-blue-300",
                "placeholder": "Descrição..."
            }),
            "img_object": forms.ClearableFileInput(attrs={
                "class": "w-full p-2 border rounded-lg bg-white"
            }),
            "dt_object": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full p-2 border rounded-lg"
            }),
        }

    def clean_id_objeto(self):
        id = self.cleaned_data.get("id_objeto")
        return id or None

    def clean_name(self):
        name = self.cleaned_data.get("name")

        qs = Objeto.objects.filter(name__iexact=name)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "Já existe um objeto cadastrado com esse nome."
            )

        return name