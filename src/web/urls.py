from django.urls import path

from .views import batch
from .views import home
from .views import new_batch


urlpatterns = [
    path("", home, name="home"),
    path("batch/<int:pk>/", batch, name="batch"),
    path("batch/new/", new_batch, name="new_batch"),
]
