from openai import OpenAI


def run_strategy_agent(idea: str, research_output: str, api_key: str, base_url: str, model_name: str):
    client = OpenAI(api_key=api_key, base_url=base_url)
    prompt = f"""You are a seasoned Business Strategy Consultant (ex-McKinsey). Create a comprehensive business strategy for:

**Business Idea:** "{idea}"

**Market Research Summary:**
{research_output[:1500]}

## 🏗️ Business Model Canvas
Value Propositions, Customer Segments, Channels, Revenue Streams, Key Resources, Key Activities, Key Partners, Cost Structure.

## 💎 Value Proposition
One-line pitch and 3 supporting pillars.

## 💰 Pricing Strategy
2-3 pricing tiers with names, price points, and inclusions.

## 🌊 Revenue Streams
All revenue streams with estimated % contribution.

## 📐 Go-To-Market Strategy
Phase 1 (0-3 months), Phase 2 (3-12 months), Phase 3 (Year 2+).

## 🔑 Success Metrics (KPIs)
5 critical KPIs to track business health.

Be strategic, concrete, and use emojis."""

    stream = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text
