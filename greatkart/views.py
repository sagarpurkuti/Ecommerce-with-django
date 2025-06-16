from django.shortcuts import render
from store.models import Product, ReviewRating
from vendor.models import Advertisement


def home(request):
    products = Product.objects.all().filter(is_available = True).order_by('-created_date')


    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    banner_ad = Advertisement.objects.order_by('-id').first()


    context = {
        'products': products,
        'reviews' : reviews,
        'banner_ad': banner_ad,
    }
    return render(request, "home.html", context)