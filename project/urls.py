from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from pfe.views import (
    UserViewSet, ClientViewSet, FactureViewSet, 
    DateChangeViewSet, MyTokenObtainPairView , client_history 
)
from pfe.views import ClientImportView , ClientExportView  
from rest_framework_simplejwt.views import TokenRefreshView
from project.api.views import get_routes
from pfe import views 
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'clients', ClientViewSet, basename='client')  
router.register(r'factures', FactureViewSet)
router.register(r'datechanges', DateChangeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/routes/', get_routes),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/clients/<int:pk>/history/', client_history),
    path('generate-pdf/<int:client_id>/', views.generate_pdf, name='generate_pdf'),
    path('api/client-stats/', views.client_stats, name='client_stats'),
    path("import-clients/", ClientImportView.as_view(), name="import-clients"),
    path("export-clients/", ClientExportView.as_view(), name="export-clients"),


    
]
