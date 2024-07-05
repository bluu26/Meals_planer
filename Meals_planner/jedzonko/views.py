from datetime import datetime
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.views import View
from random import shuffle
from jedzonko.models import Recipe, Plan, RecipePlan, DayName
import random
from jedzonko.models import Recipe, Plan
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse


def get_random_recipes():
    recipes = list(Recipe.objects.all())
    random.shuffle(recipes)
    return recipes[:3]


class IndexView(View):
    def get(self, request):
        carousel_recipes = get_random_recipes()
        return render(request, 'index.html', {'carousel_recipes': carousel_recipes})


def index(request):
    carousel_recipes = get_random_recipes()
    return render(request, 'index.html', {'carousel_recipes': carousel_recipes})


class DashboardView(View):
    def get(self, request):
        recipe_number = Recipe.objects.count()
        plans_number = Plan.objects.count()

        last_plan = Plan.objects.last()
        last_plan_name = last_plan.name if last_plan else None

        days = DayName.objects.filter(id__in=RecipePlan.objects.filter(plan=last_plan).values('day_name')).distinct()

        # Tworzenie słownika dni i posiłków przypisanych do nich
        recipe_plans_by_day = {}
        if last_plan:
            for day in days:
                recipe_plans_by_day[day] = RecipePlan.objects.filter(plan=last_plan, day_name=day)

        return render(request, "dashboard.html", {
            'recipe_number': recipe_number,
            'plans_number': plans_number,
            'last_plan_name': last_plan_name,
            'recipe_plans_by_day': recipe_plans_by_day,
        })


class RecipeListView(View):
    def get(self, request):
        all_recipes = Recipe.objects.all()
        sorted_recipes = all_recipes.order_by('-votes', '-created')

        paginator = Paginator(sorted_recipes, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, "app-recipes.html", {'page_obj': page_obj})


class AddRecipeView(View):
    def get(self, request):
        return render(request, 'app-add-recipe.html')

    def post(self, request):
        name = request.POST.get('name')
        description = request.POST.get('description')
        preparation_time = request.POST.get('preparation_time')
        preparation_details = request.POST.get('preparation_details')
        preparation_method = request.POST.get('preparation_method')

        if not (name and description and preparation_time and preparation_details and preparation_method):
            messages.error(request, 'Wszystkie pola są wymagane.')
            return render(request, 'app-add-recipe.html')

        try:
            preparation_time = int(preparation_time)
        except ValueError:
            messages.error(request, 'Czas przygotowania musi być liczbą całkowitą.')
            return render(request, 'app-add-recipe.html')



        recipe = Recipe.objects.create(
            name=name,
            description=description,
            preparation_time=preparation_time,
            ingredients=preparation_details,
            preparation_method=preparation_method
        )

        print(f"Saved recipe ID: {recipe.id}")

        messages.success(request, 'Przepis został pomyślnie dodany.')

        # Przekieruj użytkownika do widoku listy przepisów po dodaniu przepisu
        return redirect('recipe_list')


class PlanAddView(View):
    def get(self, request):
        return render(request, 'app-add-schedules.html')

    def post(self, request):
        name = request.POST.get('name')
        description = request.POST.get('description')

        if not name or not description:
            error_message = "UZUPEŁNIJ POLA!."
            return render(request, 'app-add-schedules.html', {'error_message': error_message})

        Plan.objects.create(
            name=name,
            description=description
        )

        return redirect('plan_list')


def plan_list(request):
    plans = Plan.objects.all()
    num_pages = 3
    page = 1
    page_numbers = [1]

    context = {
        'plans': plans,
        'num_pages': num_pages,
        'page': page,
        'page_numbers': page_numbers,
    }
    return render(request, 'app-schedules.html', context)


class DetailsPlanView(View):
    def get(self, request):
        plans = Plan.objects.all()
        recipes = Recipe.objects.all()
        day_name = DayName.objects.all()
        return render(request, 'app-schedules-meal-recipe.html', {
            'plans': plans,
            'recipes': recipes,
            'day_names': day_name
        })

    def post(self, request):
        meal_name = request.POST.get('meal_name')
        recipe_id = request.POST.get('recipe_id')
        plan_id = request.POST.get('plan_id')
        order = request.POST.get('order')
        day_name_id = request.POST.get('day_name_id')

        recipe = Recipe.objects.get(id=recipe_id)
        plan = Plan.objects.get(id=plan_id)
        day_name = DayName.objects.get(id=day_name_id)

        RecipePlan.objects.create(
            meal_name=meal_name,
            recipe=recipe,
            plan=plan,
            order=order,
            day_name=day_name
        )

        return redirect('plan_list')


class PlanIdView(View):
    def get(self, request, id):
        plan = get_object_or_404(Plan, id=id)
        recipe_plans = RecipePlan.objects.filter(plan_id=plan.id).order_by("order")

        days_with_recipes = {}
        for recipe_plan in recipe_plans:
            day_name = recipe_plan.day_name.name
            if day_name not in days_with_recipes:
                days_with_recipes[day_name] = []
            days_with_recipes[day_name].append(recipe_plan)

        ctx = {
            "plan": plan,
            "days_with_recipes": days_with_recipes,
        }
        return render(request, "app-details-schedules.html", ctx)


class RecipeDeleteFromPlan(View):
    def get(self, request, pk):
        plan_id = RecipePlan.objects.get(id=pk).plan_id
        RecipePlan.objects.get(id=pk).delete()
        return redirect(f'/plan/{plan_id}')

class RecipeDetailsView(View):
    def get(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        return render(request, 'app-recipe-details.html', {'recipe': recipe})

    def post(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)

        if 'vote' in request.POST:
            if request.POST['vote'] == 'up':
                recipe.votes += 1
            elif request.POST['vote'] == 'down':
                recipe.votes -= 1
            recipe.save()
            return HttpResponseRedirect(
                reverse('app-recipe-details', args=(id,)))
        else:
            return HttpResponseBadRequest("Invalid request")


class RecipeModifyView(View):

    def get(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return render(request, 'app-edit-recipe.html', {'recipe': recipe})

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        name = request.POST.get('name')
        description = request.POST.get('description')
        preparation_time = request.POST.get('preparation_time')
        preparation_method = request.POST.get('preparation_method')
        ingredients = request.POST.get('ingredients')
        recipe.name = name
        recipe.description = description
        recipe.preparation_time = preparation_time
        recipe.preparation_method = preparation_method
        recipe.ingredients = ingredients

        if not (name or description or preparation_time or preparation_method or ingredients):
            messages.error(request, 'Wypełnij poprawnie wszystkie pola.')
            return render(request, 'app-edit-recipe.html')
        try:
            preparation_time = int(preparation_time)
        except ValueError:
            messages.error(request, 'Czas przygotowania musi być liczbą całkowitą.')
            return render(request, 'app-edit-recipe.html')

        recipe.save()
        return redirect('recipe_list')


class PlanModifyView(View):

    def get(self, request, pk):
        plan = get_object_or_404(Plan, id=pk)
        return render(request, 'edit-plan.html', {'plan':plan})
    def post(self, request, pk):
        plan = get_object_or_404(Plan, id=pk)
        name = request.POST.get('name')
        description = request.POST.get('description')
        plan.name = name
        plan.description = description

        if not (name or description):
            messages.error(request, 'Wypełnij poprawnie wszystkie pola.')
            return render(request, 'edit-plan.html')

        plan.save()
        return redirect('plan_list')
