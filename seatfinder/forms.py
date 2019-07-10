from django import forms

class NameForm(forms.Form):
    name = forms.CharField(label='Who/what room are you looking for?', max_length=100)