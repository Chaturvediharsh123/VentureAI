import glob
import re

for path in glob.glob('agents/*_agent.py'):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove the constants completely
    content = re.sub(r'GROK_BASE_URL.*?=.*\n', '', content)
    content = re.sub(r'GROK_MODEL.*?=.*\n', '', content)

    # 1. research_agent (idea, api_key) -> (idea, api_key, base_url, model_name)
    content = content.replace('def run_research_agent(idea: str, api_key: str):',
                              'def run_research_agent(idea: str, api_key: str, base_url: str, model_name: str):')
                              
    # 2. strategy, finance, tech, presentation (idea, context, api_key)
    content = re.sub(r'def run_(strategy_agent|finance_agent|tech_agent|presentation_agent)\((.*?),\s*api_key:\s*str\):',
                     r'def run_\1(\2, api_key: str, base_url: str, model_name: str):', content)
                     
    # 3. marketing agent (idea, rs, str, api_key)
    content = content.replace('def run_marketing_agent(idea: str, research_output: str, strategy_output: str, api_key: str):',
                              'def run_marketing_agent(idea: str, research_output: str, strategy_output: str, api_key: str, base_url: str, model_name: str):')

    # Replace the instantiation and calls
    content = content.replace('def make_client(api_key: str) -> OpenAI:\n    return OpenAI(api_key=api_key, base_url=base_url)', '')
    content = content.replace('client = make_client(api_key, base_url)', 'client = OpenAI(api_key=api_key, base_url=base_url)')
    content = content.replace('client = make_client(api_key)', 'client = OpenAI(api_key=api_key, base_url=base_url)')
    content = content.replace('OpenAI(api_key=api_key, base_url=GROK_BASE_URL)', 'OpenAI(api_key=api_key, base_url=base_url)')
    content = content.replace('model=GROK_MODEL,', 'model=model_name,')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Updated all agents")
