from django.urls import path
from . import views

urlpatterns = [
    path('product/', views.product_list, name='product_list'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('product/add/', views.product_add, name='product_add'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('category/add/', views.category_add, name='category_add'),
]