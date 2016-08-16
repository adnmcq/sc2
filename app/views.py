from django.shortcuts import render,HttpResponseRedirect
from django.core.urlresolvers import reverse

from models import *
from django.db.models import Count
import json
#from django.template import Context, Template

from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt


from django.forms.models import modelformset_factory, formset_factory,inlineformset_factory
from forms import *


from forms import IngredientLineForm

#cn=hange name of index --> recipe
#optional parameter to recipe - recipe id
#make recipe model - name, nuts
#but nuts also has ingredients[{'food':food.id,'amt':amt,'serving':serving},{..},{..}]
#this ingredients is set on post
#also nutriional facts for recipe calculated on post

#if recipe id is passed into the index, first look up ingredients from recipe.nuts['ingredients']
#use that to populate the formset (might have to make it a modelformset


def index(request):
    return render(request, 'app/index.html', {})



def recipe(request, id=None):
    if id:
        recipe = Recipe.objects.get(id=id)
        init_ingredients_info = recipe.nuts['ingredients']
    else:
        init_ingredients_info = []
    IngredientsFormSet = formset_factory(IngredientLineForm, can_delete=True, can_order=True)
    if request.method == 'POST':
        formset = IngredientsFormSet(request.POST, request.FILES)
        if formset.is_valid():#maybe make a custom clean
            ingredients_list = []
            for form in formset.ordered_forms:
                cd = form.cleaned_data
                choices = Food.objects.get(name=cd['food']).get_units()
                ingredients_list.append({'food':cd['food'],'units':cd['units'],'amt':cd['amt'],'choices':choices})
                #after getting all the stuff
                #recipe = Recipe.objects.create(nuts=nuts, name=name)
            nuts = {'ingredients':ingredients_list}
            if id:
                recipe.nuts=nuts
                recipe.save()
            else:
                recipe = Recipe.objects.create(nuts=nuts)
            print recipe.nuts
        else:
            print formset.errors
    else:
        formset = IngredientsFormSet() #{'units': [u'Select a valid choice. serving is not one of the available choices.']}]
        for i,ingredient_info in enumerate(init_ingredients_info):
            #get recipe nuts['ingredients']
            #this ok - recipe only called if forloop hits
            formset[i].fields['units'].choices = init_ingredients_info[i]['choices']
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

