import json
import hashlib
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import redis
from app.services.ai_service import interpret_with_llm

# 캐시 설정
CACHE_TTL_SEC = 3600 * 24 * 7  # 7일
CACHE_NS = "jargon:v2"  # ← 기존 "jargon:"에서 v2로 올려 과거 실패 캐시 무시

def _cache_key(term: str, context_sentence: Optional[str]) -> str:
    ctx = (context_sentence or "").strip()
    ctx_hash = hashlib.md5(ctx.encode("utf-8")).hexdigest()[:8] if ctx else "noctx"
    return f"{CACHE_NS}:{term}:{ctx_hash}"

# 외부 디버그에서 쓰기 좋게 보조 함수 노출
def cache_key_for(term: str, context_sentence: Optional[str]) -> str:
    return _cache_key(term, context_sentence)

def _is_fallback_line(meaning_line: str) -> bool:
    if not isinstance(meaning_line, str):
        return True
    s = meaning_line.strip()
    return (s == "") or ("정확한 해석을 찾지 못했습니다" in s) or s.endswith(":")  # 내용 비어있거나 실패 문구

async def _safe_get(rds, key):
    try:
        return await rds.get(key)
    except Exception as e:
        print(f"[CACHE OFF][GET] {key} -> {e}")
        return None

async def _safe_set(rds, key, val, ex):
    try:
        await rds.set(key, val, ex)
    except Exception as e:
        print(f"[CACHE OFF][SET] {key} -> {e}")

async def get_interpretation(
    term: str,
    db: AsyncSession,
    rds: redis.Redis,
    context_sentence: Optional[str],
    *,
    nocache: bool = False,
    refresh: bool = False,
) -> Dict[str, Any]:
    key = _cache_key(term, context_sentence)

    if not nocache and not refresh:
        cached = await _safe_get(rds, key)
        if cached:
            try:
                obj = json.loads(cached)
            except Exception:
                obj = {"meaning_line": str(cached)}
            line = obj.get("meaning_line", obj.get("meaning", ""))
            if _is_fallback_line(line):
                print(f"[CACHE IGNORE: fallback-hit] {key}")
            else:
                print(f"[CACHE HIT] {key}")
                return {"meaning_line": line}

    print(f"[CACHE MISS{' (nocache)' if nocache else ''}{' (refresh)' if refresh else ''}] {key} → LLM")
    data = await interpret_with_llm(term, context_sentence)
    line = data.get("meaning_line") if isinstance(data, dict) else str(data or "")
    if _is_fallback_line(line):
        print(f"[CACHE SKIP: fallback] {key}")
        return {"meaning_line": line}

    # refresh=true면 성공값으로 덮어씀
    await _safe_set(rds, key, json.dumps({"meaning_line": line}, ensure_ascii=False), ex=CACHE_TTL_SEC)
    print(f"[CACHE SET] {key}")
    return {"meaning_line": line}

async def get_all_jargon_terms(db: AsyncSession):
    result = await db.execute(select(models.Jargon.term))
    return result.scalars().all()

async def analyze_user_input(user_input: str) -> dict:
    """사용자 입력을 분석하여 신조어와 문맥을 추출합니다."""
    return await analyze_conversation_context(user_input)

async def get_contextual_interpretation(term: str, context_sentence: str, db: AsyncSession, redis_client: redis.Redis):
    """문맥을 고려한 신조어 해석을 제공합니다."""
    return await get_interpretation(term, db, redis_client, context_sentence)

async def batch_interpret_terms(terms: list, context_sentence: str = None, db: AsyncSession = None, redis_client: redis.Redis = None):
    """여러 신조어를 일괄 해석합니다."""
    results = []
    
    for term in terms:
        try:
            if db and redis_client:
                result = await get_interpretation(term, db, redis_client, context_sentence)
            else:
                result = await interpret_with_llm(term, context_sentence)
            
            results.append({
                "term": term,
                "success": True,
                "result": result
            })
        except Exception as e:
            results.append({
                "term": term,
                "success": False,
                "error": str(e)
            })
    
    return results