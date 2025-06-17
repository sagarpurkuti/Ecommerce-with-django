from django.urls import path
from vendor import views



urlpatterns = [
    path('', views.AdminPanel, name='admin_panel'),

    path('add_product/', views.AddProduct, name='add_product'),
    path('edit_product/<int:p_id>/', views.EditProduct, name='edit_product'),
    path('delete_product/<int:p_id>/', views.DeleteProduct, name='delete_product'),

    path('orders/', views.orders, name='orders'),
    path('order_info/<int:order_id>/', views.order_info, name='order_info'),

    path('categories/', views.CategoriesList, name='categories'),
    path('add_category/', views.AddCategory, name='add_category'),
    path('del_category/<int:category_id>/', views.DeleteCategory, name='del_category'),

    path('review_rating/', views.ReviewRatingList, name='review_rating'),
    path('delete_review/<int:review_id>/', views.DeleteReview, name='delete_review'),
    
    path('advertisement/', views.AdvertisementView, name='advertisement'),

    

    
]