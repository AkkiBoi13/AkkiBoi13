"""Refresh the live section of README.md.

Reads the solar wind speed, the planetary Kp index and the 10.7 cm solar
flux from NOAA's Space Weather Prediction Center, and the latest Beatrixe
release from GitHub, then rewrites the text between the live markers.
Standard library only, so the GitHub Action needs no setup.
Run: python tools/update.py
"""
import datetime as dt
import json
import pathlib
import re
import urllib.request

README = pathlib.Path(__file__).resolve().parent.parent / "README.md"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30), "IST")
HEADERS = {"User-Agent": "AkkiBoi13-profile-readme", "Accept": "application/json"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=20) as r:
        return json.load(r)


def kp_words(kp):
    if kp >= 5:
        return f"a geomagnetic storm (G{min(5, int(kp) - 4)})"
    if kp >= 4:
        return "an unsettled magnetosphere"
    return "a quiet magnetosphere"


def flux_words(flux):
    # Rough bands for the 10.7 cm flux, in solar flux units.
    if flux >= 150:
        return "a very active Sun"
    if flux >= 100:
        return "an active Sun"
    return "a fairly calm Sun"


def lines():
    out = []
    try:
        wind = get("https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json")[0]["proton_speed"]
        kp = float(get("https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json")[-1]["Kp"])
        flux = get("https://services.swpc.noaa.gov/products/summary/10cm-flux.json")[0]["flux"]
        out.append(
            f"☉ &nbsp;The solar wind is reaching Earth at **{round(float(wind))} km/s**, "
            f"the Kp index is **{kp:.1f}** ({kp_words(kp)}), "
            f"and the 10.7 cm flux is **{round(float(flux))} sfu** ({flux_words(float(flux))})."
        )
    except Exception:  # NOAA is down or changed format: keep the rest of the page
        out.append("☉ &nbsp;Space weather from NOAA is unavailable right now. It will be back at the next update.")
    try:
        rel = get("https://api.github.com/repos/AkkiBoi13/Beatrixe/releases/latest")
        downloads = sum(a.get("download_count", 0) for a in rel.get("assets", []))
        date = dt.datetime.fromisoformat(rel["published_at"].replace("Z", "+00:00")).astimezone(IST)
        out.append(
            f"ν &nbsp;[Beatrixe {rel['tag_name']}]({rel['html_url']}) came out on {date.day} {date:%B %Y}"
            f" and its files have been downloaded **{downloads}** times."
        )
    except Exception:
        out.append("ν &nbsp;[Beatrixe](https://github.com/AkkiBoi13/Beatrixe/releases/latest) release details are unavailable right now.")
    now = dt.datetime.now(IST)
    out.append(f"<sub>Updated {now:%H:%M} IST, {now.day} {now:%b %Y}. Data: NOAA SWPC and GitHub.</sub>")
    return out


def main():
    text = README.read_text(encoding="utf-8")
    body = "\n\n".join(lines())
    block = "<!-- live:start -->\n" + body + "\n<!-- live:end -->"
    new = re.sub(r"<!-- live:start -->.*?<!-- live:end -->", lambda m: block, text, flags=re.S)
    if new != text:
        README.write_text(new, encoding="utf-8", newline="\n")
    print(body)


if __name__ == "__main__":
    main()
