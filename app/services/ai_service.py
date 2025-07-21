from openai import AsyncOpenAI
from app.core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def interpret_with_llm(term: str) -> dict | None:
    # 이 부분은 실제 서비스에 맞게 정교한 프롬프트 엔지니어링이 필요합니다.
    prompt = f"""
    The Korean new slang word is '{term}'.
    1. Explain its meaning and nuance in a simple way.
    2. Provide a natural example sentence using the word.
    
    Provide the output in JSON format with "meaning" and "example" keys.
    """
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        # 실제로는 JSON 파싱 및 유효성 검사가 필요합니다.
        import json
        return json.loads(content)
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return None
