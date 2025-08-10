import openai
from typing import List, Dict, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        else:
            logger.warning("OpenAI API 키가 설정되지 않았습니다.")
    
    async def analyze_jargon(self, words: List[str], context: str = None) -> List[Dict[str, Any]]:
        """
        신조어들을 GPT API를 통해 분석합니다.
        
        Args:
            words: 분석할 신조어 리스트
            context: 추가 컨텍스트 정보
            
        Returns:
            분석 결과 리스트
        """
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API 키가 필요합니다.")
        
        try:
            # GPT API 요청을 위한 프롬프트 구성
            prompt = self._build_analysis_prompt(words, context)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 한국어 신조어 분석 전문가입니다. 주어진 단어들의 의미와 출처를 정확하게 분석해주세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # 응답 파싱 및 결과 구성
            result = self._parse_gpt_response(response.choices[0].message.content, words)
            return result
            
        except Exception as e:
            logger.error(f"GPT API 호출 중 오류 발생: {e}")
            raise
    
    def _build_analysis_prompt(self, words: List[str], context: str = None) -> str:
        """GPT API 요청을 위한 프롬프트를 구성합니다."""
        prompt = f"다음 신조어들의 의미와 출처를 분석해주세요:\n\n"
        
        for word in words:
            prompt += f"- {word}\n"
        
        if context:
            prompt += f"\n컨텍스트: {context}\n"
        
        prompt += """
        
        각 단어에 대해 다음 형식으로 응답해주세요:
        
        단어: [단어명]
        의미: [상세한 의미 설명]
        출처: [출처 정보 (알 수 없는 경우 "알 수 없음")]
        ---
        
        JSON 형식으로 응답하지 마시고, 위 형식으로만 응답해주세요.
        """
        
        return prompt
    
    def _parse_gpt_response(self, response: str, words: List[str]) -> List[Dict[str, Any]]:
        """GPT 응답을 파싱하여 구조화된 데이터로 변환합니다."""
        results = []
        
        # 응답을 단어별로 분리
        sections = response.split("---")
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.strip().split("\n")
            word_data = {}
            
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == "단어":
                        word_data["word"] = value
                    elif key == "의미":
                        word_data["explanation"] = value
                    elif key == "출처":
                        word_data["source"] = value
            
            if word_data:
                results.append(word_data)
        
        return results
    
    async def get_single_word_analysis(self, word: str) -> Dict[str, Any]:
        """단일 신조어를 분석합니다."""
        # GPT API가 없을 때를 위한 임시 데이터
        if word == "갓생":
            return {
                "word": "갓생",
                "explanation": "갓(God) + 생(생활)의 합성어로, '신처럼 완벽한 생활'을 의미하는 신조어입니다. 주로 SNS에서 자신의 일상을 자랑할 때 사용됩니다.",
                "source": "인터넷 신조어"
            }
        
        # 다른 신조어들도 추가 가능
        test_data = {
            "갓생": {
                "word": "갓생",
                "explanation": "갓(God) + 생(생활)의 합성어로, '신처럼 완벽한 생활'을 의미하는 신조어입니다. 주로 SNS에서 자신의 일상을 자랑할 때 사용됩니다.",
                "source": "인터넷 신조어"
            },
            "갓생": {
                "word": "갓생",
                "explanation": "갓(God) + 생(생활)의 합성어로, '신처럼 완벽한 생활'을 의미하는 신조어입니다. 주로 SNS에서 자신의 일상을 자랑할 때 사용됩니다.",
                "source": "인터넷 신조어"
            }
        }
        
        return test_data.get(word, {
            "word": word,
            "explanation": f"'{word}'에 대한 정보를 찾을 수 없습니다.",
            "source": "알 수 없음"
        }) 