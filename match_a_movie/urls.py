
from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", accounts_views.HomeView.as_view(), name="home"),
    path('accounts/', include('accounts.urls')),
    path('rooms/', include('rooms.urls')),
    path('movies/', include('movies.urls')),
]
