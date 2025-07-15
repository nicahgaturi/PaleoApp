from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.utils.safestring import mark_safe
from .models import Collection, Locality, AccessionNumber, Storage,AccessionNumberRangeLog
from .models import ConflictLog


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

# Resource class for AccessionNumberRangeLog
class AccessionNumberRangeLogResource(resources.ModelResource):
    class Meta:
        model = AccessionNumberRangeLog
        fields = (
            "user__username",
            "collection__name",
            "start_range",
            "end_range",
            "generated_at",
        )
        import_id_fields = ("start_range", "end_range", "collection")


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
    list_filter = ("number","collection", "locality", "date_time_accessioned", "type_status")
    readonly_fields = ("date_time_accessioned", "user")
    search_fields = ("number","collection__name", "locality__name", "storage__shelf_number", "type_status")

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

# Admin class for AccessionNumberRangeLog
class AccessionNumberRangeLogAdmin(ImportExportModelAdmin):
    resource_class = AccessionNumberRangeLogResource
    list_display = ("user", "collection", "start_range", "end_range", "generated_at")
    list_filter = ("collection", "generated_at", "user")
    search_fields = ("user__username", "collection__name", "start_range", "end_range")
    readonly_fields = ("generated_at",)

class StorageAdmin(ImportExportModelAdmin):
    list_display = ("shelf_number",)
    search_fields = ("shelf_number",)


@admin.register(ConflictLog)
class ConflictLogAdmin(admin.ModelAdmin):
    list_display = ('collection', 'conflict_number', 'conflict_collection_name', 'requested_specimens', 'available_specimens', 'timestamp', 'resolved')
    list_filter = ('resolved', 'timestamp')
    search_fields = ('collection__name', 'conflict_collection_name', 'user__username')
    actions = ['mark_as_resolved']

    @admin.action(description='Mark selected conflicts as resolved')
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(resolved=True)
        self.message_user(request, f"{updated} conflict(s) marked as resolved.")
    

    
admin.site.register(AccessionNumberRangeLog, AccessionNumberRangeLogAdmin)
admin.site.register(Collection, ImportExportModelAdmin)
admin.site.register(Locality, ImportExportModelAdmin)
admin.site.register(Storage, StorageAdmin)  # Register Storage
admin.site.register(AccessionNumber, AccessionNumberAdmin)
