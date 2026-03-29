import * as functions from "firebase-functions";
import * as admin from "firebase-admin";

admin.initializeApp();

interface SearchRequest {
  query: string;
  filters?: {
    t_log_type?: string | null;
    t_any_states?: string;
    "t_enrichment.google_places.still_open"?: boolean;
    geo_near?: {
      lat: number;
      lon: number;
      radius_miles: number;
    };
  };
  sort?: string;
  sort_order?: "asc" | "desc";
  limit?: number;
}

interface SearchResult {
  results: admin.firestore.DocumentData[];
  total: number;
  query: string;
}

/**
 * Search endpoint for kylejeromethompson.com
 *
 * Phase 0: Simple pass-through to Firestore array-contains on t_any_keywords.
 * Phase N: Add fuzzy search, geo-radius, multi-array, Gemini NLP.
 */
export const search = functions.https.onRequest(async (req, res) => {
  // CORS
  res.set("Access-Control-Allow-Origin", "*");
  res.set("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.set("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.status(204).send("");
    return;
  }

  if (req.method !== "POST") {
    res.status(405).json({ error: "Method not allowed. Use POST." });
    return;
  }

  const body = req.body as SearchRequest;
  const queryText = (body.query || "").trim().toLowerCase();
  const limit = Math.min(body.limit || 20, 100);

  if (!queryText) {
    res.status(400).json({ error: "query is required" });
    return;
  }

  try {
    const db = admin.firestore();

    // Tokenize query into keywords
    const keywords = queryText
      .split(/\s+/)
      .filter((k: string) => k.length > 1);

    // Phase 0: Simple array-contains on first keyword
    // Firestore only supports one array-contains per query
    let query: admin.firestore.Query = db.collection("locations");

    if (keywords.length > 0) {
      query = query.where("t_any_keywords", "array-contains", keywords[0]);
    }

    // Apply pipeline filter
    if (body.filters?.t_log_type) {
      query = query.where("t_log_type", "==", body.filters.t_log_type);
    }

    query = query.limit(limit);

    const snapshot = await query.get();

    const results: admin.firestore.DocumentData[] = [];
    snapshot.forEach((doc) => {
      results.push({ id: doc.id, ...doc.data() });
    });

    // Phase 0: Client-side filter for additional keywords
    let filtered = results;
    if (keywords.length > 1) {
      const extraKeywords = keywords.slice(1);
      filtered = results.filter((r) => {
        const allKeywords = (r.t_any_keywords || []) as string[];
        const allNames = (r.t_any_names || []) as string[];
        const searchable = [...allKeywords, ...allNames];
        return extraKeywords.every((k: string) =>
          searchable.some((s: string) => s.includes(k))
        );
      });
    }

    const response: SearchResult = {
      results: filtered,
      total: filtered.length,
      query: queryText,
    };

    res.status(200).json(response);
  } catch (error) {
    console.error("Search error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});
