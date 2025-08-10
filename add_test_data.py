#!/usr/bin/env python3
"""
DB에 테스트용 신조어 데이터를 추가하는 스크립트
"""

import requests
import json

def add_test_jargon():
    """테스트용 신조어 데이터를 API를 통해 추가"""
    
    # 테스트용 신조어 데이터
    test_jargons = [
        {
            "word": "갓생",
            "explanation": "갓(God) + 생(생활)의 합성어로, '신처럼 완벽한 생활'을 의미하는 신조어입니다. 주로 SNS에서 자신의 일상을 자랑할 때 사용됩니다.",
            "source": "인터넷 신조어",
            "search_count": 0,
            "is_user_modified": False
        },
        {
            "word": "갓생",
            "explanation": "갓(God) + 생(생활)의 합성어로, '신처럼 완벽한 생활'을 의미하는 신조어입니다. 주로 SNS에서 자신의 일상을 자랑할 때 사용됩니다.",
            "source": "인터넷 신조어",
            "search_count": 0,
            "is_user_modified": False
        },
        {
            "word": "갓생",
            "explanation": "갓(God) + 생(생활)의 합성어로, '신처럼 완벽한 생활'을 의미하는 신조어입니다. 주로 SNS에서 자신의 일상을 자랑할 때 사용됩니다.",
            "source": "인터넷 신조어",
            "search_count": 0,
            "is_user_modified": False
        }
    ]
    
    base_url = "http://localhost:8000"
    
    for jargon in test_jargons:
        try:
            # 신조어 조회 (이미 있으면 건너뛰기)
            response = requests.get(f"{base_url}/api/v1/jargon/{jargon['word']}")
            
            if response.status_code == 404:
                # 신조어가 없으면 생성
                print(f"'{jargon['word']}' 신조어를 DB에 추가합니다...")
                
                # POST 요청으로 신조어 생성 (간단한 방법)
                # 실제로는 API 엔드포인트를 추가해야 하지만, 
                # 여기서는 직접 DB에 접근하는 대신 기존 API 활용
                
                # 일괄 분석 API 사용
                analysis_data = {
                    "words": [jargon['word']],
                    "context": "테스트용 데이터"
                }
                
                response = requests.post(
                    f"{base_url}/api/v1/jargon/analyze",
                    json=analysis_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    print(f"✅ '{jargon['word']}' 추가 성공")
                else:
                    print(f"❌ '{jargon['word']}' 추가 실패: {response.text}")
            else:
                print(f"'{jargon['word']}' 이미 존재합니다.")
                
        except Exception as e:
            print(f"오류 발생: {e}")

if __name__ == "__main__":
    print("=== 테스트용 신조어 데이터 추가 ===")
    add_test_jargon()
    print("=== 완료 ===") 