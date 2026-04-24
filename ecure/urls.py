from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_prescription, name='upload_prescription'),
    path('add_cart/<int:medicine_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('search/', views.search, name='search'),
    path('medicine/<int:id>/', views.medicine_detail, name='medicine_detail'),
    path('category/<str:category_name>/', views.category, name='category'),
    path('article/<int:id>/', views.article_detail, name='article_detail'),
    path('articles/', views.all_articles, name='all_articles'),
    path('brand/<str:brand_name>/', views.brand_products, name='brand'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('update-quantity/<int:item_id>/<str:action>/', views.update_quantity, name='update_quantity'),
    path('about/', views.about, name='about'),

]


