from django.urls import path
from . import views

urlpatterns = [
    path('register/student/', views.student_register, name='student_register'),
    path('register/instructor/', views.instructor_register, name='instructor_register'),
    path('profile/', views.profile, name='profile'),
] 