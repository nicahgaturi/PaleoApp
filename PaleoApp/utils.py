from django.db.models import Max
from PaleoApp.models import Collection

def assign_range_to_collection(collection, block_size=20):
    """
    Assigns an initial accession number range for a collection if not already assigned.

    Parameters:
    - collection: Collection instance
    - block_size: number of accession numbers to allocate per range

    Returns:
    - True if a new range was assigned, False if already assigned
    """
    if collection.start_range is None or collection.end_range is None:
        last_end = Collection.objects.exclude(end_range__isnull=True).aggregate(
            max_range=Max('end_range'))['max_range'] or 0
        start = last_end + 1
        end = start + block_size - 1
        collection.start_range = start
        collection.end_range = end
        collection.save()
        return True
    return False
