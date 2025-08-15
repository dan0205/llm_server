#!/usr/bin/env python3
"""
신조어 해석 API 테스트 스크립트
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class APITester:
    def __init__(self):
        self.session = None
        self.test_results = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, method: str, endpoint: str, expected_status: int = 200, **kwargs) -> Dict[str, Any]:
        """API 엔드포인트를 테스트합니다."""
        url = f"{API_BASE}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, **kwargs) as response:
                    status = response.status
                    data = await response.json() if response.content_type == 'application/json' else await response.text()
            elif method.upper() == "POST":
                async with self.session.post(url, **kwargs) as response:
                    status = response.status
                    data = await response.json() if response.content_type == 'application/json' else await response.text()
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
            
            success = status == expected_status
            result = {
                "endpoint": endpoint,
                "method": method,
                "status": status,
                "expected": expected_status,
                "success": success,
                "data": data,
                "error": None
            }
            
            if not success:
                result["error"] = f"예상 상태 코드: {expected_status}, 실제: {status}"
            
        except Exception as e:
            result = {
                "endpoint": endpoint,
                "method": method,
                "status": None,
                "expected": expected_status,
                "success": False,
                "data": None,
                "error": str(e)
            }
        
        self.test_results.append(result)
        return result
    
    async def test_basic_endpoints(self):
        """기본 엔드포인트들을 테스트합니다."""
        print("🔍 기본 엔드포인트 테스트 중...")
        
        # 서버 상태 확인
        await self.test_endpoint("GET", "/docs", 200)
        
        # 모든 신조어 목록 조회
        await self.test_endpoint("GET", "/jargons", 200)
    
    async def test_jargon_interpretation(self):
        """신조어 해석 기능을 테스트합니다."""
        print("🧠 신조어 해석 테스트 중...")
        
        # 기본 신조어 해석 (캐시 없음)
        await self.test_endpoint("GET", "/jargons/interpret/갑분싸", 200)
        
        # 문맥과 함께 신조어 해석
        await self.test_endpoint("GET", "/jargons/interpret/대박?context=오늘%20시험에서%20대박%20났어!", 200)
        
        # 동일한 신조어 재시도 (캐시 히트)
        await self.test_endpoint("GET", "/jargons/interpret/갑분싸", 200)
        
        # 잘못된 입력 테스트
        await self.test_endpoint("GET", "/jargons/interpret/", 400)  # 빈 텍스트
        await self.test_endpoint("GET", "/jargons/interpret/" + "a" * 101, 400)  # 너무 긴 텍스트
    
    async def test_contextual_interpretation(self):
        """문맥 기반 해석을 테스트합니다."""
        print("📝 문맥 기반 해석 테스트 중...")
        
        # 다양한 문맥으로 테스트
        contexts = [
            "게임에서 레벨업했어!",
            "회사에서 프로젝트가 성공했어!",
            "친구와 재미있게 놀았어!"
        ]
        
        for context in contexts:
            await self.test_endpoint("GET", f"/jargons/interpret/대박?context={context}", 200)
    
    async def test_error_handling(self):
        """에러 처리를 테스트합니다."""
        print("⚠️ 에러 처리 테스트 중...")
        
        # 존재하지 않는 엔드포인트
        await self.test_endpoint("GET", "/nonexistent", 404)
        
        # 잘못된 신조어 형식
        await self.test_endpoint("GET", "/jargons/interpret/!@#$%", 200)  # 특수문자도 처리 가능해야 함
    
    async def test_performance(self):
        """성능을 테스트합니다."""
        print("⚡ 성능 테스트 중...")
        
        # 동시 요청 테스트
        terms = ["갑분싸", "인싸", "아싸", "대박", "헐"]
        start_time = time.time()
        
        tasks = []
        for term in terms:
            task = self.test_endpoint("GET", f"/jargons/interpret/{term}")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"📊 {len(terms)}개 신조어 동시 해석: {total_time:.2f}초")
        
        # 성공률 계산
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        success_rate = (success_count / len(results)) * 100
        print(f"📈 성공률: {success_rate:.1f}%")
    
    def print_results(self):
        """테스트 결과를 출력합니다."""
        print("\n" + "="*60)
        print("📋 테스트 결과 요약")
        print("="*60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"총 테스트: {total_tests}")
        print(f"성공: {successful_tests} ✅")
        print(f"실패: {failed_tests} ❌")
        print(f"성공률: {(successful_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['method']} {result['endpoint']}: {result['error']}")
        
        print("\n" + "="*60)
    
    async def run_all_tests(self):
        """모든 테스트를 실행합니다."""
        print("🚀 신조어 해석 API 테스트 시작")
        print("="*60)
        
        try:
            await self.test_basic_endpoints()
            await self.test_jargon_interpretation()
            await self.test_contextual_interpretation()
            await self.test_error_handling()
            await self.test_performance()
            
        except Exception as e:
            print(f"❌ 테스트 실행 중 오류 발생: {e}")
        
        self.print_results()

async def main():
    """메인 함수"""
    async with APITester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    print("신조어 해석 API 테스트를 시작합니다...")
    print("백엔드 서버가 실행 중인지 확인하세요: http://localhost:8000")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류: {e}")
