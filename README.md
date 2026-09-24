# 77 GHz Automotive Radar — Design Notes

Reference pages for a 76–81 GHz FMCW ADAS radar.

- [docs/radar77-signal-chain.html](docs/radar77-signal-chain.html) — architecture and typical specs from antenna, Tx/LO/Rx front end, IF and ADC to digital processing, with a chirp and link-budget calculator.
- [docs/radar77-bist-loopback.html](docs/radar77-bist-loopback.html) — on-chip BIST and loopback: stimulus generation, on-chip measurement, trim/calibration feedback, and instrument-free production test.
- [docs/radar77-continuity.html](docs/radar77-continuity.html) — open/short and contact-resistance (Cres) test.
- [docs/radar77-dft-stress.html](docs/radar77-dft-stress.html) — digital DFT, scan, memory/logic BIST, stress screening and qualification.

Published with GitHub Pages: https://sinliongtoo.github.io/project_claude_circuit/

## Editing

After changing any page, run `python tools/build.py` (needs `beautifulsoup4`). It refreshes the shared search component, regenerates the glossary (`tools/glossary.py` holds the terms), renumbers sections, and rebuilds the cross-page search index embedded in each page.

Figures are typical engineering values for early trade-offs; verify against your chosen MMIC's datasheet and current regulations.
