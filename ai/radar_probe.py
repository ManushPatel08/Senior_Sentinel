"""Scam radar probe: one Claude call per story, with web search, returning a structured verdict with its
sources. Records time, sources and usage per call in ai/eval/RADAR_PROBE.md.

    python -m ai.radar_probe                      # the three stories in English, grandparent in es and hi
    python -m ai.radar_probe --model claude-opus-5-5 --effort medium

The request: web search limited to the radar's domains, the verdict through the strict report_verdict tool,
sources from the search results it names (the same tool and parsing as policy.scamcheck).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import time
from pathlib import Path

import anthropic

from common import claude
from policy.scamcheck import DOMAINS, VERDICT_TOOL, RadarError, _parse

HERE = Path(__file__).resolve().parent
INSTRUCTIONS = (
    "You protect an older adult from scams. Use the facts given and search the web, then call report_verdict once. "
    "'say' is in the shopper's language, two short sentences, warm, never a score, one clear action. Never blame her. "
    "In source_urls, list only search results that report this scam."
)
STORIES = [
    ("grandparent", "en",
     "My grandson Alex just called crying. He's in jail after a car accident and needs $2,000 for bail today. "
     "His voice sounded a little different. He begged me not to tell his mom.",
     "Trusted contacts on file: Alex (grandson) +1-404-555-0187. Caller number: unknown."),
    ("power_company", "en",
     "Peachtree Power called and said my power will be cut off tonight unless I pay $480 right away with gift cards.",
     "Peachtree Power account: balance $0.00, last bill $96.20 paid on Sep 12, autopay on."),
    ("tech_support", "en",
     "A pop-up said my computer has a virus and gave a Microsoft number. The man says I was overcharged and "
     "needs me to install AnyDesk so he can refund me.",
     "No recent Microsoft orders. Recent orders: groceries on Sep 24."),
    ("grandparent", "es",
     "Mi nieto Alex llamó llorando, está en la cárcel y necesita 2000 dólares para la fianza hoy. "
     "Me pidió que no le diga a su mamá.",
     "Contactos de confianza: Alex (nieto) +1-404-555-0187."),
    ("grandparent", "hi",
     "मेरे पोते एलेक्स का फोन आया, वो रो रहा था। वो जेल में है और आज ज़मानत के लिए 2000 डॉलर चाहिए। "
     "उसने कहा अपनी मम्मी को मत बताना।",
     "भरोसेमंद संपर्क: एलेक्स (पोता) +1-404-555-0187."),
]


def request_body(story: str, lang: str, facts: str, model: str, effort: str) -> dict:
    return dict(
        model=model,
        max_tokens=16000,
        system=INSTRUCTIONS,
        messages=[{"role": "user", "content": f"Language: {lang}. Story: {story} Facts: {facts}"}],
        tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 3, "allowed_domains": DOMAINS},
               VERDICT_TOOL],
        output_config={"effort": effort},
        **claude.FALLBACK,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=claude.MODEL)
    ap.add_argument("--effort", default="low", help="low, medium, high, xhigh or max")
    ap.add_argument("--timeout", type=float, default=30.0)
    args = ap.parse_args()

    client = claude.client()
    out = ["# Scam radar probe", "",
           f"Run {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} on `{args.model}` (effort {args.effort}) with "
           f"`web_search` limited to {', '.join(DOMAINS)}. The verdict comes through the strict `report_verdict` tool; "
           "sources are the search results it names.", "",
           "| Story | Lang | ms | Verdict | Pattern | Actions | Sources | Searches | Tokens in/out |",
           "|---|---|---|---|---|---|---|---|---|"]
    details = []
    for name, lang, story, facts in STORIES:
        start = time.perf_counter()
        try:
            resp = client.beta.messages.create(**request_body(story, lang, facts, args.model, args.effort),
                                               timeout=args.timeout)
            ms = (time.perf_counter() - start) * 1000
            v = _parse(resp)
        except anthropic.APIError as e:
            ms = (time.perf_counter() - start) * 1000
            out.append(f"| {name} | {lang} | {ms:.0f} | {type(e).__name__} | | | | | |")
            details += [f"### {name} ({lang}): {type(e).__name__}", "", "```", str(e)[:800], "```", ""]
            print(name, lang, type(e).__name__, str(e)[:300])
            continue
        except RadarError as e:
            out.append(f"| {name} | {lang} | {ms:.0f} | {e} | | | | | |")
            print(name, lang, e)
            continue
        u = v["usage"]
        out.append(f"| {name} | {lang} | {ms:.0f} | {v['verdict']} | {v.get('pattern', '')} | "
                   f"{', '.join(v.get('actions') or [])} | {len(v['sources'])} | {u['web_searches']} | "
                   f"{u['input_tokens'] + u['cache_read_input_tokens'] + u['cache_creation_input_tokens']}/{u['output_tokens']} |")
        details += [f"### {name} ({lang}), {ms:.0f} ms", "", f"- **say**: {v.get('say', '')}",
                    f"- **reported recently**: {v.get('reported_recently', '')}",
                    f"- **usage**: `{json.dumps(u)}`"]
        details += [f"- source: [{s['title'] or s['url']}]({s['url']})" for s in v["sources"]] + [""]
        print(f"{name:14} {lang} {ms:6.0f} ms  {v['verdict']}  sources={len(v['sources'])}  searches={u['web_searches']}")
    (HERE / "eval" / "RADAR_PROBE.md").write_text("\n".join(out + [""] + details), encoding="utf-8")


if __name__ == "__main__":
    main()
