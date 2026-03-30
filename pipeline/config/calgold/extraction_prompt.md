You are extracting structured location data from a transcript of a "California's Gold" or
"Visiting with Huell Howser" episode. Huell Howser visits specific California locations -
landmarks, parks, restaurants, historical sites, natural wonders, museums, and communities.

For each distinct location visited in this episode, extract:

{
  "name": "Primary location name",
  "description": "2-3 sentence description of what this place is",
  "city": "City name",
  "state": "CA",
  "county": "County if mentioned",
  "address": "Street address if mentioned",
  "historical_period": "Time period if relevant (e.g., '1921-1954')",
  "builder": "Person who built/founded it if mentioned",
  "owner": "Current owner/operator if mentioned",
  "historical_figures": ["People associated with this location"],
  "actors": ["Named people featured. ALWAYS include 'Huell Howser' as the first actor. Add any featured person - park rangers, historians, business owners, chefs, docents, etc."],
  "roles": ["Normalized role types for each actor (host, park ranger, historian, chef, owner, docent, guide, curator, artist, farmer, etc.)"],
  "cuisines": ["Cuisine types if food is featured (Mexican, BBQ, Bakery, Seafood, etc.). Empty array if no food."],
  "dishes": ["Specific food items mentioned (fish tacos, date shake, tri-tip, sourdough bread, etc.). Empty array if no food."],
  "eras": ["Historical periods or time references (Gold Rush, 1920s, Spanish Colonial, Victorian, WWII, etc.). Empty array if no historical context."],
  "continents": ["Always ['North America'] for CalGold."],
  "designation": "Official designation if any (National Historic Landmark, State Park, etc.)",
  "huell_quote": "Most memorable Huell quote about this location",
  "episode_categories": ["art", "history", "food", "nature", "architecture", "community",
                          "industry", "agriculture", "science", "transportation", "military",
                          "sports", "music", "religion"],
  "aka_names": ["Alternative names for this location"],
  "visits": [
    {
      "video_id": "{VIDEO_ID}",
      "video_title": "{VIDEO_TITLE}",
      "host_intro": "First 1-2 sentences Huell says about arriving at this location",
      "timestamp_start": 0.0
    }
  ]
}

Return a JSON array of location objects. One episode may visit multiple locations.
If no specific geocodable location is identifiable, return an empty array.
