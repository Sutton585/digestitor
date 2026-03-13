# Configuration Reference

Complete parameter encyclopedia for `reddit2md`. All parameters work identically across all three interfaces:
- **`config.yml`** — use snake_case keys (e.g., `ignore_below_score`)
- **CLI flags** — use dash-case (e.g., `--ignore-below-score`)
- **Python overrides** — use snake_case dict keys (e.g., `{"ignore_below_score": 100}`)

---

## System & Output Settings

### `md_output_directory`
Path where Markdown files are written. Relative paths are resolved from the working directory.

### `data_output_directory`
Path where JSON files and the SQLite database are written.

### `md_log`
Path to the Markdown scrape log file. Set `enable_md_log: false` to disable it.

### `save_md`
`true` (default) / `false` — Toggle markdown file generation.

### `save_json`
`true` (default) / `false` — Toggle JSON file generation.

### `detailed_db`
`true` / `false` — When enabled, the SQLite database expands to store the full JSON payload per post (enables complex historical queries without touching files). Automatically enabled if `save_json` is `false` but scraping is active.

### `track`
`true` (default) / `false` — Set to `false` to disable all SQLite DB reads and writes entirely.

### `db_limit`
Max number of records to retain in the SQLite DB before pruning. The oldest records (and their associated JSON files) are deleted first. Default: `1000`.

### `detail`
Comment depth preset. Controls how many comments and replies are extracted:
`XS` (none) → `SM` (top-level only) → `MD` (default) → `LG` → `XL` (full tree)

### `verbose`
Console output level:
- `0` — Errors only
- `1` — Progress summaries
- `2` — Full debug output (default)

### `group_by`
Automatically organizes markdown output into subfolders based on a field in the post data. Can be set to any field name in the post JSON:

```yaml
group_by: subreddit    # → output/MarvelStudios/PostTitle_abc123.md
group_by: author       # → output/username/PostTitle_abc123.md
group_by: domain       # → output/youtube.com/PostTitle_abc123.md
group_by: post_flair   # → output/Discussion/PostTitle_abc123.md
```

Set to `false` (or omit) for a flat output directory.

### `max_results`
Maximum number of posts to process per routine run. Default: `8`.

### `offset`
Skip the first N results from the Reddit feed before counting toward `max_results`.

---

## Routine Configuration

Routines are defined in `config.yml` under the `routine:` key. Each routine inherits all `settings:` values and can override any of them:

```yaml
settings:
  max_results: 10
  sort: new

routine:
  - name: "tech-top"
    subreddit: technology
    sort: top              # overrides settings sort
    timeframe: day

  - name: "ml-search"
    subreddit: MachineLearning
    search: "transformer OR LLM"
    max_results: 5         # overrides settings max_results
```

**`name`**: Optional. Gives the routine a name, shown in console output and used with `--routine`.

**`subreddit`** / **`subreddits`**: The target subreddit(s). Both singular and plural are accepted:
```yaml
subreddit: Python
subreddits:
  - Python
  - MachineLearning
```

---

## Tier 1: Browse Parameters

These use Reddit's fast, low-latency browse endpoint.

### `sort`
Feed sort order: `new` (default), `hot`, `top`, `rising`

> [!NOTE]
> Using `relevance` or `comments` as sort values automatically forces the search endpoint.

### `timeframe`
Restricts results to a time window: `hour`, `day`, `week`, `month`, `year`, `all`.
> Forces the search endpoint when used.

---

## Tier 2: Search Parameters

Using any of these causes reddit2md to switch to Reddit's advanced search API (`/search.rss`), which is more powerful but slower.

### `search`
Freeform Lucene-style query string. Passed directly to Reddit's search. See [Advanced Querying](#advanced-querying).

### `author`
Require posts submitted by a specific user or list of users.

### `domain`
Require posts that link to a specific domain (e.g., `domain: youtube.com`).

### `selftext`
Search within post body text (text posts only).

### `title_search`
Search within post titles only.

### `flair_contains`
Match posts whose flair **contains** the given word. Case-insensitive word match.

```yaml
flair_contains: Discussion   # matches [Weekly Discussion], [Discussion Thread], [Discussion]
flair_contains:
  - Discussion
  - News               # OR logic — matches either word
```

> [!NOTE]
> `flair_contains` uses Reddit's `flair:` search operator, which matches if the given word appears anywhere in the flair text. It is **not** a substring match — `flair_contains: Disc` will **not** match `[Discussion]`.

### `flair`
Match posts with an **exact, complete flair name**. Most useful with `sort: new` (uses the fast browse endpoint `f=flair_name:`), otherwise uses the search endpoint.

```yaml
flair: "Weekly Discussion"    # matches only posts with exactly this flair
```

### `exclude_flair`
Exclude posts carrying a specific flair. Accepts a single value or list.

### `nsfw_only`
`true` / `false` — Return only NSFW-flagged posts.

### `spoiler`
`true` / `false` — Return only spoiler-flagged posts.

### `allow_nsfw`
`true` / `false` — When `false` (default), NSFW posts are filtered out at the URL level.

---

## Tier 3: Local Filters

These run locally after Reddit returns the feed. When a post is rejected, reddit2md paginates deeper to fulfill `max_results` (up to 3 pages deep before giving up).

### `ignore_below_score`
Drop posts with fewer upvotes than this threshold.

### `ignore_below_upvote_ratio`
Drop posts with a lower upvote percentage (e.g., `0.85` = 85%). Useful for filtering out controversial posts.

### `ignore_below_comments`
Drop posts with fewer comments than this threshold.

### `ignore_older_than_hours` / `ignore_older_than_days`
Drop posts older than this age.

### `ignore_newer_than_hours` / `ignore_newer_than_days`
Drop posts younger than this age. Useful for waiting until a post has accumulated discussion.

### `exclude_terms`
Drop posts whose title contains any of the specified keywords. Accepts a single string or list.

### `exclude_author`
Drop posts from specific users (bots, automods, etc.). Accepts a single string or list.

### `exclude_urls`
Drop posts whose source URL is in this list (does not affect extracting links from the post body).

### `ignore_urls`
Removes specific URLs from the `post_links` array inside each output file. Does **not** filter out the post itself.

---

## Rescraping & Maturity Logic

### `rescrape_newer_than_hours` / `rescrape_newer_than_days`
The primary maturity controller. Posts younger than this threshold are scraped but flagged in the DB to be revisited on a future run once they've matured.

**The full maturity workflow:**

```yaml
subreddit: marvelstudios
timeframe: day                    # Reddit returns posts from past 24h
ignore_newer_than_hours: 20       # Discard posts under 20h old (too fresh for discussion)
rescrape_newer_than_hours: 24     # Everything that survives gets a rescrape mark
```

1. Reddit returns posts from the last 24 hours.
2. Posts under 20h old are discarded — not scraped, not tracked.
3. Posts in the 20–24h window are scraped and queued for rescraping.
4. On the next run, mature posts are revisited and their updated comments are appended to the Markdown file.

> [!TIP]
> Set `rescrape_newer_than_hours: 0` or omit it entirely if you don't need post maturity tracking.

---

## Advanced Querying

The `search` parameter supports Reddit's full Lucene-style syntax:

| Operator | Example | Effect |
|---|---|---|
| `AND` / `OR` / `NOT` | `marvel AND NOT disney` | Boolean logic |
| `" "` (quotes) | `"spider-man"` | Exact phrase match |
| `title:` | `title:announcement` | Search post titles only |
| `site:` | `site:youtube.com` | Filter by linked domain |
| `selftext:` | `selftext:tutorial` | Search post body text |
| `author:` | `author:spez` | Filter by author |

---

## System Fields (Read-Only)

These fields are automatically populated in the JSON output and SQLite database. They are not user-configurable.

### `ingestion_history`
A JSON array logging every query that has ever touched this post. Each entry contains:
- `type`: `"initial"` (first scrape), `"rescrape"` (re-scraped after maturity), or `"hit"` (query returned this post but it didn't need re-scraping)
- `timestamp`: UTC ISO timestamp
- `query`: The full configuration parameters used for that run

This provides a full audit trail for understanding which queries produce which content.

---

## Aliases (Backward Compatibility)

| Config key | Canonical key | Notes |
|---|---|---|
| `subreddits` | `subreddit` | Natural plural form, fully supported |
| `label` | `flair_contains` | Old partial flair param |
| `flair_exact`, `label_exact`, `exact_flair` | `flair` | Old exact flair param |
| `exclude_label` | `exclude_flair` | Old exclude flair param |
| `query` | `search` | Old search param alias |
| `exclude_authors` | `exclude_author` | Plural alias |
| `max_age_hours` | `ignore_older_than_hours` | Old age filter alias |
| `min_age_hours` | `ignore_newer_than_hours` | Old freshness filter alias |

---

## Markdown Templates

`reddit2md` allows you to customize the structural output of your Markdown files using a logic-free template system based on Python's `string.Template`.

### Template Files
Located in `reddit2md/templates/`:
- **`post.template`**: Dictates the main Markdown file (Frontmatter + Post Body).
- **`comment.template`**: Dictates the layout of a single comment and its recursive tree of replies. 
- **`update.template`**: Dictates the block appended to a post when it is rescraped for more discussion.

### Syntax
Templates use the `${variable_name}` placeholder syntax. If a variable is missing or empty, the placeholder is safely removed during rendering.

### Available Variables

#### `post.template`
| Variable | Description |
|---|---|
| `${post_id}` | Reddit's unique alphanumeric ID for the thread |
| `${title}` | The post title |
| `${selftext}` | The body content of the post |
| `${poster}` | The author's username |
| `${source}` | The subreddit community name |
| `${post_flair}` | The post's flair/label |
| `${score}` | Net upvotes |
| `${upvote_ratio}` | Percentage of upvotes (e.g., `0.95`) |
| `${num_comments}` | Total comment count |
| `${domain}` | The out-link domain (e.g., `github.com`) |
| `${permalink}` | The relative URL path to the Reddit thread |
| `${is_nsfw}` | `True` or `False` |
| `${over_18}` | `True` or `False` (alias for maturity) |
| `${date_created}` | Submission date (`YYYY-MM-DD HH:MM`) |
| `${date_scraped}` | Script execution date (`YYYY-MM-DD HH:MM`) |
| `${comment_section}` | The macro where all comments are rendered |
| `${update_section}` | The macro where maturity update blocks are placed |
| `${rescrape_after}` | The frontmatter field for maturity tracking |
| `${post_links}` | A list of resolved Obsidian internal links or external URLs |

#### `comment.template`
| Variable | Description |
|---|---|
| `${author}` | The comment author |
| `${score}` | Net upvotes for the comment |
| `${body}` | The comment text |
| `${indent}` | Automatically handles tab spacing for matching thread depth |
| `${replies}` | The macro where child comments are recursively rendered |

#### `update.template`
| Variable | Description |
|---|---|
| `${update_timestamp}` | The date/time of the rescrape |
| `${comments}` | The entire new comment tree block |
