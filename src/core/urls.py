from django.contrib import admin
from django.urls import path
from core.api import *
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Incluye las rutas de tu app 'core'
]

