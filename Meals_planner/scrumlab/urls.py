"""scrumlab URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from jedzonko import views

from jedzonko.views import IndexView, DashboardView, RecipeListView, PlanAddView, AddRecipeView, DetailsPlanView, \

    PlanIdView, RecipeDetailsView, RecipeModifyView, PlanModifyView, RecipeDeleteFromPlan


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('index/', IndexView.as_view()),
    path('main/', DashboardView.as_view(), name='dashboard'),
    path('recipe/list/', RecipeListView.as_view(), name='recipe_list'),
    path('recipe/add/', AddRecipeView.as_view(), name='add_recipe'),
    path('plan/add/', PlanAddView.as_view(), name='plan_add'),
    path('plan/list/', views.plan_list, name='plan_list'),
    path('recipe/list/<int:page>/', RecipeListView.as_view(), name='recipe_list_paginated'),
    path('plan/add-recipe/', DetailsPlanView.as_view(), name='DetailsPlanView'),
    path('plan/<int:id>/', PlanIdView.as_view(), name='plan-id'),
    path('recipe/<int:id>/', RecipeDetailsView.as_view(), name='app-recipe-details'),
    path('recipe/modify/<int:pk>/', RecipeModifyView.as_view(), name='recipe_modify'),
    path('plan/modify/<int:pk>/', PlanModifyView.as_view(), name='plan_modify')
    path('plan/delete-plan-recipe/<int:pk>/', RecipeDeleteFromPlan.as_view(), name='RecipeDeleteFromPlan'),
]
