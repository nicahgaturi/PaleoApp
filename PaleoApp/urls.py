from django.urls import path, include
from . import views
from .views import authView, dashboard

app_name = "PaleoApp"

urlpatterns = [
    # Dashboard and auth (already included at root for signup and accounts)
    path("", dashboard, name="dashboard"),  # Root of the app — dashboard homepage
    # In PaleoApp/urls.py
    path("signup/", authView, name="signup"),


    # Accession management
    path("generate-accession-number/", views.generate_accession_number, name="generate_accession_number"),
    path("accession-table/", views.accession_table, name="accession_table"),
    path("edit-shelf-number/<int:accession_number_id>/", views.edit_shelf_number, name="edit_shelf_number"),
]
