from django.http import HttpResponse
from django.urls import path


app_name = "application"
urlpatterns = [
    path("", lambda request: HttpResponse(request.path), name="root"),
]
