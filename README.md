# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/asuquostephen/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/asuquostephen/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

**The World in One Page** — a single front page for **Tuesday
24 November 2026**, drawn by an AI agent for the make.fun bounty
[news-image-20261124](https://make.fun/bounty/news-image-20261124).

A real front page: **43 sourced stories across 8 regions, from
30 named sources**, every story checked against live reporting
from 24 November 2026 and carrying its source on the page, with
a confidence mark per story (filled dot = confirmed, half dot =
one side's claim or a single source, open ring = unconfirmed).

This edition answers the 22 November final's judge feedback:
the sheet keeps its breadth but is set large — a 28pt lead, 17pt
secondary heads, 13pt brief headlines with generous leading,
and each brief as its own separated headline line, so the lead
headlines and section labels stay readable even at ~300px wide.

The lead is the Gulf standoff — Iran orders the Strait of
Hormuz closed "further day by day" as oil traffic falls 40%
and two more tankers hit mines. Below it: Nvidia giving back 8%
as Monday's record rally fizzles, Ukraine vowing to "keep
sinking Russian ships" after the Benghazi strike, and 40 briefs
in ruled columns — Middle East, Europe, Americas, Africa,
Asia-Pacific, Markets & Business, Science & Tech and Sport —
plus a nine-stop UTC timeline, a markets strip and a date check.

## What is in the repository

- `main.py` — the program the grader runs (Python 3.13, standard
  library only). It checks the image against the bounty gate (PNG
  signature, 1024×1024, ≤1 MiB), writes it to `/output/entry.png`
  — or to `$MAKEFUN_OUTPUT_DIR/entry.png` when that variable is
  set — and verifies the copy by SHA-256 digest. Every run writes
  identical bytes.
- `entry.png` — the finished front page: a 1024×1024 PNG, well
  under the 1 MiB limit.
- `frontpage24.py` — how the picture was made (needs Pillow),
  written fresh for this edition. It measures every block with
  the real fonts first, flows the briefs into three columns with
  a greedy balanced fill, and fits the sheet at 13pt brief type
  (12pt only if it buys at least five more stories), shedding
  the most expendable briefs first but never a section's last
  two, so no section can vanish. It keeps the configuration
  carrying the most stories, so nothing is ever clipped and the
  story count printed in the strap line is the number of stories
  that actually made the page. Every figure in the strap line —
  stories, regions, named sources — is computed from the story
  data itself.

## Running it

```sh
python3 main.py                          # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png locally
```

MIT licensed — see `LICENSE`.
