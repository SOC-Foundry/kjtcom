#!/usr/bin/env python3
"""kjtcom IAO Telegram Bot - routes commands to kjtcom agents and middleware. P3 logged.

Commands:
    /status  - Ollama model status, system health, event log stats
    /query   - Firestore query description (informational)
    /evaluate [version] - Run Qwen evaluator against an iteration
    /gotcha  - List active gotchas
    /scores  - Agent leaderboard
    /ask [question] - Dual retrieval Q&A (Firestore entities + ChromaDB archive)
    /search [query] - Brave Search API -> OpenClaw (Gemini) for summary

Requires: KJTCOM_TELEGRAM_BOT_TOKEN environment variable
Security: Bot restricted to authorized user IDs only
"""
import os
import sys
import json
import logging
import subprocess
import time
import requests
import sdnotify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

sys.path.insert(0, os.path.dirname(__file__))
from utils.iao_logger import log_event
from utils.ollama_config import merge_defaults
from query_rag import query as rag_query
from intent_router import route_question
from firestore_query import execute_query as firestore_execute

# Config
KJTCOM_TELEGRAM_BOT_TOKEN = os.environ.get('KJTCOM_TELEGRAM_BOT_TOKEN')
OLLAMA_URL = 'http://localhost:11434'
AUTHORIZED_USERS = set()  # Empty = allow all. Add Telegram user IDs to restrict.
PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# Session memory (v9.43) - stores last query context per Telegram user_id
# Keys: user_id -> {"filters": {}, "results": [], "count": int, "timestamp": float}
# TTL: 10 minutes. Lost on restart (acceptable).
user_sessions = {}
SESSION_TTL = 600  # 10 minutes


def resolve_context(question, user_id):
    """Detect references to previous results and inject context.

    Returns the previous session dict if context words found and session is fresh,
    else None.
    """
    context_words = ["those", "them", "the results", "that list", "from before",
                     "out of those", "out of them", "from that", "of those"]
    question_lower = question.lower()
    if any(word in question_lower for word in context_words):
        session = user_sessions.get(user_id)
        if session and (time.time() - session["timestamp"]) < SESSION_TTL:
            log_event("command", "telegram-bot", "session-memory", "resolve-context",
                      input_summary=f"user={user_id}, context_count={session['count']}",
                      status="success")
            return session
    return None

# systemd watchdog notifier (v9.42)
sd_notifier = sdnotify.SystemdNotifier()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def check_auth(update: Update) -> bool:
    """Check if user is authorized. Empty set = allow all."""
    if not AUTHORIZED_USERS:
        return True
    return update.effective_user.id in AUTHORIZED_USERS


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Ollama model status and system health."""
    if not check_auth(update):
        await update.message.reply_text('Unauthorized.')
        return

    log_event("agent_msg", "telegram-user", "telegram-bot", "status",
              input_summary="/status")

    try:
        resp = requests.get(f'{OLLAMA_URL}/api/tags', timeout=5)
        models = resp.json().get('models', [])
        model_lines = [f"  {m['name']} ({m.get('size', 0) // (1024**3)}GB)"
                       for m in models]
        ollama_status = f"Ollama: running\nModels ({len(models)}):\n" + '\n'.join(model_lines)
    except Exception as e:
        ollama_status = f"Ollama: ERROR - {e}"

    # Check ChromaDB
    try:
        import chromadb
        client = chromadb.PersistentClient(path=os.path.join(PROJECT_DIR, 'data', 'chromadb'))
        col = client.get_collection('kjtcom_archive')
        chroma_status = f"ChromaDB: {col.count()} chunks indexed"
    except Exception as e:
        chroma_status = f"ChromaDB: ERROR - {e}"

    # Check Brave
    brave_key = os.environ.get('KJTCOM_BRAVE_SEARCH_API_KEY')
    brave_status = "Brave Search: SET" if brave_key else "Brave Search: NOT SET"

    # Event log stats
    try:
        from analyze_events import load_events, analyze
        events = load_events()
        summary = analyze(events)
        event_status = (f"Event Log: {summary['total_events']} events, "
                        f"{summary['error_rate']}% error rate")
    except Exception:
        event_status = "Event Log: unavailable"

    msg = f"{ollama_status}\n\n{chroma_status}\n{brave_status}\n{event_status}"
    log_event("agent_msg", "telegram-bot", "telegram-user", "response",
              output_summary=msg[:200])
    await update.message.reply_text(msg)


async def cmd_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Describe a Firestore query."""
    if not check_auth(update):
        return
    query_text = ' '.join(context.args) if context.args else ''
    log_event("agent_msg", "telegram-user", "telegram-bot", "query",
              input_summary=f"/query {query_text}"[:200])
    if not query_text:
        await update.message.reply_text(
            'Usage: /query <description>\n'
            'Example: /query t_any_cuisines contains "french"'
        )
        return
    response_text = (f'Query: {query_text}\n\n'
                     f'Run this on kylejeromethompson.com or via Firebase MCP.')
    log_event("agent_msg", "telegram-bot", "telegram-user", "response",
              output_summary=response_text[:200])
    await update.message.reply_text(response_text)


async def cmd_evaluate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run Qwen evaluator against an iteration."""
    if not check_auth(update):
        return
    version = context.args[0] if context.args else 'v9.38'
    log_event("agent_msg", "telegram-user", "telegram-bot", "evaluate",
              input_summary=f"/evaluate {version}")
    await update.message.reply_text(f'Running Qwen evaluator for {version}...')

    try:
        prompt = f'/no_think Rate the kjtcom iteration {version} on a scale of 1-10 for: problem_analysis, code_correctness, efficiency, gotcha_avoidance, novel_contribution. Return JSON only.'
        start = time.time()
        eval_payload = merge_defaults({
            'model': 'qwen3.5:9b',
            'messages': [{'role': 'user', 'content': prompt}],
        }, evaluation=True)
        resp = requests.post(f'{OLLAMA_URL}/api/chat', json=eval_payload,
                             timeout=120)
        data = resp.json()
        content = data['message']['content']
        latency = int((time.time() - start) * 1000)
        log_event("llm_call", "telegram-bot", "qwen3.5:9b", "evaluate",
                  input_summary=prompt[:200], output_summary=content[:200],
                  tokens={"prompt": data.get('prompt_eval_count', 0),
                          "eval": data.get('eval_count', 0),
                          "total": data.get('prompt_eval_count', 0) + data.get('eval_count', 0)},
                  latency_ms=latency, status="success" if content.strip() else "empty_response")
        response_text = f'Qwen evaluation for {version}:\n\n{content[:2000]}'
        log_event("agent_msg", "telegram-bot", "telegram-user", "response",
                  output_summary=response_text[:200])
        await update.message.reply_text(response_text)
    except Exception as e:
        log_event("llm_call", "telegram-bot", "qwen3.5:9b", "evaluate",
                  input_summary=prompt[:200], status="error", error=str(e))
        await update.message.reply_text(f'Evaluator error: {e}')


async def cmd_gotcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List active gotchas from agent_scores.json."""
    if not check_auth(update):
        return
    log_event("agent_msg", "telegram-user", "telegram-bot", "gotcha",
              input_summary="/gotcha")
    try:
        scores_path = os.path.join(PROJECT_DIR, 'agent_scores.json')
        with open(scores_path) as f:
            scores = json.load(f)

        gotchas = []
        for entry in scores:
            for g in entry.get('gotcha_events', []):
                gotchas.append(f"{g['id']}: {g['description']}")

        if gotchas:
            msg = f"Active Gotchas ({len(gotchas)}):\n\n" + '\n'.join(gotchas[-10:])
        else:
            msg = "No gotcha events in recent scores."
        log_event("agent_msg", "telegram-bot", "telegram-user", "response",
                  output_summary=msg[:200])
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f'Error reading gotchas: {e}')


async def cmd_scores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show agent leaderboard."""
    if not check_auth(update):
        return
    log_event("agent_msg", "telegram-user", "telegram-bot", "scores",
              input_summary="/scores")
    try:
        scores_path = os.path.join(PROJECT_DIR, 'agent_scores.json')
        with open(scores_path) as f:
            scores = json.load(f)

        # Aggregate per agent
        agent_totals = {}
        for entry in scores:
            for s in entry.get('scores', []):
                name = s['agent']
                if name not in agent_totals:
                    agent_totals[name] = {'scores': [], 'iterations': 0}
                agent_totals[name]['scores'].append(s['total'])
                agent_totals[name]['iterations'] += 1

        lines = ['Agent Leaderboard:', '']
        for name, data in sorted(agent_totals.items(),
                                  key=lambda x: -max(x[1]['scores'])):
            avg = sum(data['scores']) / len(data['scores'])
            best = max(data['scores'])
            worst = min(data['scores'])
            lines.append(
                f"{name}: avg={avg:.1f}/50, best={best}, "
                f"worst={worst}, iterations={data['iterations']}"
            )

        response_text = '\n'.join(lines)
        log_event("agent_msg", "telegram-bot", "telegram-user", "response",
                  output_summary=response_text[:200])
        await update.message.reply_text(response_text)
    except Exception as e:
        await update.message.reply_text(f'Error: {e}')


async def cmd_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dual retrieval Q&A - routes to Firestore (entities) or ChromaDB (dev history)."""
    if not check_auth(update):
        return
    question = ' '.join(context.args) if context.args else ''
    if not question:
        await update.message.reply_text('Usage: /ask <question>')
        return

    user_id = update.effective_user.id
    log_event("agent_msg", "telegram-user", "telegram-bot", "ask",
              input_summary=f"/ask {question}"[:200])

    # Session memory: check for context references (v9.43)
    session = resolve_context(question, user_id)
    if session:
        await update.message.reply_text(f'Using previous context ({session["count"]} results)...')
        try:
            from litellm import completion as llm_completion
            # Build context from previous results for Gemini follow-up
            prev_results_text = ""
            for doc in session["results"][:50]:
                name = doc.get("t_any_names", ["Unknown"])[0] if doc.get("t_any_names") else doc.get("t_name", "Unknown")
                rating = ""
                enrichment = doc.get("t_enrichment", {})
                if isinstance(enrichment, dict):
                    gp = enrichment.get("google_places", {})
                    if isinstance(gp, dict) and gp.get("rating"):
                        rating = f" (rating: {gp['rating']}, reviews: {gp.get('user_ratings_total', 'N/A')})"
                city = doc.get("t_any_cities", [""])[0] if doc.get("t_any_cities") else ""
                state = doc.get("t_any_states", [""])[0] if doc.get("t_any_states") else ""
                loc = ", ".join(filter(None, [city, state]))
                prev_results_text += f"- {name}{' (' + loc + ')' if loc else ''}{rating}\n"

            synth_start = time.time()
            synth_resp = llm_completion(
                model="gemini/gemini-2.5-flash",
                messages=[{"role": "user", "content": (
                    f"Previous query returned {session['count']} results:\n\n"
                    f"{prev_results_text[:3000]}\n\n"
                    f"Now answer this follow-up question: {question}"
                )}],
                max_tokens=1024,
                thinking={"type": "disabled"},
            )
            synth_content = synth_resp.choices[0].message.content
            synth_latency = int((time.time() - synth_start) * 1000)
            log_event("llm_call", "telegram-bot", "gemini/gemini-2.5-flash", "session-followup",
                      input_summary=f"followup: {question}"[:200],
                      output_summary=synth_content[:200],
                      latency_ms=synth_latency, status="success")
            response_text = f"[Session Context -> Gemini]\n\n{synth_content[:2000]}"
        except Exception as e:
            log_event("llm_call", "telegram-bot", "gemini/gemini-2.5-flash", "session-followup",
                      input_summary=f"followup: {question}"[:200],
                      status="error", error=str(e))
            response_text = f"Session follow-up error: {e}"

        log_event("agent_msg", "telegram-bot", "telegram-user", "response",
                  output_summary=response_text[:200])
        await update.message.reply_text(response_text)
        return

    await update.message.reply_text(f'Routing: {question}...')

    try:
        # Stage 1: Intent routing via Gemini Flash
        routing = route_question(question)
        route = routing.get("route", "chromadb")

        log_event("agent_msg", "telegram-bot", "intent-router", "route",
                  input_summary=question[:200],
                  output_summary=f"route={route}, filters={routing.get('filters', {})}"[:200])

        if route == "web":
            # Stage 2c: Web search via Brave -> Gemini synthesis
            try:
                from brave_search import search as brave_search
                search_results = brave_search(routing.get("query", question), count=5)
                if 'error' in search_results:
                    response_text = f"Search error: {search_results['error']}"
                else:
                    # Format raw results
                    raw_lines = []
                    for r in search_results.get('results', []):
                        raw_lines.append(f"- {r['title']}\n  {r['url']}\n  {r['snippet'][:150]}")
                    raw_text = "\n".join(raw_lines)

                    # Synthesize with Gemini
                    try:
                        from litellm import completion as llm_completion
                        synth_start = time.time()
                        synth_resp = llm_completion(
                            model="gemini/gemini-2.5-flash",
                            messages=[{"role": "user", "content": (
                                f"Based on these web search results:\n\n{raw_text[:3000]}\n\n"
                                f"Answer this question concisely: {question}"
                            )}],
                            max_tokens=1024,
                            thinking={"type": "disabled"},
                        )
                        synth_content = synth_resp.choices[0].message.content
                        synth_latency = int((time.time() - synth_start) * 1000)
                        log_event("llm_call", "telegram-bot", "gemini/gemini-2.5-flash", "synthesize-web",
                                  input_summary=f"web synth: {question}"[:200],
                                  output_summary=synth_content[:200],
                                  latency_ms=synth_latency, status="success")
                        response_text = f"[Web -> Gemini]\n\n{synth_content[:2000]}"
                    except Exception:
                        response_text = f"[Web]\n\n{raw_text[:2000]}"

                log_event("api_call", "telegram-bot", "brave-search", "web-route",
                          input_summary=question[:200],
                          output_summary=response_text[:200],
                          status="success")
            except Exception as e:
                log_event("api_call", "telegram-bot", "brave-search", "web-route",
                          input_summary=question[:200],
                          status="error", error=str(e))
                response_text = f"Web search error: {e}"

        elif route == "firestore":
            # Stage 2a: Firestore entity query
            filters = routing.get("filters", {})
            intent = routing.get("intent", "list")
            sort_field = routing.get("sort")
            sort_order = routing.get("sort_order", "desc")
            limit = routing.get("limit")
            result, raw_docs = firestore_execute(filters, intent,
                                                   sort_field=sort_field,
                                                   sort_order=sort_order,
                                                   limit=limit,
                                                   return_docs=True)

            # Store session for follow-up queries (v9.43)
            if raw_docs:
                user_sessions[user_id] = {
                    "filters": filters,
                    "results": raw_docs,
                    "count": len(raw_docs),
                    "timestamp": time.time()
                }

            # Stage 3: Optional synthesis for non-count/list intents
            if intent not in ("count", "list") and result and not result.startswith("0 results"):
                try:
                    from litellm import completion as llm_completion
                    synth_start = time.time()
                    synth_resp = llm_completion(
                        model="gemini/gemini-2.5-flash",
                        messages=[{"role": "user", "content": (
                            f"Based on these Firestore query results:\n\n{result[:3000]}\n\n"
                            f"Answer this question naturally: {question}"
                        )}],
                        max_tokens=1024,
                        thinking={"type": "disabled"},
                    )
                    synth_content = synth_resp.choices[0].message.content
                    synth_latency = int((time.time() - synth_start) * 1000)
                    log_event("llm_call", "telegram-bot", "gemini/gemini-2.5-flash", "synthesize",
                              input_summary=f"synth: {question}"[:200],
                              output_summary=synth_content[:200],
                              latency_ms=synth_latency, status="success")
                    response_text = f"[Firestore -> Gemini]\n\n{synth_content[:2000]}"
                except Exception:
                    response_text = f"[Firestore]\n\n{result[:2000]}"
            else:
                response_text = f"[Firestore]\n\n{result[:2000]}"

        else:
            # Stage 2b: ChromaDB RAG retrieval (existing path)
            start = time.time()
            results = rag_query(question, n_results=3)
            chunks = []
            for i in range(len(results['ids'][0])):
                doc = results['documents'][0][i]
                meta = results['metadatas'][0][i]
                score = 1 - results['distances'][0][i]
                chunks.append(f"[{meta.get('filename', '?')} | {meta.get('version', '?')} | score={score:.3f}]\n{doc}")
            rag_latency = int((time.time() - start) * 1000)

            if not chunks:
                log_event("api_call", "telegram-bot", "chromadb", "query",
                          input_summary=question[:200], output_summary="0 chunks",
                          latency_ms=rag_latency, status="empty_response")
                await update.message.reply_text('No matching chunks found in archive.')
                return

            context_text = "\n\n---\n\n".join(chunks)
            log_event("api_call", "telegram-bot", "chromadb", "query",
                      input_summary=question[:200],
                      output_summary=f"{len(chunks)} chunks, {len(context_text)} chars",
                      latency_ms=rag_latency, status="success")

            # Synthesize with Gemini via litellm
            try:
                from litellm import completion as llm_completion
                synth_prompt = (
                    f"Based on this context from the kjtcom project archive:\n\n"
                    f"{context_text[:3000]}\n\n"
                    f"Answer this question concisely: {question}"
                )
                synth_start = time.time()
                synth_resp = llm_completion(
                    model="gemini/gemini-2.5-flash",
                    messages=[{"role": "user", "content": synth_prompt}],
                    max_tokens=1024,
                    thinking={"type": "disabled"},
                )
                synth_content = synth_resp.choices[0].message.content
                synth_latency = int((time.time() - synth_start) * 1000)
                log_event("llm_call", "telegram-bot", "gemini/gemini-2.5-flash", "ask",
                          input_summary=synth_prompt[:200], output_summary=synth_content[:200],
                          latency_ms=synth_latency, status="success")
                response_text = f'[ChromaDB -> Gemini]\n\n{synth_content[:2000]}'
            except Exception:
                response_text = f'[ChromaDB]\n\n{context_text[:2000]}'

        log_event("agent_msg", "telegram-bot", "telegram-user", "response",
                  output_summary=response_text[:200])
        await update.message.reply_text(response_text)
    except Exception as e:
        log_event("api_call", "telegram-bot", "dual-retrieval", "ask",
                  input_summary=question[:200], status="error", error=str(e))
        await update.message.reply_text(f'Error: {e}')


async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Brave Search API web search."""
    if not check_auth(update):
        return
    query_text = ' '.join(context.args) if context.args else ''
    log_event("agent_msg", "telegram-user", "telegram-bot", "search",
              input_summary=f"/search {query_text}"[:200])
    if not query_text:
        await update.message.reply_text('Usage: /search <query>')
        return

    try:
        start = time.time()
        result = subprocess.run(
            ['python3', os.path.join(PROJECT_DIR, 'scripts', 'brave_search.py'),
             query_text, '3'],
            capture_output=True, text=True, timeout=15,
            cwd=PROJECT_DIR
        )
        if result.returncode != 0:
            await update.message.reply_text(f'Search error: {result.stdout or result.stderr}')
            return

        data = json.loads(result.stdout)
        lines = [f"Search: {query_text}\n"]
        for r in data.get('results', []):
            lines.append(f"- {r['title']}\n  {r['url']}\n  {r['snippet'][:100]}")
        raw_results = '\n'.join(lines)

        # Try OpenClaw synthesis
        try:
            from interpreter import interpreter
            interpreter.llm.model = 'gemini/gemini-2.5-flash'
            interpreter.llm.api_key = os.environ.get('GEMINI_API_KEY', '')
            interpreter.auto_run = True
            synth_start = time.time()
            answer = interpreter.chat(f'Summarize these search results for: {query_text}\n\n{raw_results}')
            synth_content = answer[-1]['content'] if answer else raw_results
            log_event("llm_call", "telegram-bot", "gemini/gemini-2.5-flash", "chat",
                      input_summary=f"Summarize search: {query_text}"[:200],
                      output_summary=synth_content[:200],
                      latency_ms=int((time.time() - synth_start) * 1000), status="success")
            response_text = synth_content[:2000]
        except Exception:
            response_text = raw_results[:2000]
        log_event("agent_msg", "telegram-bot", "telegram-user", "response",
                  output_summary=response_text[:200])
        await update.message.reply_text(response_text)
    except Exception as e:
        log_event("api_call", "telegram-bot", "brave-search", "search",
                  input_summary=query_text[:200], status="error", error=str(e))
        await update.message.reply_text(f'Search error: {e}')


WELCOME_MSG = (
    "kjtcom IAO Bot\n\n"
    "Commands:\n"
    "/status - Ollama models, system health\n"
    "/query - Firestore query description\n"
    "/evaluate [version] - Run Qwen evaluator\n"
    "/gotcha - List active gotchas\n"
    "/scores - Agent leaderboard\n"
    "/ask [question] - RAG-powered Q&A\n"
    "/search [query] - Brave Search + Gemini summary\n"
    "/help - Show this message"
)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with command list."""
    log_event("agent_msg", "telegram-user", "telegram-bot", "start",
              input_summary="/start")
    log_event("agent_msg", "telegram-bot", "telegram-user", "response",
              output_summary=WELCOME_MSG[:200])
    await update.message.reply_text(WELCOME_MSG)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help message - same as /start."""
    log_event("agent_msg", "telegram-user", "telegram-bot", "help",
              input_summary="/help")
    log_event("agent_msg", "telegram-bot", "telegram-user", "response",
              output_summary=WELCOME_MSG[:200])
    await update.message.reply_text(WELCOME_MSG)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Default handler for non-command text messages."""
    if not check_auth(update):
        return
    text = update.message.text or ''
    log_event("agent_msg", "telegram-user", "telegram-bot", "text",
              input_summary=text[:200])
    response_text = "Unknown command. Try /status, /ask [question], or /help for all commands."
    log_event("agent_msg", "telegram-bot", "telegram-user", "response",
              output_summary=response_text)
    await update.message.reply_text(response_text)


async def watchdog_ping(context: ContextTypes.DEFAULT_TYPE):
    """Periodic watchdog ping for systemd WatchdogSec. Runs every 5 minutes."""
    sd_notifier.notify("WATCHDOG=1")
    logger.debug("Watchdog ping sent")


def main():
    if not KJTCOM_TELEGRAM_BOT_TOKEN:
        print('ERROR: KJTCOM_TELEGRAM_BOT_TOKEN not set in environment')
        print('Kyle: create bot via @BotFather, then:')
        print('  set -gx KJTCOM_TELEGRAM_BOT_TOKEN "your-token"')
        sys.exit(1)

    app = Application.builder().token(KJTCOM_TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', cmd_start))
    app.add_handler(CommandHandler('help', cmd_help))
    app.add_handler(CommandHandler('status', cmd_status))
    app.add_handler(CommandHandler('query', cmd_query))
    app.add_handler(CommandHandler('evaluate', cmd_evaluate))
    app.add_handler(CommandHandler('gotcha', cmd_gotcha))
    app.add_handler(CommandHandler('scores', cmd_scores))
    app.add_handler(CommandHandler('ask', cmd_ask))
    app.add_handler(CommandHandler('search', cmd_search))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # systemd watchdog: ping every 5 min (WatchdogSec=600 = 10 min)
    app.job_queue.run_repeating(watchdog_ping, interval=300, first=10)

    # Notify systemd we're ready
    sd_notifier.notify("READY=1")

    print('kjtcom IAO Bot starting...')
    print('Commands: /start /help /status /query /evaluate /gotcha /scores /ask /search')
    app.run_polling()


if __name__ == '__main__':
    main()
