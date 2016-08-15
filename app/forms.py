from django import forms


class IngredientLineForm(forms.Form):
    food = forms.CharField(widget=forms.TextInput(attrs={'class':'foods form-control'})) #class = food
    units = forms.ChoiceField(choices = [('cup','cup'),('bucket','bucket'),('serving','serving')],widget=forms.Select(attrs={'class':'units form-control'}))
    amt = forms.CharField(widget=forms.NumberInput(attrs={'class':'amt form-control'}))
    #instead of passing initial to formset, I have to go one by one in form and pass as kwargs to forms in formset
    '''
    def __init__(self, *args, **kwargs):
        units_choices = kwargs.pop('units_choices', None)
        super(IngredientLineForm, self).__init__(*args, **kwargs)
        if units_choices:
            self.fields['units'].choices = units_choices
        if unit_initial:
            1
    '''
