from re import VERBOSE
from django import forms
from .models import Dosyalar


class DokumanForm(forms.ModelForm):

    class Meta:
        model = Dosyalar
        fields =[ 'aciklama','file']
