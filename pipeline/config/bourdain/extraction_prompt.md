You are extracting structured location and entity data from a transcript of an
Anthony Bourdain travel/food show episode. Bourdain visits restaurants, street food
vendors, markets, bars, neighborhoods, and cultural landmarks around the world.

Shows include: No Reservations, Parts Unknown, A Cook's Tour, The Layover.

For each distinct location or establishment visited in this episode, extract:

{
  "name": "Primary location/restaurant/vendor name",
  "description": "2-3 sentence description of what this place is and what Bourdain experienced there",
  "city": "City name",
  "state": "State/province if applicable",
  "county": "County/district if mentioned",
  "country": "Country name",
  "country_code": "ISO 3166-1 alpha-2 code (US, FR, VN, JP, etc.)",
  "continent": "Continent name (North America, Europe, Asia, South America, Africa, Oceania)",
  "address": "Street address if mentioned",
  "neighborhood": "Neighborhood or district name if mentioned",
  "people": ["Named people featured - chefs, owners, guides, locals, other personalities"],
  "actors": ["Named people featured. ALWAYS include 'Anthony Bourdain' as the first actor. Add any featured person - chefs, owners, friends, fixers, locals."],
  "roles": ["Normalized role types for each actor (host, chef, owner, guide, local, friend, fixer, producer, etc.)"],
  "shows": ["Specific show name: 'No Reservations', 'Parts Unknown', 'A Cook''s Tour', or 'The Layover'"],
  "cuisines": ["Cuisine types featured (Vietnamese, French, Mexican, BBQ, Street Food, Seafood, etc.)"],
  "dishes": ["Specific dishes or food items mentioned (pho, bun cha, cassoulet, tacos al pastor, bone marrow, etc.)"],
  "eras": ["Historical periods or cultural references if relevant. Empty array if none."],
  "keywords": ["Relevant tags: street food, fine dining, market, dive bar, family-run, Michelin, hole-in-wall, local favorite, etc."],
  "categories": ["food", "market", "bar", "street_food", "fine_dining", "cultural", "neighborhood", "history"],
  "bourdain_quote": "Most memorable Bourdain quote about this location",
  "visits": [
    {
      "video_id": "{VIDEO_ID}",
      "video_title": "{VIDEO_TITLE}",
      "context": "Brief description of the visit context",
      "timestamp_start": 0.0
    }
  ]
}

Return a JSON array of location/entity objects. One episode typically visits multiple locations.
Bourdain episodes are dense - expect 5-15 distinct locations per episode.
If a location name is unclear but a city/neighborhood is identifiable, use the neighborhood or
market name as the primary name.
If no specific geocodable location is identifiable, return an empty array.
