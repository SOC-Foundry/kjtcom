import * as functions from "firebase-functions";
/**
 * Search endpoint for kylejeromethompson.com
 *
 * Phase 0: Simple pass-through to Firestore array-contains on t_any_keywords.
 * Phase N: Add fuzzy search, geo-radius, multi-array, Gemini NLP.
 */
export declare const search: functions.https.HttpsFunction;
