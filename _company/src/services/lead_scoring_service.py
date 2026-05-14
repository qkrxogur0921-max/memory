import os
from typing import Dict, Any

# --- Configuration & Constants ---
CRM_API_ENDPOINT = "https://api.crmsystem.com/v1/leads" 
SLACK_WEBHOOK_URL = "YOUR_HIGH_PRIORITY_SLACK_WEBHOOK" # 실제 환경변수로 대체 필수
MINIMUM_HIGH_RISK_SCORE = 75 # 스코어 임계값 정의

# --- Mock API Clients (실제 사용 시 OAuth/Key 관리 필요) ---
class CRMClient:
    """가상의 CRM 시스템과 통신하는 클라이언트."""
    def __init__(self, api_key):
        self.api_key = api_key
        print(f"[CRM] Initialized with API Key.")

    def create_lead(self, lead_data: Dict[str, Any], score: int) -> bool:
        """실제 CRM 시스템에 리드 정보를 기록하고 ID를 반환하는 함수."""
        print("------------------------------------------")
        print(f"[CRM] 🚀 Attempting to record new lead...")
        # 실제 API 호출 로직 (requests.post 등 사용)이 들어갈 자리
        if self.api_key:
            # Mock 성공 응답 처리
            lead_id = f"LEAD-{hash(str(lead_data)) % 10000}"
            print(f"[CRM] ✅ Successfully recorded lead {lead_id} (Score: {score}).")
            return True, lead_id
        else:
            print("[CRM] ❌ Error: API Key missing.")
            return False, None

class AlertClient:
    """고위험군 감지 시 담당자에게 알림을 전송하는 클라이언트."""
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        print("[Alert] Initialized with Slack Webhook.")

    def send_high_risk_alert(self, lead_data: Dict[str, Any], score: int) -> bool:
        """슬랙 또는 이메일을 통해 담당자에게 즉시 알림을 전송합니다."""
        print("------------------------------------------")
        print("[Alert] 🚨 HIGH RISK LEAD DETECTED!")
        alert_message = (
            f"🚨 **긴급 리드 경보**: 신규 고위험군 잠재 고객 발견!\n"
            f"👤 이름: {lead_data.get('name', 'N/A')} ({lead_data.get('email')})\n"
            f"🏢 회사 규모: {lead_data.get('company_size', 'N/A')}, 산업군: {lead_data.get('industry', 'N/A')}\n"
            f"💰 스코어링 점수: **{score}점** (임계치 초과)\n"
            f"👉 즉시 $1,500$ 오퍼링 전송 및 후속 컨설팅 연결 필요."
        )
        # 실제 Slack/Email API 호출 로직이 들어갈 자리
        print(f"[Alert] 💬 Sending alert via webhook: {alert_message}")
        return True

def calculate_lead_score(data: Dict[str, Any]) -> int:
    """제공된 데이터를 기반으로 리드 스코어링 점수를 계산하는 핵심 로직."""
    score = 0
    # 가중치 설정 (이 값들은 비즈니스 목표에 따라 조정되어야 합니다.)
    weight_size = 35  # 회사 규모가 클수록 높은 점수
    weight_industry = 40 # 산업군 특성이 높을수록 높은 점수

    company_size = data.get('company_size', 'S')
    industry = data.get('industry', 'N/A').upper()

    # 1. 회사 규모 스코어링
    if company_size == 'Large':
        score += weight_size # 예시: 35점 추가
    elif company_size == 'Mid':
        score += int(weight_size * 0.6) # 예시: 21점 추가

    # 2. 산업군 스코어링 (고위험/고가치 산업군 정의 필요)
    if "FINTECH" in industry or "HEALTHCARE" in industry:
        score += weight_industry # 예시: 40점 추가
    elif "GOVERNMENT" in industry:
        score += int(weight_industry * 0.8) # 예시: 32점 추가

    return score

def process_lead_submission(raw_data: Dict[str, Any]):
    """전체 워크플로우를 실행하는 메인 함수."""
    print("============================================")
    print("⚙️ STARTING LEAD SCORING AND AUTOMATION WORKFLOW")
    print("============================================\n")

    # 1. 스코어 계산 및 점수화
    lead_score = calculate_lead_score(raw_data)
    print(f"✨ [Scoring Engine] Calculated Score for {raw_data.get('name')}: {lead_score}점.")

    crm = CRMClient(api_key=os.environ.get("CRM_API_KEY"))
    alert = AlertClient(webhook_url=os.environ.get("SLACK_WEBHOOK_URL"))

    # 2. CRM 기록 (필수 단계)
    success, lead_id = crm.create_lead(raw_data, lead_score)

    if not success:
        print("[FAILURE] Critical Error: Failed to record lead in CRM. Process halted.")
        return False
    
    # 3. 고위험군 체크 및 알림 (조건부 액션)
    if lead_score >= MINIMUM_HIGH_RISK_SCORE:
        print(f"[CHECK] Score {lead_score} meets High Risk threshold ({MINIMUM_HIGH_RISK_SCORE}).")
        alert.send_high_risk_alert(raw_data, lead_score)
    else:
        print("[CHECK] Lead is standard risk level. Monitoring only.")

    return True

# --- Test Block (개발/테스트 환경용) ---
if __name__ == '__main__':
    # 1. [High Risk Test Case]: 대형 회사, 고가치 산업군
    high_risk_lead = {
        "name": "김철수", 
        "email": "chulsoo@largecorp.com", 
        "company_size": "Large", 
        "industry": "FINTECH",
        "company_info": "금융기술 대기업"
    }
    print("====================\n[RUNNING TEST CASE 1: HIGH RISK]\n")
    process_lead_submission(high_risk_lead)

    # 2. [Low Risk Test Case]: 중소 규모, 일반 산업군
    low_risk_lead = {
        "name": "이영희", 
        "email": "younghee@smallbiz.net", 
        "company_size": "Mid", 
        "industry": "Retail",
        "company_info": "소매업 중견기업"
    }
    print("\n\n====================\n[RUNNING TEST CASE 2: LOW RISK]\n")
    process_lead_submission(low_risk_lead)