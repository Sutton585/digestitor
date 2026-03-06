# The Digestitor Protocol: Architectural Blueprint for Scraper Modules

This document defines the strict architectural and philosophical standards for the "Digestitor" suite of scrapers. Whether building a module for Reddit, HackerNews, Twitter, or any other platform, **every scraper must adhere to this blueprint.** 

This ensures that the overarching orchestration layer can interact with any module predictably, and that the end-user experiences a unified, highly controllable knowledge-gathering pipeline.

---

## 1. Core Philosophy: The "Living Knowledge Base"

Digestitor modules are not simple data dumpers; they are **Knowledge Accumulators** designed for professional note-taking environments like Obsidian.

*   **Markdown is the Ultimate Authority:** The file system is the primary source of truth. If a user manually edits a note's front-matter (e.g., changing its categorization or deleting a scheduled re-scrape time), the scraper MUST detect and respect that change on its next run.
*   **Cumulative Knowledge (Living Notes):** Scrapers do not blindly overwrite files and history. When an entity is re-scraped (due to an update or reaching "maturity"), the system updates the metadata but **appends** the new content (e.g., new comments) to the end of the file. This creates a chronological record of an evolving discussion.
*   **Safe Vault Coexistence:** Modules must assume they are writing into a densely populated, human-curated directory. A scraper must surgically identify its "owned" files by checking for a specific ID in the front-matter (e.g., `post_id`). It must never touch or alter unrelated files.
*   **Zero-Dependency Graceful Degradation:** Modules should strive to operate using only the Python Standard Library to ensure maximum portability. However, they must gracefully detect and utilize superior external libraries (like `requests` over `urllib`) if present, to handle advanced anti-bot measures (e.g., 403 blocks).

---

## 2. The Trinity of Interfaces

Every scraper must support three distinct modes of interaction. There must be **100% feature parity** across all three modes. If a setting exists, it must be accessible everywhere.

### A. The Configuration File (`config.json`)
Used for persistent, automated workflows. It must contain:
-   `global_defaults`: Baseline settings applied to all executions.
-   `jobs`: A sequence of specific scrape tasks. 

### B. The Command Line Interface (CLI)
Used for ad-hoc exploration, testing, and cron-job orchestration.
-   Must support targeting a specific origin entity (e.g., `--subreddit news`) for one-off scrape jobs of entities not in the config.
-   Must support explicit, typed overrides for every single parameter (e.g., `--limit 5`, `--detail XL`, `--save-json False`).

### C. The Python Resource (Importable Module)
Used for higher-level orchestration (e.g., an LLM agent triggering a scrape).
-   The main orchestrator class must accept an `overrides` dictionary in its `run()` method to bypass any global or job-specific defaults programmatically.

**Precedence Order:** Direct Overrides (CLI/Python) > Job-Specific Config > Global Defaults Config.

---

## 3. The Execution Architecture: The "Job" Model

Modules must not use a simple "lookup" model (e.g., "Find the config for X and run it once"). Instead, they operate on a **Job Queue**.

*   **Sequential Execution:** The `config.json` defines an array of `jobs`. The module iterates through this list and executes them in order.
*   **Multi-Faceted Targeting:** A user must be able to define multiple jobs for the exact same origin entity, each with different settings.

---

## 4. Behavioral Toggles & Limits
Scrapers must allow users to suppress side effects or limit footprints:
- **`save_json` (Boolean):** Whether to persist the sanitized JSON data after processing.
- **`update_log` (Boolean):** Whether to append the run results to the human-readable Markdown log.
- **`max_db_records` (Integer):** Maximum number of records to keep in the SQLite index. Older records are pruned to keep the database size manageable.
- **`min_post_age_hours` (Integer):** Setting this to `0` must disable all maturity/re-scraping logic, making every scrape final.

---

## 5. State Reconciliation Flow
To maintain the Source of Truth, every module must perform a surgical reconciliation on startup. This ensures the SQLite cache reflects the current state of the filesystem.

1. Scan Directory: Recursively scan the output_directory for all .md files.
2. Verify Ownership: For each file, parse the front-matter. If the post_id field is missing, skip the file entirely (it belongs to the user, not the scraper).
3. Conflict Resolution: Compare the flair and rescrape_after values in the Markdown file against the SQLite database. If they differ, the Markdown file wins—update the database record immediately.
4. Orphan Pruning: Check for records in the SQLite database where the corresponding Markdown file no longer exists on disk. Delete these records from the database (the user has "forgotten" the post).

---

## 6. The Data Pipeline & State Management

Data flows through three distinct layers, each serving a specific architectural purpose.

### Layer 1: JSON Archive (The Backup)
*   **Path:** `data_directory/json/`
*   **Purpose:** Stores the sanitized, high-signal JSON data (never the raw, messy API response).
*   **Function:** Serves as an offline backup. If the user accidentally deletes their Markdown notes or the SQLite database, the system can rebuild the entire vault from these JSON files without hitting the external API rate limits.

### Layer 2: SQLite Index (The Memory Cache)
*   **Path:** `data_directory/database.db`
*   **Purpose:** A high-speed tracking index. It remembers what has been scraped, when it was scraped, and when it is scheduled to be re-scraped. This index is considered a cache and should be rebuildable from the Markdown files.
*   **Function:** It is strictly treated as a **Self-Healing Cache**. It must never be the ultimate source of truth.
*   **Pruning:** The database footprint is managed by a `max_db_records` integer setting.

### Layer 3: Markdown Notes (The Final Product)
*   **Path:** `output_directory/`
*   **Purpose:** The human-readable and LLM-parsable final output.
*   **Function:** As detailed in the Core Philosophy, these are living documents that dictate state back to the SQLite cache during reconciliation.

---

## 7. Anatomy of a Scrape: Maturity & Internal Linking

### Context vs. Freshness (Maturity Logic)
To balance the need for immediate news with the desire for deep context, modules must implement Maturity Logic.
1.  **Fresh Scrape:** A new post is scraped immediately but marked with a future `rescrape_after` timestamp in the DB and the Markdown front-matter.
2.  **Maturation:** Once that time passes, the module re-fetches the thread, updates the metadata (e.g., new score/upvotes), and *appends* the finalized conversation to the file.
3.  **Disablement:** Setting `min_post_age_hours` to `0` must disable this entirely, making every scrape final.

### Automatic Internal Linking (The Graph)
Where applicable, scrapers should convert external URLs pointing to the origin platform into internal Markdown links (e.g., `[[Origin_ID]]`). This allows the generated files to form a cohesive, interconnected graph within tools like Obsidian.

---

## 8. Standard Metadata & Nomenclature

Consistency across modules is mandatory. Front-matter fields and database columns must use standardized naming:

*   **`post_id`**: The unique, immutable identifier from the source platform.
*   **`flair`**: (Formerly `project`). Used to categorize the post based on source metadata (e.g., Reddit Flair).
*   **`post_link`**: (Formerly `story_link`). Used to link to related internal notes or external URLs.
*   **`rescrape_after`**: The ISO timestamp dictating when the "Living Note" should be updated.

---

## 9. File & Folder Rules

### Filename Pattern
Filenames must be completely decoupled from volatile metadata (like `flair` or `title`).
*   **Standard:** `[OriginEntity]_[post_id].md` (e.g., `Python_1rm32fu.md`).

### Automated Folder Organization
Modules must support a `generate_subreddit_folders` (or equivalent `generate_folders`) boolean toggle.
*   **True:** Files are sorted into subdirectories based on their origin (e.g., `output_directory/OriginEntity/File.md`).
*   **False:** All files are placed directly in the root of the `output_directory`.

### Debug Mode Isolation (CRITICAL)
The `debug` flag is a hard safety override.
*   **When True:** The module **MUST** completely ignore all user-configured `output_directory`, `data_directory`, and `scrape_log_path` settings. It must force all operations into a local `./data/` folder relative to the script. This guarantees that a developer can test the scraper without accidentally writing files into a user's live production vault.

---

## 10. Required Class Structure

To maintain code readability and modularity, every new scraper must be divided into these five "Buckets" (Classes). This ensures that any developer in the suite can immediately understand and maintain any module.

### 1. The Brain (`Config`)
Manages the loading of `config.json`, the hierarchy of defaults, and the surgical merging of job-specific and CLI overrides. Its only job is to determine the "active settings" for a run.

### 2. The Hands (`Client`)
Handles all external HTTP requests. It must encapsulate API logic, pagination, and anti-bot measures. 
**Mandatory Pattern:** To ensure portability, the Client must follow this "Standard Library First" pattern for its fetch operations:

```python
try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    from urllib import request, error
    _REQUESTS_AVAILABLE = False

# Traffic must be routed through a private helper that handles the toggle:
def _fetch_url(self, url, headers):
    if _REQUESTS_AVAILABLE:
        # Use requests for robust fetching (bypassing 403s)
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.content
    else:
        # Fallback to standard library urllib
        req = request.Request(url, headers=headers)
        with request.urlopen(req) as response:
            return response.read()
```

### 3. The Translator (`Processor`)
The pure logic layer. It converts messy raw API responses into sanitized internal JSON, handles internal link resolution (`[[Obsidian_Links]]`), and generates the final Markdown formatting. It should not perform any I/O operations (writing files).

### 4. The Memory (`DatabaseManager`)
Encapsulates all SQLite operations. It acts as the high-speed state-tracker, managing the scheduled re-scrapes (Maturity) and the pruning of old records to keep the cache footprint small.

### 5. The Boss (`Scraper`)
The main orchestrator. It does not do the "grunt work" itself; it initializes the other four buckets and manages the flow: starting the reconciliation, iterating through the Job queue, and triggering the final Scrape Log export.

