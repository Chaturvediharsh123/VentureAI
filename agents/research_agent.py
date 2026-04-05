from openai import OpenAI


def make_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key, base_url=base_url)

def run_research_agent(idea: str, api_key: str, base_url: str, model_name: str):
    client = OpenAI(api_key=api_key, base_url=base_url)
    prompt = f"""You are a world-class Market Research Analyst. Conduct a comprehensive market research report for:

"{idea}"

## 🌍 Market Overview
Describe the overall market landscape, size (TAM/SAM/SOM), and maturity.

## 🎯 Target Audience
Define primary and secondary customer segments with demographics and psychographics.

## 😣 Key Pain Points
List the top 5 problems customers face that this business solves.

## 📈 Industry Trends
Identify 5 major trends shaping this industry in 2024-2026.

## 🏆 Competitive Landscape
Name 3-5 key competitors, their strengths/weaknesses, and market gaps.

## 💡 Opportunity Assessment
Summarize the biggest opportunity and why NOW is the right time.

Be specific, data-driven, and actionable. Use emojis for visual appeal."""

    stream = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text
