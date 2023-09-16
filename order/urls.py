from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.get_orders, name='get-orders'),
    path('orders/<str:pk>', views.get_order, name='get-an-order'),
    path('orders/<str:pk>/process/',
         views.processing_order, name='processing-order'),
    path('orders/<str:pk>/delete/', views.delete_order, name='delete-order'),
    path('order/new/', views.new_order, name='new-order'),
]
