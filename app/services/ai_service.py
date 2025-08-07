import json
import re
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from app.core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class ContextAnalyzer:
    """문맥 분석을 위한 클래스"""
    
    @staticmethod
    def extract_context_from_sentence(sentence: str, term: str) -> Dict[str, Any]:
        """문장에서 신조어의 문맥을 분석합니다."""
        context_info = {
            "sentence": sentence,
            "term": term,
            "context_type": "neutral",
            "emotion": "neutral",
            "formality": "casual",
            "domain": "general"
        }
        
        # 감정 분석 (간단한 키워드 기반)
        emotion_keywords = {
            "positive": ["좋아", "대박", "최고", "사랑", "행복", "웃겨"],
            "negative": ["싫어", "별로", "최악", "화나", "슬퍼", "짜증"],
            "surprise": ["헐", "와", "진짜", "대박", "놀라"]
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in sentence for keyword in keywords):
                context_info["emotion"] = emotion
                break
        
        # 격식 수준 분석
        formal_patterns = ["습니다", "니다", "습니다", "입니다"]
        if any(pattern in sentence for pattern in formal_patterns):
            context_info["formality"] = "formal"
        
        # 도메인 분석
        domain_keywords = {
            "gaming": ["게임", "플레이", "스킬", "레벨", "팀"],
            "social_media": ["인스타", "틱톡", "유튜브", "팔로우", "좋아요"],
            "work": ["회사", "업무", "프로젝트", "회의", "보고서"],
            "school": ["학교", "수업", "과제", "시험", "친구"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in sentence for keyword in keywords):
                context_info["domain"] = domain
                break
        
        return context_info

class ConversationManager:
    """대화 히스토리 관리 클래스"""
    
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        """대화 히스토리에 메시지 추가"""
        self.conversation_history.append({"role": role, "content": content})
        
        # 히스토리 길이 제한 (최근 10개 메시지)
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_context_messages(self) -> List[Dict[str, str]]:
        """문맥 분석을 위한 메시지 반환"""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """대화 히스토리 초기화"""
        self.conversation_history.clear()

# 전역 대화 관리자 (실제로는 사용자별로 관리해야 함)
conversation_manager = ConversationManager()

async def interpret_with_llm(term: str, context_sentence: Optional[str] = None) -> dict | None:
    """향상된 문맥 기반 신조어 해석"""
    
    # 문맥 분석
    context_info = None
    if context_sentence:
        context_info = ContextAnalyzer.extract_context_from_sentence(context_sentence, term)
        conversation_manager.add_message("user", f"문장: {context_sentence}, 신조어: {term}")
    
    # 시스템 프롬프트 구성
    system_prompt = """당신은 한국어 신조어 전문가입니다. 다음 지침을 따라 신조어를 해석해주세요:

1. **문맥 고려**: 제공된 문장의 문맥을 고려하여 가장 적절한 의미를 찾아주세요.
2. **감정 분석**: 문장의 감정적 톤에 맞는 해석을 제공하세요.
3. **사용 맥락**: 격식 수준과 사용 도메인을 고려하세요.
4. **예시 제공**: 실제 사용할 수 있는 자연스러운 예시를 제공하세요.
5. **추가 정보**: 필요시 유사어, 반대어, 사용 팁 등을 제공하세요.

반드시 다음 JSON 형식으로 응답해주세요:
{
    "meaning": "신조어의 의미",
    "example": "사용 예시",
    "context_analysis": {
        "detected_emotion": "감지된 감정",
        "formality_level": "격식 수준",
        "usage_domain": "사용 도메인"
    },
    "additional_info": {
        "similar_terms": ["유사한 표현들"],
        "usage_tips": "사용 시 주의사항",
        "origin": "어원 정보 (알려진 경우)"
    }
}"""

    # 사용자 프롬프트 구성
    user_prompt = f"신조어: '{term}'"
    
    if context_info:
        user_prompt += f"\n\n문맥 정보:\n- 문장: {context_info['sentence']}\n- 감정: {context_info['emotion']}\n- 격식: {context_info['formality']}\n- 도메인: {context_info['domain']}"
    
    # 대화 히스토리 추가
    messages = [{"role": "system", "content": system_prompt}]
    
    # 최근 대화 히스토리 추가 (문맥 이해를 위해)
    context_messages = conversation_manager.get_context_messages()
    if context_messages:
        messages.extend(context_messages[-4:])  # 최근 4개 메시지만 사용
    
    messages.append({"role": "user", "content": user_prompt})
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7,  # 창의성과 일관성의 균형
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # 응답을 대화 히스토리에 추가
        conversation_manager.add_message("assistant", json.dumps(result, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return None

async def analyze_conversation_context(user_input: str) -> Dict[str, Any]:
    """대화 문맥을 분석하여 신조어와 문맥을 추출합니다."""
    
    analysis_prompt = f"""
다음 사용자 입력에서 신조어와 문맥을 분석해주세요:

사용자 입력: "{user_input}"

다음 JSON 형식으로 응답해주세요:
{{
    "detected_terms": ["발견된 신조어들"],
    "primary_term": "주요 분석 대상 신조어",
    "context_sentence": "신조어가 사용된 문장",
    "conversation_intent": "사용자의 의도 (질문/설명/예시 등)",
    "requires_clarification": true/false
}}
"""
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": analysis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
    except Exception as e:
        print(f"Error analyzing conversation context: {e}")
        return {
            "detected_terms": [],
            "primary_term": "",
            "context_sentence": user_input,
            "conversation_intent": "unknown",
            "requires_clarification": False
        }

async def get_similar_terms(term: str) -> List[str]:
    """유사한 신조어들을 찾습니다."""
    
    prompt = f"""
'{term}'와 유사하거나 관련된 한국어 신조어들을 찾아주세요.
의미적으로 유사하거나, 같은 맥락에서 사용되는 신조어들을 포함해주세요.

JSON 형식으로 응답해주세요:
{{
    "similar_terms": ["유사한 신조어들"],
    "related_concepts": ["관련 개념들"]
}}
"""
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        return result.get("similar_terms", [])
        
    except Exception as e:
        print(f"Error finding similar terms: {e}")
        return []

async def clarify_ambiguous_term(term: str, context: str) -> Dict[str, Any]:
    """모호한 신조어의 의미를 명확히 합니다."""
    
    prompt = f"""
신조어 '{term}'이 문맥 '{context}'에서 모호하게 사용되었습니다.
가능한 모든 의미를 분석하고, 문맥에 가장 적합한 의미를 추천해주세요.

JSON 형식으로 응답해주세요:
{{
    "possible_meanings": [
        {{
            "meaning": "의미 1",
            "confidence": 0.8,
            "explanation": "이 의미가 적합한 이유"
        }}
    ],
    "recommended_meaning": "추천하는 의미",
    "clarification_questions": ["명확히 하기 위한 질문들"]
}}
"""
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
    except Exception as e:
        print(f"Error clarifying ambiguous term: {e}")
        return {
            "possible_meanings": [],
            "recommended_meaning": "",
            "clarification_questions": []
        }
