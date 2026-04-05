from openai import OpenAI


def run_marketing_agent(idea: str, research_output: str, strategy_output: str, api_key: str, base_url: str, model_name: str):
    client = OpenAI(api_key=api_key, base_url=base_url)
    prompt = f"""You are a Chief Marketing Officer. Create a complete marketing plan for:

**Business Idea:** "{idea}"

**Market Research:**
{research_output[:800]}

**Strategy:**
{strategy_output[:600]}

## 🎯 Brand Identity
- Brand Name suggestion, Voice/Personality (3 adjectives), Tagline, Color palette.

## 📣 Marketing Channels Strategy
For each: audience, content type, frequency, expected ROI:
1. 📸 Instagram / TikTok
2. 🔍 SEO / Content Marketing
3. 📧 Email Marketing
4. 💰 Paid Ads (Google/Meta)
5. 🤝 Partnerships / Influencers
6. 📱 WhatsApp / Community

## 🚀 30-Day Launch Campaign
Weekly milestones for the first month.

## 📈 Growth Hacking Tactics
5 creative, low-cost growth hacks.

## 🎁 Customer Retention Strategy
Loyalty programs, referral schemes, re-engagement.

## 📊 Marketing KPIs & Budget
Monthly budget recommendation + key metrics (CAC, LTV, CTR)."""

    stream = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text
