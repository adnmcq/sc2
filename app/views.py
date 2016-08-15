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
        #recipe = Recipe.objects.get(id=id)

        #recipe_id - if a recipe is already populated, set initial data for formset
        #a model method on the recipe to get recipe.nuts['ingredients']

        #before giving the value here for 'units', you need to pass in a choices tuple [(:),(:),(:)] that unit is a part of
        init_ingredients = [{'food':'Candy','amt':12,'units':'cup'},{'food':'Bacon','amt':9,'units':'cup'}]
    else:
        init_ingredients = None
    IngredientsFormSet = formset_factory(IngredientLineForm, can_delete=True, can_order=True)
    if request.method == 'POST':
        formset = IngredientsFormSet(request.POST, request.FILES)
        if formset.is_valid():#maybe make a custom clean
            #get food_item, food.nuts, amt, number and use it to build nuts (for recipe)
            for form in formset.ordered_forms:
                print(form.cleaned_data)
                #after getting all the stuff
                #recipe = Recipe.objects.create(nuts=nuts, name=name)
        else:
            print formset.errors
    else:
        formset = IngredientsFormSet(initial=init_ingredients) #{'units': [u'Select a valid choice. serving is not one of the available choices.']}]
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

