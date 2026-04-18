import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

MEMBERS = [
    {"id": "243000",      "name": "천양",   "emoji": "🌙"},
    {"id": "madaomm",     "name": "마다옴", "emoji": "🌸"},
    {"id": "nanamoon777", "name": "나나문", "emoji": "🐰"},
    {"id": "imha22",      "name": "임하밍", "emoji": "🌿"},
    {"id": "doormomo",    "name": "문모모", "emoji": "🌷"},
    {"id": "kim91709",    "name": "한아밍", "emoji": "🌟"},
    {"id": "kappuchan",   "name": "카푸",   "emoji": "☁️"},
    {"id": "kyaang123",   "name": "캬앙",   "emoji": "🔥"},
    {"id": "wellro314",   "name": "김웰로", "emoji": "🎵"},
    {"id": "mocamu2",     "name": "모카",   "emoji": "☕"},
    {"id": "dalta20",     "name": "달타",   "emoji": "⚡"},
    {"id": "baeksoon2",   "name": "파니",   "emoji": "🦊"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Origin": "https://www.sooplive.co.kr",
    "Referer": "https://www.sooplive.co.kr/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9",
}


def fetch_station(user_id):
    url = f"https://ch.sooplive.co.kr/api/{user_id}/station"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            # 디버그: 첫 200자 출력
            if user_id == "nanamoon777":
                print(f"\n=== {user_id} 원본 응답 (200자) ===")
                print(repr(raw[:200]))
                print(f"Content-Type: {resp.headers.get('Content-Type')}")
                print(f"Status: {resp.status}")
                print("=== 끝 ===\n")
            return json.loads(raw)
    except Exception as e:
        print(f"[{user_id}] 실패: {e}")
        return None


def extract(member, data):
    result = {
        "id": member["id"],
        "name": member["name"],
        "emoji": member["emoji"],
        "live": False,
        "title": None,
        "viewers": None,
        "thumb": None,
        "broad_no": None,
    }
    if not data:
        return result

    broad = data.get("broad")
    if broad and broad.get("broad_no"):
        result["live"] = True
        result["title"] = broad.get("broad_title", "")
        result["broad_no"] = broad.get("broad_no")
        viewers = broad.get("current_sum_viewer_cnt")
        try:
            result["viewers"] = int(viewers) if viewers is not None else None
        except (ValueError, TypeError):
            result["viewers"] = None
        result["thumb"] = f"https://liveimg.sooplive.co.kr/m/{broad['broad_no']}"

    return result


def main():
    results = []
    for member in MEMBERS:
        data = fetch_station(member["id"])
        results.append(extract(member, data))

    kst = timezone(timedelta(hours=9))
    output = {
        "updated_at": datetime.now(kst).isoformat(),
        "members": results,
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    live_count = sum(1 for r in results if r["live"])
    print(f"\n완료: {live_count}명 방송 중")


if __name__ == "__main__":
    main()
