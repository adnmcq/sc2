from django.shortcuts import render,HttpResponseRedirect,HttpResponse
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
    recipe_nutrients = []
    ingredients_list = []
    if id:
        recipe = Recipe.objects.get(id=id)
        init_ingredients_info = recipe.ingredients
        extra = len(init_ingredients_info)+1
    else:
        recipe = None
        extra = 1
        init_ingredients_info = []
    IngredientsFormSet = formset_factory(IngredientLineForm, can_delete=True, can_order=True, extra = extra)
    if request.method == 'POST':
        formset = IngredientsFormSet(request.POST, request.FILES)
        rform = RecipeForm(request.POST)
        if formset.is_valid() and rform.is_valid():
            for form in formset.ordered_forms:
                recipe = rform.save(commit=False) #do not commit twice
                cd = form.cleaned_data
                food, units, amt = cd['food'], cd['units'], cd['amt']
                choices = Food.objects.get(name=cd['food']).get_units()
                ingredients_list.append({'food':food, 'units':units, 'amt':amt, 'choices':choices})
                single_food_nutrients = Food.objects.get(name = food).nuts
                '''
                single_food_nutrients
                ----------------
                see single_food_nutrients.txt
                '''
                for nut_dict in single_food_nutrients: #loop through nutrients for a food
                    nut_name = nut_dict['name']
                    try:
                        nut_val = filter(lambda n: n.get('label') == units, nut_dict['measures'])[0]['value']
                    except IndexError:
                        nut_val = nut_dict['value']
                    nut_unit = nut_dict['unit']
                    #if this nutrient is not already present in the recipe nutrient dict, create it
                    #make sure to match name AND units - handle if units don't match
                    recipe_nutrient = filter(lambda n: (n.get('name') == nut_name and n.get('unit') == nut_unit), recipe_nutrients)
                    if not recipe_nutrient:
                        #equivalent already handled with val
                        recipe_nutrients.append({'name':nut_name, 'unit':nut_unit, 'val':nut_val})
                    else:#if is found, add new nutrientvalue
                        recipe_nutrient[0]['val'] = recipe_nutrient[0]['val'] + nut_val
            recipe.ingredients = ingredients_list
            recipe.nuts = recipe_nutrients
            recipe.save()
            return HttpResponse([recipe.nuts, recipe.ingredients])
            #{'ingredients': [{'food': u"AMY'S, CHEWY CANDY BARS, CARAMEL, PECANS & CHOCOLATE, UPC: 042272003891", 'units': u'serving', 'val': u'2', 'choices': [u'serving']},
            # {'food': u'Babyfood, banana apple dessert, strained', 'units': u'jar NFS', 'val': u'1', 'choices': [u'tbsp', u'jar NFS', u'jar Gerber Second Food (4 oz)']}]}

        else:
            print formset.errors
    else:
        rform = RecipeForm(instance = recipe)
        formset = IngredientsFormSet() #{'units': [u'Select a valid choice. serving is not one of the available choices.']}]
        for i,ingredient_info in enumerate(init_ingredients_info):
            #get recipe nuts['ingredients']
            #this ok - recipe only called if forloop hits
            print init_ingredients_info[i]['choices']
            formset[i].fields['units'].choices = (('cup', 'cup'),('serving', 'serving'))#init_ingredients_info[i]['choices']
            formset[i].fields['units'].initial = init_ingredients_info[i]['units']
            formset[i].fields['val'].initial = init_ingredients_info[i]['val']#this actually needs to be set from recipe.nuts
            formset[i].fields['food'].initial = init_ingredients_info[i]['food']#
    return render(request, 'app/recipe.html', {'rform':rform,'formset': formset})



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

