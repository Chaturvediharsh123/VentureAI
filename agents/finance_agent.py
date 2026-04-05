from openai import OpenAI

GROK_BASE_URL = "https://api.x.ai/v1"
GROK_MODEL = "grok-3"

def run_finance_agent(idea: str, strategy_output: str, api_key: str):
    client = OpenAI(api_key=api_key, base_url=GROK_BASE_URL)
    prompt = f"""You are a CFO and financial modeling expert. Create detailed financial projections for:

**Business Idea:** "{idea}"

**Strategy Summary:**
{strategy_output[:1200]}

## 💸 Startup Costs (One-Time)
List all initial costs in USD. Show a total.

## 🔥 Monthly Burn Rate
Break down monthly operational expenses for Year 1 with total.

## 📊 Revenue Projections
| Month | Customers | MRR | ARR |
Show projections for Month 1, 3, 6, 12, 24, 36.

## ⚖️ Break-Even Analysis
When does the business break even? Customer count needed?

## 📈 3-Year P&L Summary
| Year | Revenue | Expenses | Net Profit | Margin |

## 💼 Funding Requirements
How much funding needed? Bootstrapped/Seed/Series A stages.

## 🎯 ROI Estimate
Expected ROI at end of Year 3 for an early investor.

Use realistic, conservative estimates with $ and % signs."""

    stream = client.chat.completions.create(
        model=GROK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text
