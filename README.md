# reddit2md

A hyper-customizable Python module for scraping Reddit posts and comments into clean Markdown, JSON, and SQLite.

---

## The Basics

There are several ways to use `reddit2md`:

**1. Direct URL Scrape** — you have a specific Reddit post URL you want right now:
```bash
python3 reddit2md.py --url "https://www.reddit.com/r/Python/comments/abc123/some_post"
```

**2. Query Scrape** — you want the top N posts from a fitlered feed matching paritular criteria:
```bash
# Top 5 posts from r/Python this week
python3 reddit2md.py --subreddit python --sort top --timeframe week --max-results 5

# New posts from r/MachineLearning, skipping anything with fewer than 100 upvotes
python3 reddit2md.py --subreddit MachineLearning --sort new --ignore-below-score 100
```

These are easy to drop into a cron job. Point `--md-output-directory` at your Obsidian vault and you're done.

**3. Named routines** — if you run the same query often, define it once in `config.yml` and call it by name:
**in your config.yaml**
```yaml
settings:
  group_by: subreddit         # organizes output into subfolders by subreddit
  max_results: 3              # default max outputs

routines:
  - name: "Obsidian Feed"
    md_output_directory: "../obsidianVault/newsfeed/reddit"
    subreddit: ["ObsidianMD", "obsidianMDmemes", "ObsidianPorn"]
    search: "automation"
    max_results: 6
    detail: LG               # deeper comment extraction (supports: XS, SM, MD, LG, XL)
```

**simple command to update your feed**
```bash
python3 reddit2md.py --routine "Obsidian Feed"
```

---

## Quick Start

### CLI
```bash
# Scrape a single post by URL or post ID
python3 reddit2md.py --url "https://www.reddit.com/r/Python/comments/abc123/post_title"
python3 reddit2md.py --url "abc123"

# Feed scrape: newest posts from a subreddit
python3 reddit2md.py --subreddit python --sort new --max-results 10

# Run a named routine from config.yml
python3 reddit2md.py --routine "my-news-feed"

# Run all routines in config.yml
python3 reddit2md.py
```

### config.yml
For routines you'll run regularly, define them in `config.yml`:

```yaml
settings:
  md_output_directory: "../../workspace/feeds/reddit"
  data_output_directory: "../../workspace/data/reddit"
  group_by: subreddit        # organizes output into subfolders by subreddit
  ignore_below_score: 50
  detail: MD

routine:
  - name: "tech-news"
    subreddit: technology
    sort: top
    timeframe: day

  - name: "ml-deep"
    subreddit: MachineLearning
    search: "transformer OR LLM"
    detail: LG               # deeper comment extraction
```

Then run `python3 reddit2md.py` to execute all routines, or `python3 reddit2md.py --routine tech-news` for one.

### Python API
All parameters work identically when calling the scraper from Python:

```python
from reddit2md.scraper import RedditScraper

scraper = RedditScraper()

# Scrape a specific post
scraper.run(target_scrape="abc123")

# Feed scrape with overrides
scraper.run(overrides={
    "subreddit": "MachineLearning",
    "search": "transformer OR LLM",
    "save_md": True,
    "save_json": True,
})

# Run a named routine from config.yml
scraper.run(routine_name="ml-deep")
```

---

## Output: The Data Triad

`reddit2md` produces up to three simultaneous outputs — toggle any combination on or off:

| Output | Flag | Best For |
|---|---|---|
| **Markdown** (`.md`) | `save_md: true` | Obsidian, PKM tools, human reading |
| **JSON** (`.json`) | `save_json: true` | LLM pipelines, raw data archives |
| **SQLite** (`.db`) | `detailed_db: true` | Headless agents, historical queries |

---

## Output Organization: `group_by`

By default, all Markdown files go into a single output directory. Use `group_by` to automatically sort them into subfolders based on any field in the post data:

```yaml
settings:
  group_by: subreddit    # → output/MarvelStudios/PostTitle_abc123.md
  # group_by: author     # → output/username/PostTitle_abc123.md
  # group_by: domain     # → output/youtube.com/PostTitle_abc123.md
  # group_by: post_flair # → output/Discussion/PostTitle_abc123.md
```

Setting `group_by` to `false` (or omitting it) puts all files in a flat directory.

---

## Querying & Filtering: Three Tiers

reddit2md works without API access, so there's some complexities under the hood surrounding the endpoints it uses. I've categorized parameters by *where* filtering happens, because it determines performance and pagination behavior.

### Tier 1: Browse endpoint (fastest)
These hit Reddit's simple, low-latency browse feed:
- **`subreddit`** — target subreddit(s). Single value or list.
- **`sort`** — `new`, `hot`, `top`, `rising`
- **`limit`** / **`max_results`** — max posts to return
- **`offset`** — skip the first N results

### Tier 2: Search endpoint
Using any of these causes reddit2md to switch to Reddit's advanced search API endpoint, which supports complex filtering but is *potentially* slower to update:
- **`search`** — Lucene-style query string (see Advanced Querying below)
- **`timeframe`** — `hour`, `day`, `week`, `month`, `year`, `all`
- **`author`** — require posts by specific user(s)
- **`domain`** — require posts linking to a specific domain (e.g., `youtube.com`)
- **`selftext`** — search within post body text
- **`title_search`** — search within post titles only
- **`flair_contains`** — match posts whose flair **contains** the given word (e.g., `flair_contains: Discussion` matches `[Weekly Discussion]` and `[Discussion Thread]`)
- **`flair`** — match posts with a **specific exact flair name** (e.g., `flair: "Weekly Discussion"`)
- **`exclude_flair`** — exclude posts carrying a specific flair
- **`nsfw_only`** — return only NSFW-flagged posts
- **`spoiler`** — return only spoiler-flagged posts

### Tier 3: Local filters (with deep pagination)
These run locally after Reddit returns the feed. When a post is rejected by a local filter, reddit2md automatically paginates deeper to fulfill your `max_results` target (up to 3 pages):
- **`ignore_below_score`** — drop posts below an upvote threshold
- **`ignore_below_upvote_ratio`** — drop posts below a ratio (e.g., `0.85`)
- **`ignore_below_comments`** — drop posts with too few comments
- **`ignore_older_than_hours`** / **`ignore_older_than_days`** — drop stale posts
- **`ignore_newer_than_hours`** / **`ignore_newer_than_days`** — drop posts that are too fresh
- **`exclude_terms`** — drop posts with specific words in their title
- **`exclude_author`** — drop posts from specific authors or bots
- **`exclude_urls`** — drop posts linking to specific domains

---

## Advanced Querying

When using the `search` parameter, reddit2md passes your query directly to Reddit's Lucene-style search engine:

| Operator | Example | Effect |
|---|---|---|
| `AND` / `OR` / `NOT` | `marvel AND NOT disney` | Boolean logic |
| `" "` (quotes) | `"spider-man"` | Exact phrase match |
| `title:` | `title:announcement` | Search post titles only |
| `site:` | `site:youtube.com` | Filter by linked domain |

---

## Customizing Output Templates

`reddit2md` uses a powerful, logic-free templating system that allows you to control exactly how your data is presented. By modifying the files in `reddit2md/templates/`, you can adjust frontmatter keys, body styling, and nesting for:

- **`post.template`**: The full page layout (Post Body + Frontmatter)
- **`comment.template`**: How individual comments and their replies are structured
- **`update.template`**: The formatting of the "Updated Comments" block during rescrapes

Templates use a simple `${variable}` syntax. For a full list of available variables, see the [Configuration Reference](README_config_guide.md#markdown-templates).

---

## Post Maturity & Rescraping (Optional Features)

Scraping a thread soon after it's posted often misses the best comment sections. Use these three parameters together to implement a maturity window:

```yaml
subreddit: marvelstudios
timeframe: day                 # Reddit returns posts from past 24h
ignore_newer_than_hours: 20    # Drop anything under 20h old (too fresh)
rescrape_newer_than_hours: 24  # Queue posts under 24h for a follow-up scrape
```

What happens:
1. Reddit returns posts from the last 24 hours.
2. Posts under 20 hours old are discarded (local filter, triggers deep pagination).
3. Posts in the 20–24h window are scraped and flagged for rescraping.
4. On the next run, those posts are revisited and the mature comment section is appended to the Markdown file.

---

## Extended Reference

- **[Configuration Reference](README_config_guide.md)** — complete parameter encyclopedia with all 30+ options, CLI flag equivalents, and detailed examples.

