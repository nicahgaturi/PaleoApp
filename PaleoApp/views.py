from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django import forms
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .helpers import HELP_TEXTS  
from PaleoApp.helpers import RANGE_LOG_HELP_TEXT
from django.core.paginator import Paginator


from PaleoApp.models import AccessionNumber, Collection, Locality, Storage
from PaleoApp.filters import AccessionNumberFilter
from .forms import CustomUserCreationForm, GenerateAccessionNumberForm
from PaleoApp.models import ConflictLog  
from PaleoApp.utils import assign_range_to_collection
from django.db.models import Max
from django.contrib import messages
from django.urls import reverse
from django.utils.http import urlencode
from PaleoApp.models import AccessionNumberRangeLog
from django.db.models import Q





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
            return redirect("login")  
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

# Helper function for collections data
def _build_collections_data():
    collections = []
    for collection in Collection.objects.all():
        collections.append({
            'id': collection.id,
            'name': collection.name,
            'start_range': collection.start_range,
            'end_range': collection.end_range,
        })
    return collections


@login_required(login_url='login')
def generate_accession_number(request):
    is_range_full = False
    collection_selected = None
    form = GenerateAccessionNumberForm(initial={'user': request.user})

    if request.method == 'POST':
        form = GenerateAccessionNumberForm(request.POST)
        if form.is_valid():
            user = request.user
            collection = form.cleaned_data['collection']
            collection_selected = collection
            locality = form.cleaned_data['locality']
            shelf_number = form.cleaned_data['shelf_number']
            num_specimens = form.cleaned_data['num_specimens']
            type_status = form.cleaned_data.get('type_status')
            comment = form.cleaned_data['comment'] if num_specimens == 1 else ''

            assign_range_to_collection(collection)

            storage, _ = Storage.objects.get_or_create(shelf_number=shelf_number)

            # Get all used numbers in collection
            used_numbers = set(
                AccessionNumber.objects.filter(collection=collection)
                .values_list('number', flat=True)
            )
            full_range = set(range(collection.start_range, collection.end_range + 1))
            available_numbers = sorted(full_range - used_numbers)

            if not available_numbers:
                # No numbers left in range, redirect to new range generation
                messages.warning(
                    request,
                    f"The current accession number range ({collection.start_range}-{collection.end_range}) for '{collection.name}' is exhausted. Please generate a new range."
                )
                return redirect('PaleoApp:generate_new_range', collection_id=collection.id)

            if len(available_numbers) < num_specimens:
                remaining = len(available_numbers)
                requested = num_specimens
                remaining_to_generate = requested - remaining  # <-- calculate difference here

                form.add_error(
                    'num_specimens',
                    f"Only {remaining} accession number(s) left in current range ({collection.start_range}-{collection.end_range})."
                )
                return render(request, 'PaleoApp/generate_accession_number.html', {
                    'form': form,
                    'is_range_full': False,
                    'collection_selected': collection_selected,
                    'collections_data': _build_collections_data(),
                    'warning_low_range': True,
                    'remaining_numbers': remaining,
                    'requested_numbers': requested,
                    'remaining_to_generate': remaining_to_generate,   
                })



            # Check for conflicts with other collections (global conflict)
            new_number = available_numbers[0]
            next_global_conflict = (
                AccessionNumber.objects
                .filter(number__gte=new_number)
                .exclude(collection=collection)
                .order_by('number')
                .first()
            )
            next_conflict_number = next_global_conflict.number if next_global_conflict else None

            if next_conflict_number:
                max_allowed = next_conflict_number - new_number
                if num_specimens > max_allowed:
                    conflict_collection_name = next_global_conflict.collection.name if next_global_conflict and next_global_conflict.collection else "another collection"
                    if max_allowed == 0:
                        ConflictLog.objects.create(
                            user=user,
                            collection=collection,
                            requested_specimens=num_specimens,
                            available_specimens=0,
                            conflict_number=next_conflict_number,
                            conflict_collection_name=conflict_collection_name,
                            notes="System-generated conflict log. Admin action required."
                        )
                        form.add_error(
                            'num_specimens',
                            f"No accession numbers available before {next_conflict_number} (owned by '{conflict_collection_name}'). Contact admin."
                        )
                    else:
                        form.add_error(
                            'num_specimens',
                            f"Only {max_allowed} accession number(s) available before number {next_conflict_number} (owned by '{conflict_collection_name}')."
                        )
                    return render(request, 'PaleoApp/generate_accession_number.html', {
                        'form': form,
                        'is_range_full': False,
                        'collection_selected': collection_selected,
                        'collections_data': _build_collections_data()
                    })

            # Cycle color for new accession numbers
            colors = ['green', 'black', 'blue']
            last_colored = AccessionNumber.objects.exclude(color__isnull=True).exclude(color='')\
                                                  .order_by('-date_time_accessioned').first()
            next_color = colors[0]
            if last_colored and last_colored.color in colors:
                last_color_index = colors.index(last_colored.color)
                next_color = colors[(last_color_index + 1) % len(colors)]

            # Create accession numbers from the lowest available numbers (gaps-first)
            try:
                for number in available_numbers[:num_specimens]:
                    AccessionNumber.objects.create(
                        user=user,
                        locality=locality,
                        storage=storage,
                        number=number,
                        collection=collection,
                        type_status=type_status,
                        comment=comment,
                        color=next_color
                    )
                return redirect('PaleoApp:accession_table')
            except Exception as e:
                logger.error(f"Failed to create accession numbers: {e}")
                return HttpResponse("Error creating accession numbers", status=500)

        else:
            collection_selected = form.cleaned_data.get('collection')
            if collection_selected:
                current_max = AccessionNumber.objects.filter(collection=collection_selected).aggregate(Max('number'))['number__max']
                if current_max is not None:
                    is_range_full = current_max >= collection_selected.end_range

    else:
        form = GenerateAccessionNumberForm(initial={'user': request.user})
        if 'collection' in request.GET:
            try:
                collection_selected = Collection.objects.get(pk=request.GET['collection'])
            except Collection.DoesNotExist:
                collection_selected = None

    collections_data = _build_collections_data()

    return render(request, 'PaleoApp/generate_accession_number.html', {
        'form': form,
        'is_range_full': is_range_full,
        'collection_selected': collection_selected,
        'collections_data': collections_data,
    })







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



@login_required(login_url='login')
def generate_new_range(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    last_used_number = AccessionNumber.objects.filter(collection=collection).aggregate(
        Max('number'))['number__max'] or (collection.start_range - 1)

    is_range_full = last_used_number >= collection.end_range

    if request.method == 'POST' and is_range_full:
        block_size = 20
        last_global_end = Collection.objects.exclude(end_range__isnull=True).aggregate(
            Max('end_range'))['end_range__max'] or 0

        new_start = last_global_end + 1
        new_end = new_start + block_size - 1

        collection.start_range = new_start
        collection.end_range = new_end
        collection.save()

        AccessionNumberRangeLog.objects.create(
            user=request.user,
            collection=collection,
            start_range=new_start,
            end_range=new_end,
        )

        # ✅ Send email notification
        subject = f"New Range Generated for {collection.name}"
        message = (
            f"A new accession number range has been generated for the collection '{collection.name}':\n\n"
            f"Range: {new_start} – {new_end}\n"
            f"Generated by: {request.user.username}\n"
        )

        # notify: Admins + users in that collection
        recipients = [user.email for user in User.objects.filter(is_superuser=True)]
        
        # TO DO: WILL ADD collection-specific users here (THEN I WILL CREATE  a relation in collection model)
        # recipients += [user.email for user in collection.users.all()]

        send_mail(subject, message, None, recipients, fail_silently=False)

        messages.success(request, f"New accession number range {new_start}–{new_end} assigned to '{collection.name}'.")

        url = reverse('PaleoApp:generate_accession_number')
        query_string = urlencode({'collection': collection.id})
        return redirect(f'{url}?{query_string}')

    return render(request, 'PaleoApp/generate_new_range.html', {
        'collection': collection,
        'is_range_full': is_range_full,
        'user': request.user
    })


@login_required(login_url='login')
def accession_number_range_log(request):
    # Filter params
    user_query = request.GET.get('user', '').strip()
    collection_query = request.GET.get('collection', '').strip()

    logs = AccessionNumberRangeLog.objects.select_related('user', 'collection').order_by('-generated_at')

    if user_query:
        logs = logs.filter(user__username__icontains=user_query)

    if collection_query:
        logs = logs.filter(collection__name__icontains=collection_query)

    paginator = Paginator(logs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'PaleoApp/accession_number_range_log.html', {
        'page_obj': page_obj,
    })

@login_required(login_url='login')
def help_page(request, field_name):
    return render(request, 'PaleoApp/field_help.html', {
        'field_name': field_name,
        'help_text': HELP_TEXTS.get(field_name, 'No help available for this field.'),
    })

@login_required(login_url='login')
def glossary_page(request):
    return render(request, 'PaleoApp/glossary.html', {
        'help_texts': HELP_TEXTS,
    })


@login_required(login_url='login')
def range_log_help(request):
    return render(request, 'PaleoApp/range_log_help.html', {
        'summary': RANGE_LOG_HELP_TEXT['summary'],
        'uses': RANGE_LOG_HELP_TEXT['uses'],
        'fields': RANGE_LOG_HELP_TEXT['fields'],
    })

