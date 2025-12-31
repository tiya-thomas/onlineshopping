from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Product, Category

def product_list(request):
    if request.user.is_superuser:
        products= Product.objects.all()
    else:
        products = Product.objects.all()
    return render(request, "product_list.html", {"products": products})


def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def product_add(request):
    categories = Category.objects.filter(is_active=True)

    if request.method == "POST":
        name = request.POST.get("name")
        category_id = request.POST.get("category")
        new_category_name = request.POST.get("new_category", "").strip()
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        image = request.FILES.get("image")
        is_active = True 

        # Basic validation
        if not all([name, description, price, stock]) or not (category_id or new_category_name):
            messages.error(
                request,
                "Name, description, price, stock, and a category are required."
            )
            return redirect("product_add")

        category = None
        if new_category_name:
            category, _ = Category.objects.get_or_create(
                name=new_category_name,
                defaults={"is_active": True}
            )
        else:
            category = Category.objects.filter(id=category_id, is_active=True).first()

        if category is None:
            messages.error(request, "Please select or create a valid category.")
            return redirect("product_add")

        Product.objects.create(
            name=name,
            category=category,
            description=description,
            price=price,
            stock=stock,
            image=image,
            is_active=is_active
        )

        messages.success(request, "Product added successfully.")
        return redirect("product_list")

    return render(
        request,
        "product_add.html",
        {"categories": categories}
    )

def product_detail(request, id):
    if request.user.is_superuser:
        product=get_object_or_404(Product,id=id)
    else:
        product = get_object_or_404(Product, id=id)
    return render(request, "product_detail.html", {"product": product})


@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    """
    Allow admins to remove a product quickly.
    Uses POST to avoid accidental deletions from simple link clicks.
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("product_detail", pk=pk)

    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect("product_list")


@login_required
@user_passes_test(is_admin)
def category_add(request):
    """
    Minimal category creator for admins to seed catalog without Django admin.
    """
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        is_active = True if request.POST.get("is_active") else False

        if not name:
            messages.error(request, "Category name is required.")
            return redirect("category_add")

        category, created = Category.objects.get_or_create(
            name=name,
            defaults={"is_active": 1}
        )

        if not created:
            # If it existed, update its active state for convenience.
            category.is_active = 1
            category.save(update_fields=["is_active"])
            messages.info(request, "Category updated.")
        else:
            messages.success(request, "Category created.")

        return redirect("product_add")

    categories = Category.objects.all().order_by("name")
    return render(request, "category_add.html", {"categories": categories})
    