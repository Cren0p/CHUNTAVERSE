import json
import os
import urllib.request
import urllib.parse
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
    "Origin": "https://play.sooplive.co.kr",
    "Referer": "https://play.sooplive.co.kr/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded",
}

MAX_EVENTS = 100  # 최근 이벤트 100개만 보관


def fetch_live(user_id):
    url = "https://live.sooplive.co.kr/afreeca/player_live_api.php"
    data = urllib.parse.urlencode({
        "bid": user_id,
        "bno": "",
        "type": "live",
        "confirm_adult": "false",
        "player_type": "html5",
        "mode": "landing",
        "from_api": "0",
        "pwd": "",
        "stream_type": "common",
        "quality": "HD",
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
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
        "category": None,
        "btime": None,
        "thumb": None,
        "broad_no": None,
    }
    if not data:
        return result

    channel = data.get("CHANNEL", {})
    if channel.get("RESULT") == 1:
        result["live"] = True
        result["title"] = channel.get("TITLE", "")
        result["category"] = channel.get("CATE", "")
        result["broad_no"] = channel.get("BNO")
        try:
            result["btime"] = int(channel.get("BTIME", 0))
        except (ValueError, TypeError):
            result["btime"] = None
        if result["broad_no"]:
            result["thumb"] = f"https://liveimg.sooplive.co.kr/m/{result['broad_no']}"

    return result


def load_prev_data():
    """이전 data.json 읽기"""
    if not os.path.exists("data.json"):
        return None
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_events():
    """기존 events.json 읽기"""
    if not os.path.exists("events.json"):
        return []
    try:
        with open("events.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("events", [])
    except Exception:
        return []


def detect_events(prev_data, current_members, now_iso):
    """이전 상태와 현재 상태를 비교해서 이벤트 감지"""
    events = []
    if not prev_data:
        return events

    prev_by_id = {m["id"]: m for m in prev_data.get("members", [])}

    for m in current_members:
        prev = prev_by_id.get(m["id"])
        if not prev:
            continue

        # 방송 시작
        if not prev["live"] and m["live"]:
            events.append({
                "time": now_iso,
                "type": "start",
                "member_id": m["id"],
                "member_name": m["name"],
                "emoji": m["emoji"],
                "title": m.get("title", ""),
            })
        # 방송 종료
        elif prev["live"] and not m["live"]:
            events.append({
                "time": now_iso,
                "type": "end",
                "member_id": m["id"],
                "member_name": m["name"],
                "emoji": m["emoji"],
            })
        # 방송 중 -> 방제 변경
        elif prev["live"] and m["live"]:
            if prev.get("title") != m.get("title"):
                events.append({
                    "time": now_iso,
                    "type": "title",
                    "member_id": m["id"],
                    "member_name": m["name"],
                    "emoji": m["emoji"],
                    "before": prev.get("title", ""),
                    "after": m.get("title", ""),
                })
            # 카테고리 변경
            if prev.get("category") and m.get("category") and prev.get("category") != m.get("category"):
                events.append({
                    "time": now_iso,
                    "type": "category",
                    "member_id": m["id"],
                    "member_name": m["name"],
                    "emoji": m["emoji"],
                    "before": prev.get("category", ""),
                    "after": m.get("category", ""),
                })

    return events


def main():
    # 이전 데이터 로드 (이벤트 비교용)
    prev_data = load_prev_data()

    # 현재 상태 조회
    results = []
    for member in MEMBERS:
        data = fetch_live(member["id"])
        results.append(extract(member, data))

    kst = timezone(timedelta(hours=9))
    now_iso = datetime.now(kst).isoformat()

    # 이벤트 감지
    new_events = detect_events(prev_data, results, now_iso)
    if new_events:
        print(f"새 이벤트 {len(new_events)}개 감지")
        existing_events = load_events()
        # 새 이벤트를 앞에 추가 (최신순)
        all_events = new_events + existing_events
        # 최근 MAX_EVENTS개만 유지
        all_events = all_events[:MAX_EVENTS]

        with open("events.json", "w", encoding="utf-8") as f:
            json.dump({
                "updated_at": now_iso,
                "events": all_events,
            }, f, ensure_ascii=False, indent=2)

    # data.json 저장
    output = {
        "updated_at": now_iso,
        "members": results,
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    live_count = sum(1 for r in results if r["live"])
    print(f"완료: {live_count}명 방송 중")


if __name__ == "__main__":
    main()
