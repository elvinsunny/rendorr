# urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('', views.home, name='home'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('login/', views.custom_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),  # Corrected path for LogoutView
    path('register/', views.register, name='register'),
    path('users/', views.user_list, name='user_list'),
    path('categorize/', views.categorize_joke, name='categorize_joke'),
    path('joke_feedback/<int:joke_id>/<str:feedback_type>/', views.joke_feedback, name='joke_feedback'),
    path('joke_feedbacks/<int:joke_id>/<str:feedback_type>/', views.joke_feedbacks, name='joke_feedbacks'),
   
    path('liked-jokes/', views.liked_jokes, name='liked_jokes'),

    path('pie_chart/', views.pie_chart, name='pie_chart'),
    path('user_time_spent_chart/', views.user_time_spent_chart, name='user_time_spent_chart'),


    path('visualization-selection/', views.visualization_selection, name='visualization_selection'),

    path('user_time_spent_chart/', views.user_time_spent_chart, name='user_time_spent_chart'),
    path('likes_dislikes_chart/', views.likes_dislikes_chart, name='likes_dislikes_chart'),


    path('generate-joke/', views.generate_joke, name='generate_joke'),

    path('generate-jok/', views.generate_jok, name='generate_jok'),

    # path('g/', views.classify_joke, name='classify_joke'),
    







]
