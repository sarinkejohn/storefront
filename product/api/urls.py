from django.urls import path
from . import views


urlpatterns = [
    path('', views.getRoutes),
    path('products/', views.get_products,),
    path('product/upload_images/', views.upload_product_images,
         name='upload_product_images'),
    path('products/<str:pk>', views.get_product,),


]
