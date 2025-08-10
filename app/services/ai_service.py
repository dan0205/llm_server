import asyncio
import json
from typing import Optional, Dict, Any
from openai import AsyncOpenAI, APIConnectionError, RateLimitError
from app.core.config import settings

# import 시점 고정 문제 제거 - 런타임에 클라이언트 생성
def _get_client():
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        print("[LLM ERROR] OPENAI_API_KEY is empty")
        return None
    
    # 키 프리픽스 로깅 (보안을 위해 앞 8자만)
    key_prefix = api_key[:8] + "..." if len(api_key) > 8 else api_key
    print(f"[LLM] Using API key: {key_prefix}")
    
    return AsyncOpenAI(api_key=api_key)

SYSTEM_PROMPT = """다음 단어의 의미를 한 문장으로만 설명하세요.  
예문, 부연 설명, 분석은 포함하지 마세요.  
출력은 JSON 형식으로만 반환하세요.

출력 형식:
{"meaning_line": "<단어>: <한 문장 의미>"}"""

def _fallback(term: str) -> Dict[str, Any]:
    return {
        "meaning_line": f"{term}: 정확한 해석을 찾지 못했습니다."
    }

# 보정 유틸 추가/교체
def _as_str(x):
    return x if isinstance(x, str) else ("" if x is None else str(x))

def _as_str_list(x):
    if isinstance(x, list):
        return [v if isinstance(v, str) else str(v) for v in x]
    if isinstance(x, str):
        return [s.strip() for s in x.split(",") if s.strip()]
    return []

def _coerce_schema(term: str, data: Dict[str, Any]) -> Dict[str, Any]:
    data = data or {}
    
    # meaning_line이 없으면 fallback
    if not data.get("meaning_line"):
        return _fallback(term)
    
    # 과도한 길이 방지
    if len(data["meaning_line"]) > 200:
        data["meaning_line"] = data["meaning_line"][:200] + "..."
    
    return data

async def interpret_with_llm(term: str, context_sentence: Optional[str] = None) -> Dict[str, Any]:
    # 런타임에 클라이언트 생성 (import 시점 고정 문제 해결)
    client = _get_client()
    if not client:
        print("[LLM ERROR] Cannot create OpenAI client - API key missing")
        return _fallback(term)
    
    user_prompt = f"신조어: {term}\n문맥: {context_sentence or ''}".strip()
    
    async def _once():
        try:
            print(f"[LLM] Calling OpenAI for term: {term}")
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
                timeout=20,
            )
            
            content = resp.choices[0].message.content
            print(f"[LLM] Raw response: {content[:200]}...")
            
            try:
                data = json.loads(content)
                print(f"[LLM] JSON parsed successfully")
                return _coerce_schema(term, data)
            except json.JSONDecodeError as e:
                print(f"[LLM ERROR] JSON parse failed: {e}")
                print(f"[LLM ERROR] Raw content: {content}")
                return _fallback(term)
                
        except APIConnectionError as e:
            print(f"[LLM ERROR] API connection failed: {e}")
            raise
        except RateLimitError as e:
            print(f"[LLM ERROR] Rate limit exceeded: {e}")
            raise
        except Exception as e:
            print(f"[LLM ERROR] Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    # 간단 재시도(네트워크/레이트리밋)
    for i in range(3):
        try:
            return await asyncio.wait_for(_once(), timeout=25)
        except (APIConnectionError, RateLimitError, TimeoutError, asyncio.TimeoutError) as e:
            print(f"[LLM ERROR] Attempt {i+1} failed: {e}")
            if i == 2:
                print(f"[LLM ERROR] All retries failed, returning fallback")
                return _fallback(term)
            await asyncio.sleep(0.8 * (i+1))
        except Exception as e:
            print(f"[LLM ERROR] Non-retryable error: {e}")
            return _fallback(term)
