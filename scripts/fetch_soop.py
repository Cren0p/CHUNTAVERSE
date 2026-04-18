import json
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
        result["broad_no"] = channel.get("BNO")
        try:
            result["btime"] = int(channel.get("BTIME", 0))
        except (ValueError, TypeError):
            result["btime"] = None
        if result["broad_no"]:
            result["thumb"] = f"https://liveimg.sooplive.co.kr/m/{result['broad_no']}"

    return result


def main():
    results = []
    for member in MEMBERS:
        data = fetch_live(member["id"])
        results.append(extract(member, data))

    kst = timezone(timedelta(hours=9))
    output = {
        "updated_at": datetime.now(kst).isoformat(),
        "members": results,
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    live_count = sum(1 for r in results if r["live"])
    print(f"완료: {live_count}명 방송 중")


if __name__ == "__main__":
    main()
