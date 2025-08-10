#!/usr/bin/env python3
"""
API 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """헬스 체크 테스트"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"헬스 체크: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"헬스 체크 실패: {e}")
        return False

def test_root():
    """루트 엔드포인트 테스트"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"루트 엔드포인트: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"루트 엔드포인트 실패: {e}")
        return False

def test_jargon_analysis():
    """신조어 분석 테스트"""
    try:
        data = {
            "words": ["갓생", "갓생"],
            "context": "최근 인터넷에서 자주 사용되는 신조어들"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/jargon/analyze",
            json=data
        )
        
        print(f"신조어 분석: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"분석 결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"신조어 분석 실패: {e}")
        return False

def test_get_jargon():
    """신조어 조회 테스트"""
    try:
        word = "갓생"
        response = requests.get(f"{BASE_URL}/api/v1/jargon/{word}")
        
        print(f"신조어 조회 ({word}): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"조회 결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"신조어 조회 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("=== LLM 신조어 분석 API 테스트 ===\n")
    
    tests = [
        ("헬스 체크", test_health_check),
        ("루트 엔드포인트", test_root),
        ("신조어 분석", test_jargon_analysis),
        ("신조어 조회", test_get_jargon),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} 테스트 ---")
        if test_func():
            print(f"✅ {test_name} 성공")
            passed += 1
        else:
            print(f"❌ {test_name} 실패")
    
    print(f"\n=== 테스트 결과: {passed}/{total} 통과 ===")

if __name__ == "__main__":
    main() 