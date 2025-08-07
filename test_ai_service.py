#!/usr/bin/env python3
"""
AI 서비스 테스트 스크립트
실행하기 전에 .env 파일에 OPENAI_API_KEY를 설정해야 합니다.
"""

import asyncio
import os
from dotenv import load_dotenv
from app.services.ai_service import (
    interpret_with_llm,
    analyze_conversation_context,
    get_similar_terms,
    clarify_ambiguous_term
)

# 환경 변수 로드
load_dotenv()

async def test_basic_interpretation():
    """기본 신조어 해석 테스트"""
    print("=== 기본 신조어 해석 테스트 ===")
    
    term = "대박"
    result = await interpret_with_llm(term)
    
    if result:
        print(f"신조어: {term}")
        print(f"의미: {result.get('meaning', 'N/A')}")
        print(f"예시: {result.get('example', 'N/A')}")
        print(f"문맥 분석: {result.get('context_analysis', 'N/A')}")
        print(f"추가 정보: {result.get('additional_info', 'N/A')}")
    else:
        print("해석 실패")
    print()

async def test_contextual_interpretation():
    """문맥 기반 신조어 해석 테스트"""
    print("=== 문맥 기반 신조어 해석 테스트 ===")
    
    term = "대박"
    context = "오늘 시험에서 대박 났어!"
    
    result = await interpret_with_llm(term, context)
    
    if result:
        print(f"신조어: {term}")
        print(f"문맥: {context}")
        print(f"의미: {result.get('meaning', 'N/A')}")
        print(f"예시: {result.get('example', 'N/A')}")
        print(f"문맥 분석: {result.get('context_analysis', 'N/A')}")
    else:
        print("해석 실패")
    print()

async def test_conversation_analysis():
    """대화 분석 테스트"""
    print("=== 대화 분석 테스트 ===")
    
    user_input = "오늘 친구가 '대박'이라고 했는데 무슨 뜻이야?"
    result = await analyze_conversation_context(user_input)
    
    print(f"사용자 입력: {user_input}")
    print(f"분석 결과: {result}")
    print()

async def test_similar_terms():
    """유사한 신조어 찾기 테스트"""
    print("=== 유사한 신조어 찾기 테스트 ===")
    
    term = "대박"
    similar_terms = await get_similar_terms(term)
    
    print(f"기준 신조어: {term}")
    print(f"유사한 신조어들: {similar_terms}")
    print()

async def test_ambiguous_clarification():
    """모호한 신조어 명확화 테스트"""
    print("=== 모호한 신조어 명확화 테스트 ===")
    
    term = "대박"
    context = "이 영화 대박이야"
    
    result = await clarify_ambiguous_term(term, context)
    
    print(f"신조어: {term}")
    print(f"문맥: {context}")
    print(f"명확화 결과: {result}")
    print()

async def main():
    """모든 테스트 실행"""
    print("🤖 AI 서비스 테스트 시작\n")
    
    # OpenAI API 키 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 OPENAI_API_KEY=your_api_key를 추가해주세요.")
        return
    
    try:
        await test_basic_interpretation()
        await test_contextual_interpretation()
        await test_conversation_analysis()
        await test_similar_terms()
        await test_ambiguous_clarification()
        
        print("✅ 모든 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 