# kjtcom — Project Summary & Future State (v10.62)

**Date:** April 06, 2026
**Version:** v10.62 (Phase 10: Platform Hardening)
**Repository:** SOC-Foundry/kjtcom
**Domain:** [kylejeromethompson.com](https://kylejeromethompson.com)

---

## 1. Executive Summary

**kjtcom** is a cross-pipeline location intelligence platform and a live case study in **Iterative Agentic Orchestration (IAO)**. 

At its core, the system acts as a data refinery: it ingests raw YouTube travel/food show playlists (like *California's Gold*, *Rick Steves' Europe*, and *Anthony Bourdain's No Reservations / Parts Unknown*), transcribes the audio, uses LLMs to extract geographic and cultural entities, normalizes the data into a unified schema, and enriches it via Google Places. 

This data is surfaced through a high-performance, SIEM-inspired Flutter Web application featuring a custom NoSQL query editor. However, the true product of `kjtcom` is not just the web app—it is the **AI Agent Harness**. The entire project is autonomously built, maintained, and evaluated by AI agents (Gemini CLI and Claude Code) operating under strict procedural guardrails, demonstrating how complex software ecosystems can be continuously integrated and deployed without human code intervention.

---

## 2. Core Functions & Architecture

The architecture is visualized in the app as a 4-board "PCB" (Printed Circuit Board) using Three.js (**Claw3D**), dividing the system into four distinct operational zones:

### A. The Data Pipeline (Amber Board)
The extraction engine that runs on local hardware (NVIDIA RTX GPUs):
*   **Acquisition & Transcription:** `yt-dlp` downloads audio, which is transcribed with word-level timestamps via `faster-whisper` (CUDA).
*   **LLM Extraction:** Gemini 2.5 Flash processes the massive transcripts to identify points of interest, people, cuisines, and quotes.
*   **Normalization:** Python scripts map the chaotic LLM output into **Thompson Indicator Fields** (`t_any_*`), inspired by Panther SIEM and Elastic Common Schema (ECS).
*   **Enrichment:** Entities are geocoded via Nominatim (OSM) and enriched with ratings/metadata via the Google Places API before being loaded into Firebase.

### B. The Frontend (Teal Board)
A Flutter Web application hosted on Firebase CDN, sporting a dark, Gothic/Cyberpunk UI:
*   **NoSQL Query Editor:** Features syntax highlighting, case-insensitive search, inline autocomplete, and advanced operators (`contains`, `contains-any`, `==`, `!=`) targeting `t_any_*` fields.
*   **Data Visualization:** Includes an OpenStreetMap integration (Map Tab) for rendering pipeline-colored markers, and a Globe Tab for continent/country statistical grids.
*   **Claw3D Architecture:** A live 3D representation of the system's components, utilizing dynamic `CanvasTexture` rendering for crisp, readable status labels.

### C. The Middleware (Purple Board)
The operational brain of the application and the agent harness:
*   **Telegram Bot (`@kjtcom_iao_bot`):** A systemd-managed bot providing mobile access to the database via natural language, featuring a 10-minute session memory.
*   **Intent Router:** A Gemini Flash layer that classifies incoming queries into three paths: direct database lookup, semantic RAG retrieval, or Brave web search.
*   **RAG Pipeline:** A ChromaDB vector database holding 1,800+ chunks of project documentation and architecture decision records (ADRs).
*   **Agent Evaluator Harness:** The mechanism that keeps the AI agents honest.

### D. The Backend (Blue Board)
*   **Cloud Firestore:** A single-collection NoSQL database utilizing multi-database environments (`(default)` for production, `staging` for pipeline processing). 

---

## 3. Current State Snapshot (v10.62)

As of Iteration **v10.62**, the system is highly stable and processing its fourth major dataset.

*   **Production Data:** 6,181 active entities spanning three fully completed pipelines (*California's Gold*, *Rick Steves*, *Diners, Drive-Ins and Dives*).
*   **Staging Data:** 536 entities from the *Anthony Bourdain* pipeline (Phase 1 of *Parts Unknown* recently completed, yielding 186 new entities).
*   **Recent Wins:**
    *   **Map Regression Fixed:** A data-type mismatch in coordinate parsing was surgically resolved, restoring all 6,181+ map markers.
    *   **Claw3D Polish:** Text rendering in the 3D architecture view was migrated to high-resolution `CanvasTexture`, eliminating overflow bugs and ensuring readability (Pattern 18 / G59 resolved).
    *   **Strict Governance:** The implementation of rigorous `post_flight.py` checks that physically prevent an iteration from completing if the agent fails to generate the required Markdown audit artifacts (Pattern 19 / G61).

---

## 4. The IAO Methodology (The Meta-Project)

The defining characteristic of `kjtcom` is **Iterative Agentic Orchestration (IAO)**. The human (Kyle) acts only as the prompter and hardware provider; the agents write the code.

1.  **The Artifact Loop:** Every iteration *must* produce four immutable documents: Design, Plan, Build Log, and Report.
2.  **Split-Agent Model:** 
    *   **Gemini CLI** handles heavy, high-volume pipeline execution and mechanical refactoring.
    *   **Claude Code** handles complex architectural reasoning, UI polish, and schema design.
3.  **Gotcha-Driven Development:** When an agent makes a critical error (e.g., using heredocs, fetching external JSON in static assets, failing to generate artifacts), it is logged as a "Gotcha" (G1 through G61) and added to the executable middleware to prevent future agents from making the same mistake.
4.  **Three-Tier Evaluation:** After an iteration, the agent's work is graded by a local `Qwen3.5-9B` model. If Qwen fails due to schema constraints, it falls back to Gemini Flash, and finally to a deterministic self-eval script.

---

## 5. Future State Goals & Roadmap

The project is currently in **Phase 10: Platform Hardening**, transitioning from a travel-data experiment into an enterprise-grade intelligence platform.

### A. Finish the Bourdain Pipeline
The immediate operational goal is to finish acquiring, transcribing, and extracting the remaining episodes of *Parts Unknown* (Items 61+), merge them with the *No Reservations* dataset, and promote the staging database to production.

### B. GCP Portability (ADR-010)
To prepare the system for enterprise/air-gapped deployments (e.g., TachTech Intranet), the platform will be abstracted away from Firebase-specific tooling.
*   **Goal:** Migrate to generic Google Cloud Platform services.
*   **Implementation:** Replace Firestore with PostgreSQL (via Cloud SQL or AlloyDB), replace Firebase Functions with Cloud Run, and use Google Secret Manager. Deployments will be harmonized using Terraform.

### C. Intranet Intelligence / Shadow SIEM (ADR-011)
The **Thompson Indicator Fields (`t_any_*`)** have proven highly effective at normalizing chaotic LLM output. The future state involves extending this schema (v4) beyond geographic locations.
*   **Goal:** Allow `kjtcom` to ingest corporate intranet data (Slack messages, Jira tickets, Google Drive documents, CRM records).
*   **Implementation:** By treating a Slack thread the same way the system treats a Bourdain transcript, the platform will become a "Shadow SIEM" for organizational knowledge, queryable via the same high-speed Flutter frontend.

### D. Hyper-Agent Optimization & Evaluator Hardening
*   **Evaluator Repair:** The local `Qwen3.5-9B` evaluator currently struggles with strict JSON schema compliance during complex context analysis. Future iterations will involve prompt tuning and schema relaxation to ensure reliable local grading.
*   **Self-Healing Pipelines:** Implementing meta-agents that monitor extraction success rates in real-time, automatically adjusting prompts or switching between LLMs (Gemini, Claude, GPT-4o) if data quality drops during a pipeline run.

---
*Generated by Gemini CLI — April 06, 2026*