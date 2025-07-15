HELP_TEXTS = {
    'num_specimens': (
        'The number of fossil specimens to accession in one batch (max: 10). '
        '⚠️ All specimens you want to accession at the same time  **must come from the same locality** — no mixing localities! '
        'Example: 6 from "West Turkana" = ✅ | 3 from "West Turkana" + 3 from "Koobi Fora" = ❌ '
        'If you have more than 10 fossil specimens you want to accession (e.g. 25 from "West Turkana"), split them into batches yourself (e.g. 10, 10, 5). '
        'Generate each batch separately — the system will auto-assign different color codes for each batch (e.g. green, blue, black) for clarity.'
    ),
    'collection': (
        'Choose  where the  fossil specimen is located . '
        'Examples include “TBI” for Turkana Basin Institute could be in Ileret or Turkwel  lab   or “KNM” for the National Museums of Kenya paleontology  lab.'
    ),
    'shelf_number': (
        'Optional field. Provide the physical shelf or drawer location if known — for example, 44DD or "With Yatich". '
        'Use this only if the precise location is documented.'
    ),
    'comment': (
        'Optional notes or remarks about the accession. '
        '⚠️ Note: If the number of specimens is greater than 1 during accessioning, '
        'this comment will be automatically deleted.'
    ),
    'date_accessioned': 'The date when the specimens were accessioned into the collection.',
    'locality': (
        'The geographic location where the fossil specimen(s) were collected. '
        'For example: “West Turkana”. This must match across all specimens in the same batch.'
    ),
    'type_status': (
        'Optional field. Indicates the taxonomic significance of the specimen. Examples:\n'
        '- Holotype: The primary specimen used to describe the species.\n'
        '- Isotype: A duplicate of the holotype.\n'
        '- Neotype: A replacement type if the original holotype is missing or destroyed.'
    ),
}


RANGE_LOG_HELP_TEXT = {
    'summary': (
        "The Accession Number Range Log records every instance when a user assigns a new range of accession numbers "
        "to a specific collection. This log ensures transparency, prevents overlap, and supports long-term tracking.\n\n"
        "📌 For example: If the collection 'KNM' is assigned the range **2001–2020**, this action is logged along with "
        "the user who performed it and the exact date/time it occurred."
    ),
    'uses': [
    "🧾 **Accountability** – Track who created each range and when.",
    "🚫 **Conflict Prevention** – Prevent overlaps and ensure each accession number stays globally unique.",
    "🛠️ **System Monitoring** – Know when ranges are running out and need replenishment."
    ],

    'fields': {
        'User': "The user who generated the accession range.",
        'Collection': "The collection (e.g. KNM, TBI) that received the new accession range.",
        'Start Range': "The first accession number in the assigned range (e.g. 2001).",
        'End Range': "The last accession number in the assigned range (e.g. 2020).",
        'Date/Time': "The date and time when the range was created and logged.",
    }
}



