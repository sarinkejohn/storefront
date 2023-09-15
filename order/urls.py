from django.urls import path
from . import views

urlpatterns = [
    path('order/new/', views.new_order, name='new-order'),
]
