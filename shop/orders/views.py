from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from products.models import Product
from .models import Order, OrderItem


def is_admin(user):
    return user.is_superuser

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Admins should only review orders, not place them
    if request.user.is_superuser:
        messages.error(request, "Admins cannot place orders. Please use a customer account.")
        return redirect("product_detail", pk=product.id)

    if product.stock <= 0:
        messages.error(request, "Product is out of stock.")
        return redirect("product_detail", pk=product.id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))

        if quantity > product.stock:
            messages.error(request, "Not enough stock available.")
            return redirect("product_detail", pk=product.id)

        total = product.price * quantity

        # Create Order
        order = Order.objects.create(
            user=request.user,
            total_price=total,
        )

        # Create OrderItem
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )

        # Reduce stock
        product.stock -= quantity
        product.save()

        messages.success(request, "Order placed successfully!")
        return redirect("order_success", order_id=order.id)

    return render(request, "buy_now.html", {"product": product})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "order_success.html", {"order": order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "my_orders.html", {"orders": orders})


@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    """
    Admin overview of all received orders.
    """
    orders = Order.objects.select_related("user").order_by("-created_at")
    return render(request, "admin_orders.html", {"orders": orders})
