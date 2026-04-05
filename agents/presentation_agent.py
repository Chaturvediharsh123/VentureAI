from openai import OpenAI


def run_presentation_agent(idea: str, all_outputs: str, api_key: str, base_url: str, model_name: str):
    client = OpenAI(api_key=api_key, base_url=base_url)
    prompt = f"""You are a world-class startup pitch deck writer (Y Combinator, Sequoia). Create a 10-slide pitch deck for:

**Business Idea:** "{idea}"

**Context:**
{all_outputs[:2000]}

Return ONLY a valid JSON array (no markdown fences, no extra text) with exactly 10 slide objects. Each object must have:
- "slideNumber": number (1-10)
- "title": string
- "emoji": string (one emoji)
- "subtitle": string (one compelling sub-headline)
- "bullets": array of 3-5 strings
- "highlight": string (one bold stat, e.g. "$50B Market")
- "speakerNote": string (1-2 sentences)

The 10 slides:
1. Cover / Title Slide
2. The Problem
3. The Solution
4. Market Opportunity
5. Business Model
6. Traction / Validation
7. Go-To-Market Strategy
8. Financial Projections
9. The Team
10. Ask / Investment Opportunity

Return ONLY the JSON array."""

    stream = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text
