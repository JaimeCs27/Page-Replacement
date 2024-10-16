from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('simulation', views.simulation, name='simulation'),
    path('generate', views.generate_file, name='generate_file'),
    path('fetch_next_iterations', views.fetch_next_iterations, name='fetch_next_iterations'),
]