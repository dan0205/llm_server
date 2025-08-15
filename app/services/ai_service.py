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

SYSTEM_PROMPT = """당신은 한국어 신조어/표현을 문맥에 맞게 '한 문장'으로만 설명합니다.
규칙:
- 출력은 JSON 한 줄만: {"meaning_line":"<단어>: <한 문장 의미>"}
- 예문, 해설, 추가텍스트 금지 (설명 1문장만)
- 문맥(context)이 주어지면 그 문맥에 '가장 자연스러운' 의미 1개를 택해 설명
- 모호하면 가장 일반적인 사용 의미 1개만 선택
- 최대 120자 내로 간결하게"""

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

# _coerce_schema 함수는 더 이상 사용하지 않음 (직접 처리로 대체)

async def interpret_with_llm(term: str, context_sentence: Optional[str] = None) -> Dict[str, Any]:
    # 런타임에 클라이언트 생성 (import 시점 고정 문제 해결)
    client = _get_client()
    if not client:
        print("[LLM ERROR] Cannot create OpenAI client - API key missing")
        return _fallback(term)
    
    user_prompt = (
        f"단어: {term}\n"
        f"문맥: {context_sentence or '(문맥 없음)'}\n"
        "위 규칙에 따라 JSON으로만 답하세요."
    )
    
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
                line = data.get("meaning_line", "").strip()
                if len(line) > 140: 
                    line = line[:140].rstrip()
                return {"meaning_line": line}
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
