from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from store.models import Product, Category, ReviewRating
from orders.models import Order, OrderProduct
from vendor.forms import ProductForm, CategoryForm, AdvertisementForm
from vendor.models import  Advertisement
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
# Create your views here.s

@login_required(login_url='login')
def AdminPanel(request):
    query = request.GET.get('search')
    if query:
        products = Product.objects.filter(
            Q(product_name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__category_name__icontains=query),  # Assuming category has a `category_name` field
            is_available=True
        ).order_by('-created_date')
    else:
        products = Product.objects.filter(is_available=True).order_by('-created_date')

    context = {
        'products': products,
        'search_query': query,
    }
    return render(request, 'vendor/product_list.html', context)

def AddProduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('admin_panel') 
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm()
    
    return render(request, 'vendor/add_product.html', {'form': form})

def EditProduct(request, p_id):
    product = get_object_or_404(Product, pk=p_id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product has been updated successfully!")
            return redirect('admin_panel')  
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm(instance=product)

    return render(request, 'vendor/edit_product.html', {'form': form, 'product': product})

def DeleteProduct(request, p_id):
    product = get_object_or_404(Product, pk=p_id)

    product.delete()
    messages.success(request, "Product has been deleted successfully!")
    return redirect('admin_panel')

def orders(request):
    orders = Order.objects.all().order_by('-created_at')
    orders_count = orders.count()
    context={
        'orders':orders,
        'orders_count':orders_count,
    }
    return render(request,'vendor/orders.html',context)

def order_info(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal +=i.product_price*i.quantity

    context = {
        'order_detail': order_detail,
        'order':order,
        'subtotal':subtotal,
    }
    return render(request, 'vendor/order_detail.html', context)

def CategoriesList(request):
    categories = Category.objects.all()
    context={
        'categories':categories,
    }
    return render(request,'vendor/category_list.html',context)

def AddCategory(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully!")
            return redirect('categories') 
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CategoryForm()
    
    return render(request, 'vendor/add_category.html', {'form': form})

def ReviewRatingList(request):
    reviews = ReviewRating.objects.select_related('product', 'user').all().order_by('-created_at')

    context = {
        'reviews' : reviews
    }

    return render(request, 'vendor/reviews.html', context)

def DeleteReview(request, review_id):
    review = get_object_or_404(ReviewRating, pk=review_id)
    review.delete()
    messages.success(request, "Review deleted successfully.")
    return redirect('review_rating')

def AdvertisementView(request):
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Advertisement uploaded successfully!")
            return redirect('advertisement')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AdvertisementForm()

    ads = Advertisement.objects.all().order_by('-id') 

    context = {
        'form': form,
        'ads': ads
    }

    return render(request, 'vendor/advertisement.html', context)