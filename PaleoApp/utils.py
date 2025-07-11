from django.db.models import Max
from PaleoApp.models import Collection, ConflictLog

def assign_range_to_collection(collection, block_size=20, auto_expand=False, user=None):
    """
    Assigns or auto-expands the accession number range for a collection.

    Parameters:
    - collection: Collection instance
    - block_size: number of accession numbers to allocate per range
    - auto_expand: if True, extends the range when it is full
    - user: the user requesting accession numbers (used for logging)

    Returns:
    - True if a new range was assigned or expanded, False otherwise
    """
    last_end = Collection.objects.exclude(end_range__isnull=True).aggregate(
        max_range=Max('end_range'))['max_range'] or 0

    if collection.start_range is None or collection.end_range is None:
        start = last_end + 1
        end = start + block_size - 1
        collection.start_range = start
        collection.end_range = end
        collection.save()
        return True

    # Check if auto-expansion is required
    last_used = collection.accessionnumber_set.aggregate(
        max_number=Max('number'))['max_number'] or (collection.start_range - 1)

    if auto_expand and last_used >= collection.end_range:
        old_end = collection.end_range
        start = last_end + 1
        end = start + block_size - 1
        collection.end_range = end
        collection.save()

        # Notify admin of auto-expansion via ConflictLog
        ConflictLog.objects.create(
            user=user,
            collection=collection,
            requested_specimens=0,
            available_specimens=0,
            conflict_number=end,
            conflict_collection_name=collection.name,
            notes=(
                f"System auto-expanded collection range from {collection.start_range}-{old_end} "
                f"to {collection.start_range}-{end}."
            )
        )
        return True

    return False
