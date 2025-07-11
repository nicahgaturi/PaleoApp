from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Collection(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10, blank=True, null=True)
    start_range = models.PositiveIntegerField(null=True, blank=True)
    end_range = models.PositiveIntegerField(null=True, blank=True)


    def __str__(self):
        return self.name

class Locality(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

class Storage(models.Model):
    shelf_number = models.CharField(max_length=100, blank=True, null=True, default='N/A')

    def __str__(self):
        return f"Shelf: {self.shelf_number}"

class AccessionNumber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.PositiveIntegerField(unique=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    date_time_accessioned = models.DateTimeField(auto_now_add=True)
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, null=True, blank=True)
    color = models.CharField(max_length=20, default='black')  

    TYPE_STATUS_OPTIONS = (
        ('Type', 'Type'),
        ('Holotype', 'Holotype'),
        ('Isotype', 'Isotype'),
        ('Lectotype', 'Lectotype'),
        ('Syntype', 'Syntype'),
        ('Isosyntype', 'Isosyntype'),
        ('Paratype', 'Paratype'),
        ('Neotype', 'Neotype'),
        ('Topotype', 'Topotype'),
    )

    type_status = models.CharField(
        max_length=50,
        choices=TYPE_STATUS_OPTIONS,
        null=True,
        blank=True,
        help_text="Please select the type status"
    )
    comment = models.TextField(
        null=True,
        blank=True,
        help_text="Any additional comments"
    )
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    def __str__(self):
        return str(self.number)
    
class ConflictLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True)
    requested_specimens = models.PositiveIntegerField()
    available_specimens = models.PositiveIntegerField(default=0)
    conflict_number = models.PositiveIntegerField()
    conflict_collection_name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Conflict for {self.collection} at number {self.conflict_number}"

