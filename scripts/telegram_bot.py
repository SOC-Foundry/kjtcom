#!/usr/bin/env python3
"""kjtcom IAO Telegram Bot - routes commands to kjtcom agents and middleware.

Commands:
    /status  - Ollama model status, system health
    /query   - Firestore query description (informational)
    /evaluate [version] - Run Qwen evaluator against an iteration
    /gotcha  - List active gotchas
    /scores  - Agent leaderboard
    /ask [question] - RAG-powered Q&A over archive
    /search [query] - Brave Search API web search

Requires: KJTCOM_TELEGRAM_BOT_TOKEN environment variable
Security: Bot restricted to authorized user IDs only
"""
import os
import sys
import json
import logging
import subprocess
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Config
KJTCOM_TELEGRAM_BOT_TOKEN = os.environ.get('KJTCOM_TELEGRAM_BOT_TOKEN')
OLLAMA_URL = 'http://localhost:11434'
AUTHORIZED_USERS = set()  # Empty = allow all. Add Telegram user IDs to restrict.
PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

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
    brave_key = os.environ.get('BRAVE_SEARCH_API_KEY')
    brave_status = "Brave Search: SET" if brave_key else "Brave Search: NOT SET"

    msg = f"{ollama_status}\n\n{chroma_status}\n{brave_status}"
    await update.message.reply_text(msg)


async def cmd_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Describe a Firestore query."""
    if not check_auth(update):
        return
    query_text = ' '.join(context.args) if context.args else ''
    if not query_text:
        await update.message.reply_text(
            'Usage: /query <description>\n'
            'Example: /query t_any_cuisines contains "french"'
        )
        return
    await update.message.reply_text(
        f'Query: {query_text}\n\n'
        f'Run this on kylejeromethompson.com or via Firebase MCP.'
    )


async def cmd_evaluate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run Qwen evaluator against an iteration."""
    if not check_auth(update):
        return
    version = context.args[0] if context.args else 'v9.38'
    await update.message.reply_text(f'Running Qwen evaluator for {version}...')

    try:
        prompt = f'/no_think Rate the kjtcom iteration {version} on a scale of 1-10 for: problem_analysis, code_correctness, efficiency, gotcha_avoidance, novel_contribution. Return JSON only.'
        resp = requests.post(f'{OLLAMA_URL}/api/chat', json={
            'model': 'qwen3.5:9b',
            'messages': [{'role': 'user', 'content': prompt}],
            'stream': False,
            'options': {'num_predict': 512}
        }, timeout=120)
        content = resp.json()['message']['content']
        await update.message.reply_text(f'Qwen evaluation for {version}:\n\n{content[:2000]}')
    except Exception as e:
        await update.message.reply_text(f'Evaluator error: {e}')


async def cmd_gotcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List active gotchas from agent_scores.json."""
    if not check_auth(update):
        return
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
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f'Error reading gotchas: {e}')


async def cmd_scores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show agent leaderboard."""
    if not check_auth(update):
        return
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

        await update.message.reply_text('\n'.join(lines))
    except Exception as e:
        await update.message.reply_text(f'Error: {e}')


async def cmd_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """RAG-powered Q&A over archive."""
    if not check_auth(update):
        return
    question = ' '.join(context.args) if context.args else ''
    if not question:
        await update.message.reply_text('Usage: /ask <question>')
        return

    await update.message.reply_text(f'Searching archive for: {question}...')

    try:
        result = subprocess.run(
            ['python3', os.path.join(PROJECT_DIR, 'scripts', 'query_rag.py'),
             question, '3'],
            capture_output=True, text=True, timeout=30,
            cwd=PROJECT_DIR
        )
        output = result.stdout[:2000] if result.stdout else 'No results found.'
        await update.message.reply_text(f'RAG Results:\n\n{output}')
    except Exception as e:
        await update.message.reply_text(f'RAG error: {e}')


async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Brave Search API web search."""
    if not check_auth(update):
        return
    query_text = ' '.join(context.args) if context.args else ''
    if not query_text:
        await update.message.reply_text('Usage: /search <query>')
        return

    try:
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

        await update.message.reply_text('\n'.join(lines)[:2000])
    except Exception as e:
        await update.message.reply_text(f'Search error: {e}')


def main():
    if not KJTCOM_TELEGRAM_BOT_TOKEN:
        print('ERROR: KJTCOM_TELEGRAM_BOT_TOKEN not set in environment')
        print('Kyle: create bot via @BotFather, then:')
        print('  set -gx KJTCOM_TELEGRAM_BOT_TOKEN "your-token"')
        sys.exit(1)

    app = Application.builder().token(KJTCOM_TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler('status', cmd_status))
    app.add_handler(CommandHandler('query', cmd_query))
    app.add_handler(CommandHandler('evaluate', cmd_evaluate))
    app.add_handler(CommandHandler('gotcha', cmd_gotcha))
    app.add_handler(CommandHandler('scores', cmd_scores))
    app.add_handler(CommandHandler('ask', cmd_ask))
    app.add_handler(CommandHandler('search', cmd_search))

    print('kjtcom IAO Bot starting...')
    print('Commands: /status /query /evaluate /gotcha /scores /ask /search')
    app.run_polling()


if __name__ == '__main__':
    main()
