HELP_TEXTS = {
    'num_specimens': (
        'The number of fossil specimens to accession in one batch (max: 10). '
        '⚠️ All specimens you want to accession at the same time  **must come from the same locality** — no mixing sites! '
        'Example: 6 from "West Turkana" = ✅ | 3 from "West Turkana" + 3 from "Koobi Fora" = ❌ '
        'If you have more than 10 fossil specimens you want to accession (e.g. 25 from "West Turkana"), split them into batches yourself (e.g. 10, 10, 5). '
        'Generate each batch separately — the system will auto-assign different color codes for each batch (e.g. green, blue, black) for clarity.'
    ),
    'collection': (
        'Choose the institutional or project collection to which these specimens belong. '
        'Examples include “TBI” for Turkana Basin Institute or “KNM” for the National Museums of Kenya.'
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
