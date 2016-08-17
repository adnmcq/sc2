from django import forms


'''
I need a CustomChoiceField that accepts .choices (CharField won't take .choices)
But I don't need the Choices validated method, which checks to see if the value selected
is in choices. When I set the units Select input in javascript, it doesn't update the
django choices, and the POST will fail validation.

Override validate https://github.com/django/django/blob/master/django/forms/fields.py
'''
class CustomChoiceField(forms.ChoiceField):
    def validate(self, value):
        pass


class IngredientLineForm(forms.Form):
    food = forms.CharField(widget=forms.TextInput(attrs={'class':'foods form-control'})) #class = food
    units = CustomChoiceField(widget=forms.Select(attrs={'class':'units form-control'}))
    val = forms.CharField(widget=forms.NumberInput(attrs={'class':'val form-control'}))
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
