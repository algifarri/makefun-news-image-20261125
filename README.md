# The World in One Day — Wednesday 25 November 2026

[![make.fun bounty](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![make.fun rank](https://make.fun/badge/news-image-20261125/algifarri/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![make.fun reward](https://make.fun/badge/news-image-20261125/algifarri/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

A broadsheet poster summing up the world's news of Wednesday 25 November 2026 in a single 1024x1024 image, drawn entirely in pure-stdlib Python — its own 5x7 bitmap font, its own shape rasteriser, its own PNG writer. No network, no randomness, fully deterministic.

## The day's stories

- **Top story — Gulf of Finland:** Zelenskiy confirms Ukraine hit a Russian ship; Norway urges caution.
- **Poland:** NATO sends early-warning jets after Russian missiles landed there.
- **Strait of Hormuz:** three oil tankers hit by mines.
- **The war in Ukraine:** 700,000 Russian soldiers killed, a new analysis finds.
- **Washington:** Trump awards Rudy Giuliani the Medal of Freedom.
- **In brief:** Huawei convicted in a US trial; the CIA and ODNI hit by a cyber breach; England beat Australia by 8 wickets in the 2nd T20I; BJP–Akali Dal agree a Punjab 2027 alliance.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `entry.png` (1024x1024, under 1 MiB). Run it twice and the bytes are identical.

## License

MIT — see `LICENSE`.
