import django_filters
from .models import AccessionNumber

class AccessionNumberFilter(django_filters.FilterSet):
    accession_number = django_filters.NumberFilter(field_name='number', lookup_expr='exact')  # Use NumberFilter for exact matches
    user__username = django_filters.CharFilter(lookup_expr='icontains')
    collection__name = django_filters.CharFilter(lookup_expr='icontains')
    locality__name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = AccessionNumber
        fields = ['accession_number', 'user__username', 'collection__name', 'locality__name']
