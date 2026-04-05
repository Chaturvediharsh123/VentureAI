from openai import OpenAI

GROK_BASE_URL = "https://api.x.ai/v1"
GROK_MODEL = "grok-3"

def run_tech_agent(idea: str, strategy_output: str, api_key: str):
    client = OpenAI(api_key=api_key, base_url=GROK_BASE_URL)
    prompt = f"""You are a Senior Software Architect and CTO. Design a complete technical blueprint for:

**Business Idea:** "{idea}"

**Business Strategy:**
{strategy_output[:1000]}

## 🏛️ System Architecture
High-level architecture with a text-based diagram.

## 🛠️ Recommended Tech Stack
| Layer | Technology | Why |
Frontend, Backend, Database, Mobile, Cloud, DevOps, AI/ML, Payments, Auth.

## 📱 MVP Feature List
8-10 must-have features. Mark: 🔴 Critical, 🟡 Important, 🟢 Nice-to-have.

## 🗺️ Development Roadmap
- **Phase 1 - MVP (0-3 months)**
- **Phase 2 - Growth (3-8 months)**
- **Phase 3 - Scale (8-18 months)**

## 👥 Team Requirements
Technical roles needed.

## 🔒 Security & Compliance
Key security measures and compliance requirements.

## ⚡ Scalability Plan
How to handle 10x, 100x user growth.

Use real technology names and be precise."""

    stream = client.chat.completions.create(
        model=GROK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text
