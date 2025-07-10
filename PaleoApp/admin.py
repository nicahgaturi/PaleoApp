from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.utils.safestring import mark_safe
from .models import Collection, Locality, AccessionNumber, Storage

class AccessionNumberResource(resources.ModelResource):
    class Meta:
        model = AccessionNumber
        fields = (
            "user__username", 
            "number", 
            "collection__name", 
            "locality__name", 
            "locality__abbreviation", 
            "storage__shelf_number",  # Changed to shelf_number
            "date_time_accessioned", 
            "type_status", 
            "comment"
        )
        import_id_fields = ('number',)

class AccessionNumberAdmin(ImportExportModelAdmin):
    resource_class = AccessionNumberResource
    list_display = (
        "user", 
        "number", 
        "collection", 
        "locality", 
        "locality_abbreviation", 
        "storage_display", 
        "date_time_accessioned", 
        "type_status", 
        "comment_display"
    )
    list_filter = ("number",)
    search_fields = ("number",)

    def locality_abbreviation(self, obj):
        return obj.locality.abbreviation if obj.locality else "N/A"
    locality_abbreviation.short_description = "Locality Abbreviation"

    def storage_display(self, obj):
        return obj.storage.shelf_number if obj.storage else "N/A"
    storage_display.short_description = "Storage"

    def comment_display(self, obj):
        return mark_safe(
            f'<button class="btn btn-secondary" onclick="this.nextElementSibling.classList.toggle(\'collapse\')">Toggle Comment</button>'
            f'<div class="collapse" style="display:none;">{obj.comment}</div>'
        )
    comment_display.short_description = 'Comment'

class StorageAdmin(ImportExportModelAdmin):
    list_display = ("shelf_number",)
    search_fields = ("shelf_number",)

admin.site.register(Collection, ImportExportModelAdmin)
admin.site.register(Locality, ImportExportModelAdmin)
admin.site.register(Storage, StorageAdmin)  # Register Storage
admin.site.register(AccessionNumber, AccessionNumberAdmin)
