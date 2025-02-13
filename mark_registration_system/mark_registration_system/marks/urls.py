from django.urls import path
from .views import home, gateway, view_marks, add_marks, modify_marks, visualisation, fetch_marks_data

urlpatterns = [
    path('', gateway, name='gateway'),  # Gateway as the entry point
    path('home/', home, name='home'),  # Home page, accessible only after CAPTCHA
    path('view_marks/', view_marks, name='view_marks'),
    path('add_marks/', add_marks, name='add_marks'),
    path('modify_marks/', modify_marks, name='modify_marks'),
    path('visualisation/', visualisation, name='visualisation'),
    path('fetch_marks_data/', fetch_marks_data, name='fetch_marks_data'),
]