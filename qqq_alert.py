import yfinance as yf
import requests
import os
from datetime import datetime

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]

def get_market_info():
    qqq = yf.Ticker("QQQ")
    hist = qqq.history(period="6mo", interval="1d")

    close = hist["Close"]

    # 고점 / 저점
    high_3m = hist.tail(63)["High"].max()   # 약 3개월
    low_3m  = hist.tail(63)["Low"].min()
    current = close.iloc[-1]

    # 고점 대비 하락률
    dd_high = (current - high_3m) / high_3m * 100

    # 저점 대비 반등률
    rebound_low = (current - low_3m) / low_3m * 100

    # 이동평균
    ma50 = close.rolling(50).mean().iloc[-1]
    ma200 = close.rolling(200).mean().iloc[-1]

    structure = []
    structure_emoji = []

    if current > ma50:
        structure.append("50일선 상방")
        structure_emoji.append("🟢")
    else:
        structure.append("50일선 하방")
        structure_emoji.append("🔴")

    if current > ma200:
        structure.append("200일선 상방")
        structure_emoji.append("🟢")
    else:
        structure.append("200일선 하방")
        structure_emoji.append("🔴")

    if ma50 > ma200:
        structure.append("중기 > 장기 (상승 구조)")
        structure_emoji.append("📈")
    else:
        structure.append("중기 < 장기 (하락 구조)")
        structure_emoji.append("📉")

    return {
        "current": current,
        "high_3m": high_3m,
        "low_3m": low_3m,
        "dd_high": dd_high,
        "rebound_low": rebound_low,
        "ma50": ma50,
        "ma200": ma200,
        "structure": structure,
        "structure_emoji": structure_emoji
    }

def send_discord(msg):
    requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})

def main():
    data = get_market_info()

    message = (
        "──────────────────────────────\n"
        f"📊 **QQQ 시장 구조 체크**\n"
        f"⏰ **{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}**\n\n"
        f"1️⃣ **고점 대비 변화**\n"
        f"- 3개월 고점: {data['high_3m']:.2f}\n"
        f"- 현재가: {data['current']:.2f}\n"
        f"- 고점 대비: {data['dd_high']:.2f}%\n\n"
        f"2️⃣ **저점 대비 변화**\n"
        f"- 3개월 저점: {data['low_3m']:.2f}\n"
        f"- 저점 대비: +{data['rebound_low']:.2f}%\n\n"
        f"3️⃣ **시장 구조 (추세)**\n"
        f"{data['structure_emoji'][0]} {data['structure'][0]}\n"
        f"{data['structure_emoji'][1]} {data['structure'][1]}\n"
        f"{data['structure_emoji'][2]} {data['structure'][2]}\n\n"
        f"🧠 **해석 가이드**\n"
        f"- QLD는 50·200일선 하방 시 비중 조절\n"
        f"- 고점 대비 -15% 이하 + 구조 회복 시 유리\n"
        "──────────────────────────────"
    )

    send_discord(message)

if __name__ == "__main__":
    main()
