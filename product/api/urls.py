from django.urls import path
from . import views


urlpatterns = [
    path('', views.getRoutes),
    path('products/', views.get_products,),
    path('product/upload_images/', views.upload_product_images,
         name='upload_product_images'),
    path('products/<str:pk>', views.get_product,),
    path('product/<str:pk>/update/', views.update_product, name='update_product'),
    path('product/<str:pk>/delete/', views.delete_product, name='delete_product'),
    path('product/new/', views.new_product, name='New_product'),


]
