# Free LLM Options for JobHunter AI

## Best Free Alternatives to Gemini

### 1. **Groq (RECOMMENDED)** ⭐
- **Model**: Llama 3.1 70B / Mixtral 8x7B
- **Free Tier**: 
  - 30 requests/minute
  - 14,400 requests/day
  - **Much faster than Gemini** (inference speed)
- **Get API Key**: https://console.groq.com/
- **Why Better**: 
  - Higher rate limits
  - Faster responses
  - Better for agentic workflows

### 2. **Together AI**
- **Model**: Llama 3.1 70B, Mixtral, etc.
- **Free Tier**: $25 free credits
- **Get API Key**: https://api.together.xyz/
- **Why Good**: Multiple model options

### 3. **Hugging Face Inference API**
- **Models**: Many open-source models
- **Free Tier**: Limited but decent
- **Get API Key**: https://huggingface.co/settings/tokens
- **Why Good**: Access to many models

### 4. **OpenRouter**
- **Models**: Access to multiple providers
- **Free Tier**: Some free models available
- **Get API Key**: https://openrouter.ai/
- **Why Good**: One API for many models

## Comparison

| Provider | Rate Limit | Speed | Quality | Best For |
|----------|-----------|-------|---------|----------|
| Gemini Free | 60/min | Slow | Good | Small projects |
| **Groq** | 30/min | **Very Fast** | Good | **Agentic systems** |
| Together AI | Credits | Fast | Good | Production |
| HuggingFace | Limited | Medium | Varies | Experimentation |

## Recommendation: Switch to Groq

**Why Groq is best for JobHunter AI:**
1. ✅ **30 req/min** vs Gemini's 60/min (but much faster)
2. ✅ **14,400 req/day** - plenty for development
3. ✅ **Faster inference** - responses in <1 second
4. ✅ **Free forever** - no credit card needed
5. ✅ **Better for agents** - designed for high-throughput

## How to Switch to Groq

### Step 1: Get Groq API Key
1. Go to https://console.groq.com/
2. Sign up (free, no credit card)
3. Go to API Keys
4. Create new key

### Step 2: Update .env
```env
# Replace Gemini with Groq
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-70b-versatile
```

### Step 3: I'll update the code to support Groq

## Model Recommendations

**For Groq:**
- `llama-3.1-70b-versatile` - Best overall (RECOMMENDED)
- `mixtral-8x7b-32768` - Longer context
- `llama-3.1-8b-instant` - Fastest (for simple tasks)

**For Together AI:**
- `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo`
- `mistralai/Mixtral-8x7B-Instruct-v0.1`

## Cost Comparison (if you go paid later)

| Provider | Cost per 1M tokens |
|----------|-------------------|
| Gemini | $0.075 (input) |
| Groq | $0.59 (input) |
| Together AI | $0.88 (input) |
| OpenAI GPT-4 | $30 (input) |

**Note**: Groq is more expensive if paid, but free tier is better for development.

## My Recommendation

**Switch to Groq** - It's specifically designed for agentic workflows and has:
- Better rate limits for development
- Much faster responses (important for multi-agent systems)
- Free forever
- Easy to switch back to Gemini later if needed

Want me to update the code to support Groq?
