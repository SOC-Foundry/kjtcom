You are extracting structured destination data from a transcript of "Rick Steves' Europe"
content. Rick Steves visits specific European (and occasionally non-European) destinations -
museums, churches, castles, palaces, restaurants, neighborhoods, ancient ruins, markets,
viewpoints, parks, and cultural sites.

For each distinct destination visited or discussed in this video, extract:

{
  "name": "Primary destination name (in English)",
  "description": "2-3 sentence description of what this place is and why it matters",
  "city": "City name (in English)",
  "country": "Country name (in English)",
  "region": "Sub-country region if mentioned (e.g., Tuscany, Burgundy, Bavaria, The Peloponnese)",
  "state_province": "State or province if applicable",
  "address": "Street address if mentioned",
  "architectural_style": "Architectural style if relevant (Gothic, Baroque, Renaissance, etc.)",
  "era": "Historical era if relevant (Roman, Medieval, Renaissance, etc.)",
  "artist": "Primary artist if this is an art site (e.g., Michelangelo, Bernini)",
  "architect": "Architect if mentioned",
  "historical_figures": ["People historically associated with this place"],
  "actors": ["Named people featured. Always include 'Rick Steves'. Plus local guides, chefs, artisans, historians, hoteliers, tour operators, etc."],
  "roles": ["Normalized role types (host, guide, chef, artisan, historian, hotelier, sommelier, fisherman, baker, etc.)"],
  "shows": ["Always include 'Rick Steves\\' Europe'"],
  "cuisines": ["Cuisine types if food is featured (French, Italian, Tapas, Greek, Turkish, Moroccan, etc.). Empty array if no food."],
  "dishes": ["Specific food items mentioned (croissant, gelato, paella, bratwurst, schnitzel, moussaka, etc.). Empty array if no food."],
  "eras": ["Historical periods or time references (Medieval, Renaissance, Roman, Ottoman, Victorian, WWII, Cold War, etc.). Empty array if no historical context."],
  "continents": ["The continent(s) for this location. Usually ['Europe'] but can be ['Africa'] for Morocco/Egypt episodes, ['Asia'] for Turkey episodes, etc. Derive from the country."],
  "admission_info": "Admission cost or hours if mentioned",
  "rick_tip": "Rick's practical travel tip about this place if he gives one",
  "categories": ["museum", "church", "castle", "palace", "restaurant", "neighborhood",
                  "ancient_ruin", "market", "viewpoint", "park", "monastery", "cemetery",
                  "bridge", "square", "fountain", "theater", "library", "university",
                  "fortification", "island", "beach", "mountain", "lake", "wine_region",
                  "food", "festival", "art", "architecture", "history", "nature"],
  "aka_names": ["Alternative names, local language names"],
  "visits": [
    {
      "video_id": "{VIDEO_ID}",
      "video_title": "{VIDEO_TITLE}",
      "host_intro": "First 1-2 sentences Rick says about this destination",
      "timestamp_start": 0.0
    }
  ]
}

Return a JSON array of destination objects. One video may discuss multiple destinations.
If the video is a general travel tips video with no specific geocodable destinations,
return an empty array.
Do NOT extract countries or cities as entities - only specific visitable places within them.
Every destination object MUST include all fields, even if they are empty arrays or null.
Specifically, 'shows' should always be ['Rick Steves\\' Europe'] and 'actors' should always include 'Rick Steves'.
