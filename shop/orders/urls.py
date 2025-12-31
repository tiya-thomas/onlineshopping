from django.urls import path
from . import views

urlpatterns = [
    path("buy/<int:product_id>/", views.buy_now, name="buy_now"),
    path("success/<int:order_id>/", views.order_success, name="order_success"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("received/", views.admin_orders, name="admin_orders"),
]
