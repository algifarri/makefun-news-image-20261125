# makefun-news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/algifarri/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/algifarri/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A single-page newspaper poster that sums up Wednesday 25 November 2026:
Zelenskiy confirms Ukraine hit a Russian ship in the Gulf of Finland
(Norway urges caution), NATO sends early-warning jets to Poland after
Russian missiles landed there, three oil tankers are hit by mines in the
Strait of Hormuz, a new analysis puts the Russian war dead past 700,000,
Trump awards Rudy Giuliani the Medal of Freedom, and four items in brief.
The picture is drawn from scratch at run time — no stock photo, no
downloaded asset, no network at all.

## How it is drawn

`main.py` is a small pure-stdlib Python program. It carries its own
5×7 bitmap letterface, a tiny rasteriser (rectangles, discs, triangles,
lines), and a hand-rolled PNG writer built on `zlib` and `struct`. Every
run produces the exact same bytes, because nothing in the program reads
the clock, the network, or any random source.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png`, a 1024×1024 PNG under 1 MiB.

---

<sub>Entered on [make.fun](https://make.fun/?ref=ajkq5baq&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
