"""카카오 로컬 '키워드로 장소 검색'으로 장소 5개를 찾아 보여 줍니다.

터미널:  python place.py 성수동 카페
다른 파일:  from place import search_place
"""
import os
import sys

import requests
from dotenv import load_dotenv

# 🔌 API 주소는 여기 한 곳에만
API = {
    "keyword": "https://dapi.kakao.com/v2/local/search/keyword.json",  # 🔌
}

COUNT = 5


def search_place(검색어, 개수=COUNT):
    """검색어로 장소를 찾아 [{이름, 주소, 위도, 경도}, ...] 를 돌려줍니다.

    - 못 찾으면 빈 목록 []
    - 키·설정·연결 문제는 RuntimeError('⛔ ...') (한국어 한 줄)
    """
    load_dotenv(override=True)
    key = os.getenv("KAKAO_REST_API_KEY")
    if not key:
        raise RuntimeError("⛔ .env에 KAKAO_REST_API_KEY가 없어요")

    try:
        res = requests.get(  # 🔌 API 호출
            API["keyword"],
            headers={"Authorization": f"KakaoAK {key}"},
            params={"query": 검색어, "size": 개수},
            timeout=10,
        )
    except requests.RequestException:
        raise RuntimeError("⛔ 카카오에 연결하지 못했어요. 인터넷을 확인해 주세요") from None

    if res.status_code == 401:
        raise RuntimeError("⛔ 카카오 REST API 키가 틀렸어요")
    if res.status_code == 403:
        raise RuntimeError("⛔ 카카오맵 사용 설정을 켜 주세요")
    if res.status_code != 200:
        raise RuntimeError(f"⛔ 카카오 검색이 실패했어요 (상태 코드 {res.status_code})")

    장소들 = []
    for d in res.json().get("documents", []):
        try:
            위도 = float(d["y"])  # y = 위도
            경도 = float(d["x"])  # x = 경도
        except (KeyError, ValueError):
            continue
        if not (33 <= 위도 <= 39 and 124 <= 경도 <= 132):  # 한국 밖 좌표는 버림
            continue
        장소들.append({
            "이름": d.get("place_name", ""),
            "주소": d.get("road_address_name") or d.get("address_name", ""),  # 도로명 없으면 지번
            "위도": 위도,
            "경도": 경도,
        })
    return 장소들


if __name__ == "__main__":
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")  # 윈도우 터미널에서 ⛔·한글 깨짐 방지

    검색어 = " ".join(sys.argv[1:]) or input("검색어 (예: 성수동 카페): ").strip()
    if not 검색어:
        sys.exit("검색어를 입력해 주세요")

    try:
        결과 = search_place(검색어)
    except RuntimeError as e:
        sys.exit(str(e))

    if not 결과:
        print(f"'{검색어}'을(를) 찾지 못했어요")
    else:
        print(f"'{검색어}' 검색 결과 {len(결과)}곳\n")
        for i, p in enumerate(결과, 1):
            print(f"{i}. {p['이름']}")
            print(f"   주소: {p['주소']}")
            print(f"   좌표: ({p['위도']}, {p['경도']})")

    print("\n출처: 카카오 로컬 API (키워드로 장소 검색)")
