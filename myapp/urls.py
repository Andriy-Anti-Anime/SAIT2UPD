from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]