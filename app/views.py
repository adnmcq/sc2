from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse

from models import *
from django.db.models import Count
import json


from django.http import JsonResponse
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
        init_nutrients_info = recipe.nuts
        #whole chart
        #chart_labels = [n.get('name') for n in init_nutrients_info if n.get('val') >= 0.001]
        #chart_data = [n.get('val') for n in init_nutrients_info if n.get('val') >= 0.001]
        #Proximates, Lipids, Vitamins, Minerals, Other
        prox_labels = [n.get('name') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Proximates')]
        prox_data = [n.get('val') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Proximates')]
        lip_labels = [n.get('name') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Lipids')]
        lip_data = [n.get('val') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Lipids')]
        vit_labels = [n.get('name') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Vitamins')]
        vit_data = [n.get('val') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Vitamins')]
        min_labels = [n.get('name') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Minerals')]
        min_data = [n.get('val') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Minerals')]
        oth_labels = [n.get('name') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Other')]
        oth_data = [n.get('val') for n in init_nutrients_info if (n.get('val') >= 0.001 and n.get('group')=='Other')]
        extra = len(init_ingredients_info)+1
    else:
        recipe = None
        init_ingredients_info, init_nutrients_info = [],[]
        prox_labels, prox_data, lip_data, lip_labels, vit_labels, vit_data, min_labels, min_data, oth_labels, oth_data= \
        [],[],[],[],[],[],[],[],[],[]
        extra = 1
    IngredientsFormSet = formset_factory(IngredientLineForm, can_delete=True, can_order=True, extra = extra)
    if request.method == 'POST':
        formset = IngredientsFormSet(request.POST, request.FILES)
        rform = RecipeForm(request.POST)
        if formset.is_valid() and rform.is_valid():
            #EACH FORM = RECIPE ITEM
            for form in formset.ordered_forms:
                recipe = rform.save(commit=False) #do not commit twice
                cd = form.cleaned_data
                food, units, amt = cd['food'], cd['units'], cd['amt']
                choices = Food.objects.get(name=cd['food']).get_units_choices()
                ingredients_list.append({'food':food, 'units':units, 'amt':amt, 'choices':choices})
                single_food_nutrients = Food.objects.get(name = food).nuts
                #first iteration hits Water
                for nut_dict in single_food_nutrients:
                    nut_name = nut_dict['name'] if nut_dict['name'] != 'Energy' else '%s (%s)'%(nut_dict['name'],nut_dict['unit'])#Water, Fat, etc.
                    nut_unit = nut_dict['unit']#gram or microgram - make sure these are consistent between DIFFERENT FOODS
                    nut_group = nut_dict['group'] #Proximates, Lipids, Vitamins, Minerals, Other
                    #EQUIVALENT output - which is faster?
                    #see speed_test.txt
                    matching_measure = [n for n in nut_dict['measures'] if n.get('label') == units]
                    #matching_measure = filter(lambda n: n.get('label') == units, nut_dict['measures'])
                    if matching_measure:
                        nut_serving_val = matching_measure[0]['value']
                    else:
                        nut_serving_val = nut_dict['value']
                    nut_val = nut_serving_val * amt #total - measures * amt
                    #EQUIVALENT
                    recipe_nutrient = [n for n in recipe_nutrients if (n.get('name') == nut_name and n.get('unit') == nut_unit)]
                    #recipe_nutrient = filter(lambda n: (n.get('name') == nut_name and n.get('unit') == nut_unit), recipe_nutrients)
                    if not recipe_nutrient: #update list with new nutrient
                        recipe_nutrients.append({'name':nut_name, 'unit':nut_unit, 'val':nut_val, 'group':nut_group})
                    else:
                        #weirdly enough this works, updating 'a' in a dictionary
                        #in a filtered_list = [{'a':x}] updates 'a' in original list [{'a':x}, {'b':y}]
                        recipe_nutrient[0]['val'] = recipe_nutrient[0]['val'] + nut_val
            recipe.ingredients = ingredients_list
            recipe.nuts = recipe_nutrients
            recipe.save()
            return HttpResponseRedirect(reverse('recipe', args=(recipe.id,)))#HttpResponse([recipe.nuts, recipe.ingredients])
        else:
            return HttpResponse(formset.errors)
    else:
        rform = RecipeForm(instance = recipe)
        formset = IngredientsFormSet() #{'units': [u'Select a valid choice. serving is not one of the available choices.']}]
        for i,ingredient_info in enumerate(init_ingredients_info):
            #get recipe nuts['ingredients']
            #this ok - recipe only called if forloop hits
            units_choices = init_ingredients_info[i]['choices']
            #choices_tuple = ((k, k) for k in choices_list)
            formset[i].fields['units'].choices = units_choices#(('cup', 'cup'),('serving', 'serving'))#init_ingredients_info[i]['choices']
            formset[i].fields['units'].initial = init_ingredients_info[i]['units']
            formset[i].fields['amt'].initial = init_ingredients_info[i]['amt']#this actually needs to be set from recipe.nuts
            formset[i].fields['food'].initial = init_ingredients_info[i]['food']#
    return render(request, 'app/recipe.html', {'rform':rform,'formset': formset,
                                               'nutrients':init_nutrients_info,
                                               'prox_labels':json.dumps(prox_labels),
                                               'prox_data':json.dumps(prox_data),
                                               'lip_labels':json.dumps(lip_labels),
                                               'lip_data':json.dumps(lip_data),
                                               'vit_data':json.dumps(vit_data),
                                               'vit_labels':json.dumps(vit_labels),
                                               'min_data':json.dumps(min_data),
                                               'min_labels':json.dumps(min_labels),
                                               'oth_labels':json.dumps(oth_labels),
                                               'oth_data':json.dumps(oth_data),
                                                                       }) #use this to get the nutritional facts and data for charts


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
    units_choices = food.get_units_choices()
    return JsonResponse(units_choices,safe=False)

