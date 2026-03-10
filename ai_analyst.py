import os
import json
import time
import requests
from groq import Groq
import google.generativeai as genai

# Setup API Clients
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

SYSTEM_PROMPT = """
You are a senior equity research analyst for Indian markets.
You have access to technical indicators, recent news, and 
memory of your past analysis on this stock.

IMPORTANT RULES:
- You NEVER change the technical score — that is computed 
  separately and is not your job
- You NEVER decide which stocks to include — that is the 
  user's decision via config.json
- Your ONLY job is to add reasoning and context to the 
  scores already computed
- Be specific to Indian markets — mention SEBI, RBI, NSE, 
  FII/DII flows where relevant
- Be direct and actionable — no vague statements

Always respond in this EXACT JSON format, nothing else:
{
  "verdict": "BUY or SELL or HOLD or WATCH",
  "confidence": "HIGH or MEDIUM or LOW",
  "agrees_with_signal": true or false,
  "one_liner": "max 12 words, specific and actionable",
  "reasoning": "2-3 sentences. Mention the 2 most important 
                factors. Reference news if relevant.",
  "key_risk": "Single biggest risk, one sentence",
  "key_catalyst": "Single biggest upside trigger, one sentence",
  "news_impact": "POSITIVE or NEGATIVE or NEUTRAL",
  "time_horizon": "SHORT (1-3 days) or MEDIUM (1-3 weeks) 
                   or LONG (1-3 months)",
  "memory_note": "One sentence referencing past history 
                  if available, else null"
}
"""

def analyze_stock(stock_data: dict, news: dict, memory_history: list, streak: dict, trend_change: dict) -> dict:
    # 1. Prepare User Data
    user_msg = f"""
    Analyze {stock_data['ticker']} ({stock_data.get('name', 'N/A')}).
    Sector: {stock_data.get('sector', 'N/A')}
    
    PRICE DATA:
    - Current: ₹{stock_data['price']}
    - 1D Change: {stock_data['change_1d']}%
    
    COMPUTED SIGNAL:
    - Composite Score: {stock_data['composite_score']}/100
    - Signal: {stock_data['signal']}
    
    TECHNICALS:
    - RSI: {stock_data['key_indicators']['rsi']} ({'Oversold' if stock_data['key_indicators']['rsi'] < 30 else 'Overbought' if stock_data['key_indicators']['rsi'] > 70 else 'Neutral'})
    - MACD crossover: {stock_data['key_indicators'].get('macd_crossover', 'N/A')}
    - SuperTrend: {stock_data['key_indicators'].get('supertrend', 'N/A')}
    - Volume Ratio: {stock_data['key_indicators'].get('volume_ratio', 'N/A')}
    - OBV trend: {stock_data['key_indicators'].get('obv_trend', 'N/A')}
    - Trend Strength (ADX): {stock_data['key_indicators'].get('adx', 'N/A')} ({stock_data['key_indicators'].get('trend_strength', 'N/A')})
    - Price vs 50 DMA: {stock_data['key_indicators'].get('price_vs_sma50', 'N/A')}%
    - Price vs 200 DMA: {stock_data['key_indicators'].get('price_vs_sma200', 'N/A')}%

    RECENT NEWS:
    {json.dumps(news.get('headlines', [])[:5], indent=2)}
    Sentiment: {json.dumps(news.get('sentiment_keywords', {}), indent=2)}

    MEMORY & PATTERN:
    - Streak: {streak.get('message', 'N/A')}
    - Trend Change: {trend_change.get('message', 'N/A')}
    - Past 5 verdicts: {[h.get('ai_verdict') for h in memory_history[-5:]]}
    """
    
    # 2. Try Groq
    ai_result = _try_groq(user_msg)
    
    # 3. Try Gemini Fallback
    if not ai_result:
        ai_result = _try_gemini(user_msg)
        
    # 4. Final Fallback (Safe default)
    if not ai_result:
        ai_result = {
            "verdict": "HOLD",
            "confidence": "LOW",
            "agrees_with_signal": True,
            "one_liner": "Fallback: Manual review needed (AI unavailable)",
            "reasoning": "Both AI models (Groq, Gemini) were unavailable or hit rate limits.",
            "key_risk": "Technical failure / No connection to AI",
            "key_catalyst": "Resolution of connectivity",
            "news_impact": "NEUTRAL",
            "time_horizon": "SHORT (1-3 days)",
            "memory_note": None
        }
        
    time.sleep(0.8) # Respect rate limits
    return ai_result

def _try_groq(prompt):
    if not GROQ_API_KEY: return None
    try:
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"✗ Groq failed: {e}")
        return None

def _try_gemini(prompt):
    if not GEMINI_API_KEY: return None
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-3.0-flash', 
            generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\nUSER DATA:\n{prompt}")
        return json.loads(response.text)
    except Exception as e:
        print(f"✗ Gemini failed: {e}")
        return None
