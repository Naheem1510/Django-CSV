from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from marks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='marks/login.html'), name='login'),
     path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('', views.home, name='home'),  # Add a home page URL
    path('', include('marks.urls')),  # Include the marks app URLs
]
