from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
import core.api.api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls', namespace='core')),
    path('api/v1/items/', core.api.api_views.ItemList.as_view()),
    path('api/v1/items/new', core.api.api_views.ItemCreate.as_view()),
    path('api/v1/items/<int:id>/',
         core.api.api_views.ItemRetrieveUpdateDestroy.as_view()),
    path('api/v1/items/<int:id>/stats',
         core.api.api_views.ItemStats.as_view()),
    path('login/', LoginView.as_view(), name='login'),



] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
