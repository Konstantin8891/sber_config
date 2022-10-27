from django.contrib import admin
from django.urls import path
from api.views import ConfigAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('config', ConfigAPIView.as_view(), name='config')
]
