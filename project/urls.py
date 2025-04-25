from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from pfe.views import (
    UserViewSet, ClientViewSet, FactureViewSet, 
    DateChangeViewSet, MyTokenObtainPairView
)
from rest_framework_simplejwt.views import TokenRefreshView
from project.api.views import get_routes

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'clients', ClientViewSet, basename='client')  # ✅ basename added here!
router.register(r'factures', FactureViewSet)
router.register(r'datechanges', DateChangeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/routes/', get_routes),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
]
