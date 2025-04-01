from django.urls import path
from orders import views



urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    # path('payments/', views.payments, name='payments'),


    #for esewa
    path('orders/payment-success/', views.payment_success, name='payment-success'),
    path('orders/payment-failure/', views.payment_failure, name='payment-failure'),
    
]


 