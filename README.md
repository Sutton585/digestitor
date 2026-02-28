# Digestitor: The Reddit to Markdown Digestor
Digestitor is a professional-grade Reddit scraper designed for high-signal knowledge management. It transforms transient Reddit discussions into permanent, well-structured Markdown notes for use in Obsidian vaults, AI-automated workflows, and personalized daily digests.

Whether you are building a research database, feeding an AI agent, or just keeping up with specific subreddits, Digestitor provides the granularity and control needed for a high-quality data pipeline. It requires no external Python libraries, relying entirely on the Python standard library for maximum portability and security.

## System Overview and Core Logic
Digestitor operates on a hierarchical model where data flows from Reddit's RSS and JSON APIs into local structured storage. The system is designed to be resilient, allowing users to manage their data directly through the file system. It maintains a local SQLite database that acts as a high-speed index, but the ultimate authority always rests with the Markdown files on your disk.

### The Source of Truth and Data Integrity
The system follows a strict authority chain to resolve conflicts and ensure your edits are preserved. Individual Markdown files in your output directory hold the highest authority. If you modify the front-matter of a note—such as changing its project name or removing a scheduled re-scrape timestamp—Digestitor will detect these changes during its next run and update its internal database to match. 

If you delete a Markdown file, the system interprets this as a request to reset that post. It will purge the record from the database and the JSON archive, making the post eligible for a fresh scrape if it appears in the feed again. This allows for intuitive, no-code management of your scraped library.

### Intelligent Re-scraping and Maturity
Reddit threads are often most valuable once they have had time to "mature" with high-quality comments. Digestitor includes logic to handle early scrapes of new posts. If a post is scraped within a configurable time window (defaulting to 12 hours) of its creation, the system calculates a maturity timestamp and schedules a re-scrape. On the subsequent run after that timestamp has passed, Digestitor will fetch the updated thread, capturing the full depth of the conversation.

## Comment Detail Presets
The system provides several presets to control the exact volume and depth of comments captured. This allows you to balance file size against the depth of the discussion.
#### XS Level
The XS level captures the top 3 top-level comments with 0 replies. This is ideal for high-volume subreddits where you only want the most critical initial reactions.
#### SM Level
The SM level captures the top 5 top-level comments and includes up to 1 reply for each. It provides a brief sense of the conversation without filling the note with deep threads.
#### MD Level
The default MD setting captures the top 8 top-level comments and includes up to 2 replies for each. This is the recommended balance for most users.
#### LG Level
The LG level is designed for deeper research. It captures the top 10 top-level comments, up to 3 replies for each of those (Level 2), and up to 1 sub-reply for those (Level 3). This captures a significant portion of the most active discussions.
#### XL Level
The XL level is a special mode that removes all limits. It recursively captures every single comment and reply available in the thread, providing a complete and total archive of the discussion.

## Comprehensive Configuration Guide
Every aspect of Digestitor can be controlled through the config file, the command line, or as a Python dependency.
### Post Limit
The post limit setting determines the maximum number of new threads Digestitor will attempt to fetch from a subreddit's feed during a single run. 
- In the config file, use "post_limit".
- On the CLI, use --limit. 
- In Python, pass 'post_limit' in the overrides dictionary.
### Minimum Score
The minimum score setting acts as a quality filter. Any post with a score lower than this threshold will be skipped entirely. 
- In the config file, use "min_score". 
- On the CLI, use --min-score. 
- In Python, pass 'min_score' in the overrides dictionary.
### Comment Detail
The comment detail setting selects one of the presets (XS, SM, MD, LG, XL) to control comment depth. 
- In the config file, use "comment_detail". 
- On the CLI, use --detail.
- In Python, pass 'comment_detail' in the overrides dictionary.
### Reddit Sort Method
This setting controls how Digestitor requests the feed from Reddit. You can choose from new, hot, top, or rising. 
- In the config file, use "sort". 
- On the CLI, use --sort. 
- In Python, pass 'sort' in the overrides dictionary.
### Minimum Post Age Hours
This determines the window of time a post must exist before it is considered mature. Posts newer than this will be scheduled for a re-scrape. 
- In the config file, use "min_post_age_hours". 
- On the CLI, use --age. 
- In Python, pass 'min_post_age_hours' in the overrides dictionary.
### Filter Keywords
This is a list of case-insensitive keywords. If any of these words appear in a post's title, the post will be skipped. 
- In the config file, use "filter_keywords" as a JSON list. 
- On the CLI, use --filter with a comma-separated string. 
- In Python, pass 'filter_keywords' as a list.
### URL Blacklist
The URL blacklist prevents specific domains or URL fragments from being included in the story_link metadata of your notes. 
- In the config file, use "url_blacklist" as a JSON list. 
- On the CLI, use --blacklist with a comma-separated string. 
- In Python, pass 'url_blacklist' as a list.
### Debug Mode
Debug mode is a safety toggle that redirects all output into your local data directory. When debug is enabled, the markdown folder and the scrape log are placed inside the data directory instead of your live directory or Obsidian Vault, preventing test runs from polluting your actual records. 
- In the config file, use "debug". 
- On the CLI, use --debug. 
- In Python, set debug=True when initializing the RedditScraper class.
### Data Directory
The data directory is the primary storage hub for Digestitor. It contains the SQLite database file (database.db) and the folder for structured JSON archives (json). 
- In the config file, use "data_directory". 
- On the CLI, use --data-dir.
- In Python, pass 'data_directory' in the overrides dictionary.
### Output Directory
This is the file system path where your generated Markdown notes will be saved during normal (non-debug) runs.
- In the config file, use "output_directory". 
- On the CLI, use --output-dir. 
- In Python, pass 'output_directory' in the overrides dictionary.
### Scrape Log Path
This setting defines the path for the human-readable Markdown dashboard that summarizes your scrape history. 
- In the config file, use "scrape_log_path". 
- On the CLI, use --log-path.
- In Python, pass 'scrape_log_path' in the overrides dictionary.

## Implementation Examples

### Using the Command Line Interface
The CLI is the most common way to use Digestitor. You can run all configured subreddits by calling the script with no arguments. To scrape any subreddit on the fly, even if it is not in your config, use the --source argument. For example:
```bash
python digestitor.py --source Python --limit 5 --detail XL --sort top --age 24
```

### Using as a Python Dependency
You can import the RedditScraper class into your own projects. This is ideal for building custom AI agents that need fresh Reddit data.
```python
from digestitor import RedditScraper

scraper = RedditScraper(config_path="config.json")
scraper.run(source_name="Python", overrides={'post_limit': 5, 'comment_detail': 'XL'})
```

### Using the Configuration File
The config.json file allows you to set global defaults and then override them for specific subreddits. This is the best way to manage a large list of sources for a daily digest.
```json
{
    "global_defaults": {
        "output_directory": "My Vault/Reddit",
        "min_score": 50,
        "data_directory": "data"
    },
    "sources": [
        { 
            "name": "Python", 
            "sort": "top" 
        },
        { 
            "name": "Obsidian", 
            "comment_detail": "XL" 
        }
    ]
}
```

## Directory Structure and Files
Digestitor organizes its data into three main components. The markdown folder contains the notes you see in your live directory (ie. Obsidian). The json folder inside the data directory contains the structured data used by the system and AI agents. The database.db file inside the data directory acts as the high-speed index. Finally, the Scrape Log.md file provides a more human-readable record showing the status of every post, including which ones are currently maturing and when they are scheduled for their final re-scrape.
## Installation and First Run
To get started, clone the repository to your local machine. Since Digestitor uses only the Python standard library, you do not need to install any external packages. Simply run python digestitor.py in your terminal. On the first run, if no config.json is found, the program will create a template for you. You can then edit this file to add your preferred subreddits and customize your settings.
