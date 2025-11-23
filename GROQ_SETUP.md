# Quick Setup with Groq (RECOMMENDED)

## Why Groq?
- ✅ **30 requests/minute** (vs Gemini's 60/min but MUCH faster)
- ✅ **14,400 requests/day** - plenty for development
- ✅ **Faster responses** - <1 second vs 5-10 seconds
- ✅ **Free forever** - no credit card needed
- ✅ **Better for agents** - designed for high-throughput

## Setup Steps

### 1. Get Groq API Key (2 minutes)
1. Go to https://console.groq.com/
2. Click "Sign Up" (free, no credit card)
3. Go to "API Keys" in left menu
4. Click "Create API Key"
5. Copy your key

### 2. Install Groq SDK
```bash
pip install groq
```

### 3. Update Environment
Create/edit `.env` file:
```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama-3.1-70b-versatile
API_SECRET_KEY=my_random_secret_123
```

### 4. Test It
```bash
python test_agents.py
```

## Model Options (Groq)

**Recommended:**
- `llama-3.1-70b-versatile` - Best overall (use this)

**Alternatives:**
- `llama-3.1-8b-instant` - Fastest (for simple tasks)
- `mixtral-8x7b-32768` - Longer context window

## Comparison: Groq vs Gemini

| Feature | Groq | Gemini Free |
|---------|------|-------------|
| Speed | ⚡ <1 sec | 🐌 5-10 sec |
| Rate Limit | 30/min | 60/min |
| Daily Limit | 14,400 | 1,500 |
| Quality | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Best For | Agents | General use |

**Verdict**: Groq is **much better** for our multi-agent system!

## Already Have Gemini Key?

No problem! The system supports both. Just set:
```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_gemini_key
```

## Switching Between Providers

Just change `LLM_PROVIDER` in `.env`:
- `groq` - Use Groq (recommended)
- `gemini` - Use Google Gemini
- `together` - Use Together AI

No code changes needed!
