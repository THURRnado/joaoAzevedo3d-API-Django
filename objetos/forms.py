from django import forms
from .models import Objeto

class ObjetoForm(forms.ModelForm):
    class Meta:
        model = Objeto
        fields = ["name", "description", "img_object", "dt_object"]

        widgets = {
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
