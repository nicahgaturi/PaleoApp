from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django import forms
from django.core.paginator import Paginator

from PaleoApp.models import AccessionNumber, Collection, Locality, Storage
from PaleoApp.filters import AccessionNumberFilter
from .forms import CustomUserCreationForm, GenerateAccessionNumberForm
from PaleoApp.models import ConflictLog  

import qrcode
from io import BytesIO
import base64
import logging

logger = logging.getLogger(__name__)

# -----------------------------------------
# Authentication - Signup View
# -----------------------------------------
def authView(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")  # Assumes Django auth URLs are used
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


# -----------------------------------------
# Dashboard View
# -----------------------------------------
@login_required(login_url='login')
def dashboard(request):
    return render(request, "dashboard.html")


# -----------------------------------------
# Accession Number Form & Views
# -----------------------------------------
class GenerateAccessionNumberForm(forms.ModelForm):
    locality = forms.ModelChoiceField(queryset=Locality.objects.all(), label='Locality')
    shelf_number = forms.CharField(
        max_length=100,
        required=False,
        label='Shelf Number',
        widget=forms.TextInput(attrs={'placeholder': 'Optional (N/A if not provided)'})
    )
    num_specimens = forms.IntegerField(min_value=1, label='Number of Specimens')

    class Meta:
        model = AccessionNumber
        fields = ['user', 'collection', 'locality', 'shelf_number', 'num_specimens', 'type_status', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['collection'].queryset = Collection.objects.all()

    def clean_num_specimens(self):
        shelf_number = self.cleaned_data.get('shelf_number')
        num_specimens = self.cleaned_data.get('num_specimens')
        if shelf_number and shelf_number.strip():
            if num_specimens != 1:
                raise forms.ValidationError("Number of specimens must be equal to 1 when a shelf number is provided.")
        elif num_specimens < 1:
            raise forms.ValidationError("Number of specimens must be at least 1.")
        return num_specimens

    def clean_shelf_number(self):
        shelf_number = self.cleaned_data.get('shelf_number')
        return shelf_number if shelf_number else None


@login_required(login_url='login')
def generate_accession_number(request):
    if request.method == 'POST':
        form = GenerateAccessionNumberForm(request.POST)
        if form.is_valid():
            user = request.user
            collection = form.cleaned_data['collection']
            locality = form.cleaned_data['locality']
            shelf_number = form.cleaned_data['shelf_number']
            num_specimens = form.cleaned_data['num_specimens']
            type_status = form.cleaned_data.get('type_status')
            comment = form.cleaned_data['comment'] if num_specimens == 1 else ''

            # Get or create storage
            storage, _ = Storage.objects.get_or_create(shelf_number=shelf_number)

            # Get the last accession number used in this collection
            last_accession = AccessionNumber.objects.filter(collection=collection).order_by('-number').first()
            last_number = last_accession.number if last_accession else 0
            new_number = last_number + 1

            # Check for conflicts with accession numbers in other collections
            next_global_conflict = (
                AccessionNumber.objects
                .filter(number__gte=new_number)
                .exclude(collection=collection)
                .order_by('number')
                .first()
            )
            next_conflict_number = next_global_conflict.number if next_global_conflict else None

            # Determine how many accession numbers can be assigned before a conflict
            if next_conflict_number:
                max_allowed = next_conflict_number - new_number
                if num_specimens > max_allowed:
                    conflict_collection_name = (
                        next_global_conflict.collection.name
                        if next_global_conflict and next_global_conflict.collection
                        else "another collection"
                    )

                    if max_allowed == 0:
                        # Log the conflict
                        ConflictLog.objects.create(
                            user=user,
                            collection=collection,
                            requested_specimens=num_specimens,
                            available_specimens=0,
                            conflict_number=next_conflict_number,
                            conflict_collection_name=conflict_collection_name,
                            notes="System-generated conflict log. Admin action required."
                        )

                        form.add_error('num_specimens',
                            f"No accession numbers are available before reaching number {next_conflict_number}, "
                            f"which belongs to the '{conflict_collection_name}' collection. "
                            f"Please contact the admin to assign the next set of accession numbers."
                        )
                    else:
                        form.add_error('num_specimens',
                            f"Only {max_allowed} accession number(s) are available before reaching number {next_conflict_number}, "
                            f"which belongs to the '{conflict_collection_name}' collection."
                        )
                    return render(request, 'PaleoApp/generate_accession_number.html', {'form': form})

            # Determine batch color rotation
            colors = ['green', 'black', 'blue']
            last_colored = AccessionNumber.objects.exclude(color__isnull=True).exclude(color='')\
                                                  .order_by('-date_time_accessioned').first()
            if last_colored and last_colored.color in colors:
                last_color_index = colors.index(last_colored.color)
                next_color = colors[(last_color_index + 1) % len(colors)]
            else:
                next_color = colors[0]  # Default starting color

            # Create accession numbers
            try:
                for _ in range(num_specimens):
                    AccessionNumber.objects.create(
                        user=user,
                        locality=locality,
                        storage=storage,
                        number=new_number,
                        collection=collection,
                        type_status=type_status,
                        comment=comment,
                        color=next_color
                    )
                    new_number += 1
                return redirect('PaleoApp:accession_table')
            except Exception as e:
                logger.error(f"Failed to create accession numbers: {e}")
                return HttpResponse("Error creating accession numbers", status=500)

    else:
        form = GenerateAccessionNumberForm(initial={'user': request.user})

    return render(request, 'PaleoApp/generate_accession_number.html', {'form': form})



# -----------------------------------------
# Accession Numbers Table View with QR Codes and batch coloring
# -----------------------------------------
@login_required(login_url='login')
def accession_table(request):
    accession_numbers = AccessionNumber.objects.all().order_by('-date_time_accessioned', '-number')
    accession_filter = AccessionNumberFilter(request.GET, queryset=accession_numbers)

    paginator = Paginator(accession_filter.qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    for acc in page_obj:
        qr_data = (
            f"Number: {acc.number}\n"
            f"User: {acc.user.username}\n"
            f"Collection: {acc.collection.name}\n"
            f"Locality: {acc.locality.name}\n"
            f"Type Status: {acc.type_status}\n"
            f"Comment: {acc.comment}\n"
            f"Storage: {acc.storage.shelf_number if acc.storage else 'N/A'}\n"
            f"Date Time Accessioned: {acc.date_time_accessioned}"
        )
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        qr_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        acc.qr_code = qr_image

    return render(request, 'PaleoApp/accession_table.html', {
        'page_obj': page_obj,
        'filter': accession_filter,
        'accession_numbers': page_obj,
    })


# -----------------------------------------
# Edit Shelf Number View
# -----------------------------------------
@login_required(login_url='login')
def edit_shelf_number(request, accession_number_id):
    accession_number = get_object_or_404(AccessionNumber, id=accession_number_id)

    if request.method == 'POST':
        shelf_number = request.POST.get('shelf_number')
        storage, _ = Storage.objects.get_or_create(shelf_number=shelf_number)
        accession_number.storage = storage
        accession_number.save()
        return redirect('PaleoApp:accession_table')

    return render(request, 'PaleoApp/edit_shelf_number.html', {'accession_number': accession_number})
