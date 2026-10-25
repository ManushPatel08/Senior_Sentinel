"""Radar latency and cost: 10 full /scam-check runs where Claude answers (stories the rules don't refuse on
their own), end to end: rules, facts, then Claude with web search. Writes ai/eval/RADAR_LATENCY.md.

    python -m ai.eval.radar_latency

Runs against temporary files, so Ruth's real cool-down and checks are untouched. Cost is each reply's usage at
claude-opus-5-5 list prices (PRICES); rerun with other prices if RADAR_MODEL names another model.
"""

from __future__ import annotations

import datetime as dt
import math
import os
import statistics
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
_TMP = tempfile.mkdtemp(prefix="radar_latency_")
for var, name in (("RISK_PATH", "risk.json"), ("RADAR_CACHE_PATH", "cache.json"), ("SCAM_CHECKS_PATH", "checks.json"),
                  ("DECISIONS_PATH", "decisions.json")):
    os.environ[var] = str(Path(_TMP) / name)
os.environ["RELAY_URL"] = ""

from policy import scamcheck  # noqa: E402
from policy.screen import screen  # noqa: E402

# claude-opus-5-5 list prices: USD per million tokens of each usage field, and per web search
PRICES = {"input_tokens": 4.00, "output_tokens": 20.00, "cache_read_input_tokens": 0.20,
          "cache_creation_input_tokens": 5.00}
SEARCH_USD = 0.01
STORIES = [
    ("en", "Someone from Social Security called and says my number was used in a crime and I need to verify it today."),
    ("en", "A man called saying he's from my bank's fraud team and my account has suspicious activity."),
    ("en", "I got a text that my Amazon order was charged twice and I should call a number to fix it."),
    ("en", "A woman called and said I won a sweepstakes, but I have to cover the taxes first."),
    ("es", "Me llamó un hombre del Seguro Social, dice que mi número está suspendido y tengo que confirmarlo hoy."),
    ("es", "Recibí un mensaje de que mi paquete no se pudo entregar y tengo que confirmar mi dirección en un enlace."),
    ("hi", "किसी ने फोन करके कहा कि मेरा बैंक खाता बंद होने वाला है और मुझे अपनी जानकारी देनी होगी।"),
    ("hi", "एक आदमी का फोन आया, बोला कि मेरे नाम पर एक पार्सल में गैरकानूनी सामान मिला है।"),
    ("hi", "Ek aadmi ne phone karke kaha ki meri bijli ka bill galat hai aur use theek karna hai."),
    ("en", "My neighbor's son says he can double my savings if I invest with his friend this week."),
]


def main() -> None:
    costs: list[float] = []
    real_radar = scamcheck.radar

    def counting_radar(*args, **kwargs):
        v = real_radar(*args, **kwargs)
        u = v.get("usage") or {}
        costs.append(sum(u.get(k, 0) * p for k, p in PRICES.items()) / 1_000_000 + u.get("web_searches", 0) * SEARCH_USD)
        return v

    scamcheck.radar = counting_radar
    rows, times = [], []
    for lang, story in STORIES:
        if screen(story, lang)["action"] == "refuse":
            rows.append(f"| {lang} | {story[:70]} | skipped (a rule refuses it; Claude would not run) | | | |")
            continue
        out = scamcheck.check(story, lang)
        times.append(out["ms"])
        rows.append(f"| {lang} | {story[:70]} | {out['verdict']} | {out['ms']} | {len(out['sources'])} | "
                    f"{'cache' if out['from_cache'] else 'Claude'} |")
        print(f"{lang} {out['ms']:6} ms  {out['verdict']:6} sources={len(out['sources'])}  {story[:50]}")
    times.sort()
    p90 = times[min(len(times) - 1, math.ceil(0.9 * len(times)) - 1)] if times else 0
    usd = costs
    lines = [
        "# Scam radar latency and cost", "",
        f"Run {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}: {len(times)} full `/scam-check` runs where Claude answers "
        "(rules, account facts, then Claude with web search), one after another, against temporary files.", "",
        f"- **Latency:** median {statistics.median(times) if times else 0:.0f} ms, p90 {p90} ms, max {max(times) if times else 0} ms "
        f"(budget 11 s; the station and the line wait up to 14 s).",
        f"- **Cost per check:** median ${statistics.median(usd) if usd else 0:.3f}, max ${max(usd) if usd else 0:.3f} "
        f"({len(usd)} calls; each reply's usage at claude-opus-5-5 list prices, $4/$20 per million tokens in/out and "
        "$0.01 per web search). These are checks the rules don't settle, so Claude answers Ruth; every such check calls "
        "Claude, and the cache is only the fallback when Claude is late or fails.",
        "- **A rule hit is not free:** Ruth's answer doesn't wait for Claude, but unless the story, or an earlier scam check "
        "of the same pattern in the same language, has cached sources, one Claude call with the same web search still "
        "runs in the background (up to `RADAR_TIMEOUT_S`, 12 s) to attach sources to Priyank's alert, at about the cost of "
        "a check above. Once it returns a scam verdict with sources, later hits of that pattern and language reuse them "
        "and make no call. With `RADAR_FAKE=1` no call is made.",
        "", "| Lang | Story | Verdict | ms | Sources | From |", "|---|---|---|---|---|---|", *rows, "",
    ]
    (HERE / "RADAR_LATENCY.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[4:7]))


if __name__ == "__main__":
    main()
