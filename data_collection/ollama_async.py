import aiohttp

async def chat(session, model, prompt, options=None):
    url = 'http://localhost:11434/api/chat'
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    if options:
        payload["options"] = options
    async with session.post(url, json=payload) as resp:
        return await resp.json()
