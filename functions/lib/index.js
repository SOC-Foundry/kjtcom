"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.search = void 0;
const functions = __importStar(require("firebase-functions"));
const admin = __importStar(require("firebase-admin"));
admin.initializeApp();
/**
 * Search endpoint for kylejeromethompson.com
 *
 * Phase 0: Simple pass-through to Firestore array-contains on t_any_keywords.
 * Phase N: Add fuzzy search, geo-radius, multi-array, Gemini NLP.
 */
exports.search = functions.https.onRequest(async (req, res) => {
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
    const body = req.body;
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
            .filter((k) => k.length > 1);
        // Phase 0: Simple array-contains on first keyword
        // Firestore only supports one array-contains per query
        let query = db.collection("locations");
        if (keywords.length > 0) {
            query = query.where("t_any_keywords", "array-contains", keywords[0]);
        }
        // Apply pipeline filter
        if (body.filters?.t_log_type) {
            query = query.where("t_log_type", "==", body.filters.t_log_type);
        }
        query = query.limit(limit);
        const snapshot = await query.get();
        const results = [];
        snapshot.forEach((doc) => {
            results.push({ id: doc.id, ...doc.data() });
        });
        // Phase 0: Client-side filter for additional keywords
        let filtered = results;
        if (keywords.length > 1) {
            const extraKeywords = keywords.slice(1);
            filtered = results.filter((r) => {
                const allKeywords = (r.t_any_keywords || []);
                const allNames = (r.t_any_names || []);
                const searchable = [...allKeywords, ...allNames];
                return extraKeywords.every((k) => searchable.some((s) => s.includes(k)));
            });
        }
        const response = {
            results: filtered,
            total: filtered.length,
            query: queryText,
        };
        res.status(200).json(response);
    }
    catch (error) {
        console.error("Search error:", error);
        res.status(500).json({ error: "Internal server error" });
    }
});
//# sourceMappingURL=index.js.map