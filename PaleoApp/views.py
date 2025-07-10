from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django import forms
from django.core.paginator import Paginator


from PaleoApp.models import AccessionNumber, Collection, Locality, Storage
from PaleoApp.filters import AccessionNumberFilter
from .forms import CustomUserCreationForm  # Your custom signup form

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
    return render(request, "dashboard.html")  # Or "home.html" if preferred


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
            collection = form.cleaned_data['collection']
            locality = form.cleaned_data['locality']
            user = request.user
            shelf_number = form.cleaned_data['shelf_number']
            num_specimens = form.cleaned_data['num_specimens']

            storage, _ = Storage.objects.get_or_create(shelf_number=shelf_number)
            last_accession = AccessionNumber.objects.filter(collection=collection).order_by('-number').first()
            new_number = last_accession.number + 1 if last_accession else 1

            try:
                for _ in range(num_specimens):
                    AccessionNumber.objects.create(
                        user=user,
                        locality=locality,
                        storage=storage,
                        number=new_number,
                        collection=collection,
                        type_status=form.cleaned_data.get('type_status'),
                        comment=form.cleaned_data['comment'] if num_specimens == 1 else ''
                    )
                    new_number += 1
                return redirect('PaleoApp:accession_table')
            except Exception as e:
                logger.error(f"Failed to create accession number: {e}")
                return HttpResponse("Error creating accession numbers", status=500)
    else:
        form = GenerateAccessionNumberForm()
    return render(request, 'PaleoApp/generate_accession_number.html', {'form': form})


@login_required(login_url='login')
def accession_table(request):
    accession_numbers = AccessionNumber.objects.all().order_by('-date_time_accessioned')
    accession_filter = AccessionNumberFilter(request.GET, queryset=accession_numbers)

    # PAGINATE — 10 per page
    paginator = Paginator(accession_filter.qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Generate QR codes for visible items only
    for accession_number in page_obj:
        qr_data = (
            f"Number: {accession_number.number}\n"
            f"User: {accession_number.user.username}\n"
            f"Collection: {accession_number.collection.name}\n"
            f"Locality: {accession_number.locality.name}\n"
            f"Type Status: {accession_number.type_status}\n"
            f"Comment: {accession_number.comment}\n"
            f"Storage: {accession_number.storage.shelf_number if accession_number.storage else 'N/A'}\n"
            f"Date Time Accessioned: {accession_number.date_time_accessioned}"
        )
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        qr_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        accession_number.qr_code = qr_image

    return render(request, 'PaleoApp/accession_table.html', {
        'page_obj': page_obj,
        'filter': accession_filter,
        'accession_numbers': page_obj,  # Update loop to use paginated queryset
    })



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
