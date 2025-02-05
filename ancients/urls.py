from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("ancients/admin/", admin.site.urls),
    path("ancients/", include("places.urls"))
]