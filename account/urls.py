from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('me/', views.curent_user, name='me'),
    path('me/update/', views.update_user, name='update-profile'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]
