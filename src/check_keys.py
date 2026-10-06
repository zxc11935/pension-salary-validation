"""인증키 2개(OpenDART, 공공데이터포털)가 실제로 작동하는지 한 번씩 불러 확인한다."""
import os

import requests
from dotenv import load_dotenv

load_dotenv()  # 프로젝트 폴더의 .env 값을 읽어 온다

dart_key = os.getenv("DART_API_KEY")
nps_key = os.getenv("DATA_GO_KR_KEY")
if not dart_key or not nps_key:
    raise SystemExit(".env에 DART_API_KEY와 DATA_GO_KR_KEY가 모두 있어야 해요")

# 1) OpenDART: 삼성전자(고유번호 00126380)의 기업개황을 요청한다
res = requests.get(
    "https://opendart.fss.or.kr/api/company.json",
    params={"crtfc_key": dart_key, "corp_code": "00126380"},
    timeout=10,
)
dart = res.json()
# status "000"이 정상. 키가 틀리면 "010" 같은 오류 코드가 온다
print("[OpenDART]", dart.get("status"), dart.get("message"))
print("  회사명:", dart.get("corp_name"), "/ 사업자등록번호:", dart.get("bizr_no"))

# 2) 국민연금: 사업장명에 '삼성전자'가 들어간 사업장을 검색한다
res = requests.get(
    "https://apis.data.go.kr/B552015/NpsBplcInfoInqireServiceV2/getBassInfoSearchV2",
    params={
        "serviceKey": nps_key,  # 디코딩(Decoding) 키. requests가 주소에 맞게 알아서 인코딩한다
        "wkplNm": "삼성전자",
        "dataType": "json",
        "pageNo": 1,
        "numOfRows": 5,
    },
    timeout=10,
)
try:
    nps = res.json()["response"]
    # resultCode "00"이 정상
    print("[국민연금]", nps["header"]["resultCode"], nps["header"]["resultMsg"])
    print("  검색된 건수:", nps["body"]["totalCount"])
except (ValueError, KeyError):
    # 키 오류 같은 경우는 JSON이 아닌 형식으로 올 수 있어서, 받은 내용을 그대로 보여 준다
    print("[국민연금] 예상과 다른 응답:", res.status_code, res.text[:300])
