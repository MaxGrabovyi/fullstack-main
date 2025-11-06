from django.urls import path, include # type: ignore
from .views import ProductViewSet, OrderViewSet, CategoryViewSet
from .views import place_order
from .views import home
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views
from rest_framework.routers import DefaultRouter # type: ignore

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),  # JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-orders/', views.all_orders),
    path('user-role/', views.user_role),
    path('address/', views.delivery_address_view),
    path('orders/', OrderViewSet.as_view({'post': 'create'})),  
    path("place-order/", place_order, name="place_order"),

   path('', include(router.urls)),
   path('', home),
]
