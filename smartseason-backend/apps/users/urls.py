from django.urls import path
from .views import MeView, AgentsListView

urlpatterns = [
    path("me/",     MeView.as_view(),        name="me"),
    path("agents/", AgentsListView.as_view(), name="agents"),
]
