import os
import json
from flask import Flask, request, Response, send_from_directory
from dotenv import load_dotenv

from agents.research_agent import run_research_agent
from agents.strategy_agent import run_strategy_agent
from agents.finance_agent import run_finance_agent
from agents.tech_agent import run_tech_agent
from agents.marketing_agent import run_marketing_agent
from agents.presentation_agent import run_presentation_agent

load_dotenv()

app = Flask(__name__, static_folder="public")

# ─── Serve static frontend ─────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("public", "index.html")

# ─── Expose env API key to frontend (never logs it) ───────────────────────
@app.route("/api/config")
def config():
    return {"apiKey": os.getenv("GROK_API_KEY", "")}

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("public", path)

# ─── SSE helper ────────────────────────────────────────────────────────────
def sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

def sse_chunk(agent: str, text: str) -> str:
    return f"event: chunk\ndata: {json.dumps({'agent': agent, 'text': text})}\n\n"

# ─── Main generate endpoint ────────────────────────────────────────────────
@app.route("/api/generate", methods=["POST"])
def generate():
    body = request.get_json()
    idea = (body or {}).get("idea", "").strip()
    api_key = (body or {}).get("apiKey", "").strip()
    base_url = (body or {}).get("baseUrl", "").strip()
    model = (body or {}).get("model", "").strip()

    if not idea or not api_key or not base_url or not model:
        return {"error": "Idea, API key, Base URL, and Model are required."}, 400

    def stream():
        outputs = {}
        try:
            # ── Agent 1: Research ──────────────────────────────────────────
            yield sse_event("agentStart", {"agent": "research", "label": "Research Agent"})
            research_text = ""
            for chunk in run_research_agent(idea, api_key, base_url, model):
                research_text += chunk
                yield sse_chunk("research", chunk)
            outputs["research"] = research_text
            yield sse_event("agentDone", {"agent": "research"})

            # ── Agent 2: Strategy ─────────────────────────────────────────
            yield sse_event("agentStart", {"agent": "strategy", "label": "Business Strategy Agent"})
            strategy_text = ""
            for chunk in run_strategy_agent(idea, research_text, api_key, base_url, model):
                strategy_text += chunk
                yield sse_chunk("strategy", chunk)
            outputs["strategy"] = strategy_text
            yield sse_event("agentDone", {"agent": "strategy"})

            # ── Agent 3: Finance ──────────────────────────────────────────
            yield sse_event("agentStart", {"agent": "finance", "label": "Finance Agent"})
            finance_text = ""
            for chunk in run_finance_agent(idea, strategy_text, api_key, base_url, model):
                finance_text += chunk
                yield sse_chunk("finance", chunk)
            outputs["finance"] = finance_text
            yield sse_event("agentDone", {"agent": "finance"})

            # ── Agent 4: Tech ─────────────────────────────────────────────
            yield sse_event("agentStart", {"agent": "tech", "label": "Tech Agent"})
            tech_text = ""
            for chunk in run_tech_agent(idea, strategy_text, api_key, base_url, model):
                tech_text += chunk
                yield sse_chunk("tech", chunk)
            outputs["tech"] = tech_text
            yield sse_event("agentDone", {"agent": "tech"})

            # ── Agent 5: Marketing ────────────────────────────────────────
            yield sse_event("agentStart", {"agent": "marketing", "label": "Marketing Agent"})
            marketing_text = ""
            for chunk in run_marketing_agent(idea, research_text, strategy_text, api_key, base_url, model):
                marketing_text += chunk
                yield sse_chunk("marketing", chunk)
            outputs["marketing"] = marketing_text
            yield sse_event("agentDone", {"agent": "marketing"})

            # ── Agent 6: Presentation ─────────────────────────────────────
            yield sse_event("agentStart", {"agent": "presentation", "label": "Presentation Agent"})
            all_context = "\n\n---\n\n".join([
                research_text, strategy_text, finance_text, tech_text, marketing_text
            ])
            presentation_text = ""
            for chunk in run_presentation_agent(idea, all_context, api_key, base_url, model):
                presentation_text += chunk
                yield sse_chunk("presentation", chunk)
            outputs["presentation"] = presentation_text
            yield sse_event("agentDone", {"agent": "presentation"})

            # ── Complete ──────────────────────────────────────────────────
            yield sse_event("complete", outputs)

        except Exception as e:
            print(f"[Agent Error] {e}")
            yield sse_event("error", {"message": str(e)})

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )

if __name__ == "__main__":
    print("\n🚀 AI Business Builder running at http://localhost:3001\n")
    app.run(host="0.0.0.0", port=3001, debug=False, threaded=True)
