from django import forms


class IngredientLineForm(forms.Form):
    food = forms.CharField(widget=forms.TextInput(attrs={'class':'foods form-control'})) #class = food
    units = forms.ChoiceField(widget=forms.Select(attrs={'class':'units form-control'}))
    amt = forms.CharField(widget=forms.NumberInput(attrs={'class':'amt form-control'}))
