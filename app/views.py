from django.shortcuts import render,HttpResponseRedirect
from django.core.urlresolvers import reverse

from models import *
from django.db.models import Count
import json


from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt


from django.forms.models import modelformset_factory, formset_factory,inlineformset_factory
from forms import *


from forms import IngredientLineForm

def index(request):
    return render(request, 'app/index.html', {})



def recipe(request, id=None):
    if id:
        recipe = Recipe.objects.get(id=id)
        init_ingredients_info = recipe.nuts['ingredients']
        extra = len(init_ingredients_info)+1
    else:
        extra = 1
        init_ingredients_info = []
    IngredientsFormSet = formset_factory(IngredientLineForm, can_delete=True, can_order=True, extra = extra)
    if request.method == 'POST':
        formset = IngredientsFormSet(request.POST, request.FILES)
        if formset.is_valid():
            ingredients_list = []
            for form in formset.ordered_forms:
                cd = form.cleaned_data
                choices = Food.objects.get(name=cd['food']).get_units()
                ingredients_list.append({'food':cd['food'],'units':cd['units'],'amt':cd['amt'],'choices':choices})
            nuts = {'ingredients':ingredients_list}
            if id:
                recipe.nuts=nuts
                recipe.save()
            else:
                recipe = Recipe.objects.create(nuts=nuts)
            print recipe.nuts
            #{'ingredients': [{'food': u"AMY'S, CHEWY CANDY BARS, CARAMEL, PECANS & CHOCOLATE, UPC: 042272003891", 'units': u'serving', 'amt': u'2', 'choices': [u'serving']},
            # {'food': u'Babyfood, banana apple dessert, strained', 'units': u'jar NFS', 'amt': u'1', 'choices': [u'tbsp', u'jar NFS', u'jar Gerber Second Food (4 oz)']}]}

        else:
            print formset.errors
    else:
        formset = IngredientsFormSet() #{'units': [u'Select a valid choice. serving is not one of the available choices.']}]
        for i,ingredient_info in enumerate(init_ingredients_info):
            #get recipe nuts['ingredients']
            #this ok - recipe only called if forloop hits
            print init_ingredients_info[i]['choices']
            formset[i].fields['units'].choices = (('cup', 'cup'),('serving', 'serving'))#init_ingredients_info[i]['choices']
            formset[i].fields['units'].initial = init_ingredients_info[i]['units']
            formset[i].fields['amt'].initial = init_ingredients_info[i]['amt']#this actually needs to be set from recipe.nuts
            formset[i].fields['food'].initial = init_ingredients_info[i]['food']#

    return render(request, 'app/recipe.html', {'formset': formset})



def food_select_options(request):
    json_resp_data = []
    if request.is_ajax():
        foods = Food.objects.all()#maybe ignore some
        q = request.GET.get('term', '')
        foods = foods.filter(name__icontains = q )#[:20]#(dispname__icontains = q )[:20]
        for f in foods:
            json_resp_data.append({'id':f.id,'label':f.name,'value':f.name})
    return JsonResponse(json_resp_data, safe=False)

@csrf_exempt
def unit_select_options(request):
    food=Food.objects.get(pk=request.POST['item_id'])
    unit_choices = food.get_units()
    return JsonResponse(unit_choices,safe=False)

