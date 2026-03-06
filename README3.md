# Mapping: Original README.md to Optimized README2.md

This document provides a line-by-line accounting of where information from the original `README.md` was moved or how it was refined in the new structured `README2.md`.

---

## [ORIGINAL INTRO] (Lines 1-4)
> # Digestitor: The Reddit to Markdown Digestor
> Digestitor is a professional-grade Reddit scraper designed for high-signal knowledge management...
> It requires no external Python libraries...

**Status in README2.md:** Preserved identically in the header.

---

## [SYSTEM OVERVIEW & CORE LOGIC] (Lines 6-10)
> Digestitor operates on a hierarchical model where data flows from Reddit's RSS and JSON APIs...
> The system automatically sanitizes label names...

**Status in README2.md:** 
- The general flow description is in **Section 3 (Core Concepts)**.
- Sanitization logic is moved to **Section 3.D (Safe Vault Coexistence & Sanitization)** to keep all file-system safety details in one place.

---

## [SOURCE OF TRUTH] (Lines 12-20)
> Digestitor uses a tripartite authority model to ensure data integrity...
> Deleting a note tells the system to "forget" the post entirely.

**Status in README2.md:** Preserved and enhanced in **Section 3.A (The Multi-Layer Source of Truth)**. It now explicitly mentions the `post_id` surgical check.

---

## [SAFE VAULT COEXISTENCE] (Lines 21-22)
> To allow Digestitor notes to live alongside your existing research...

**Status in README2.md:** Preserved in **Section 3.D**.

---

## [CUMULATIVE KNOWLEDGE] (Lines 24-29)
> Standard scrapers overwrite files, losing previous data...
> A new ## Updated Comments section is appended...

**Status in README2.md:** Preserved in **Section 3.B**.

---

## [MATURITY LOGIC] (Lines 31-35)
> Scraping a thread the moment it is posted often misses the best discussion...
> Note: set min_post_age_hours to 0 to disable.

**Status in README2.md:** Preserved in **Section 3.C**.

---

## [CONFIGURATION GUIDE - GENERAL] (Lines 36-159)
> Every aspect of Digestitor can be controlled through the config file...
> [Detailed explanations of Limit, Detail, Score, Sort, etc.]

**Status in README2.md:** 
- All conceptual explanations (The "What" and "Why") for these settings are preserved in **Section 5 (Comprehensive Configuration Reference)**.
- The redundant bullet points for "How to use in Config/CLI/Python" were removed from each individual entry and replaced with a consistent, non-bolded list for better signal-to-noise ratio.

---

## [DEBUG MODE & PATH MANAGEMENT] (Lines 196-239)
> The debug flag is a powerful safety toggle...
> Typical Workflow Example...

**Status in README2.md:** Preserved in **Section 4 (Debug Mode)**. 

---

## [IMPLEMENTATION EXAMPLES] (Lines 240-277)
> Using the CLI... Using as a Python Dependency... Using the Config File...

**Status in README2.md:** Preserved in **Section 2 (One Tool, Three Interfaces)**. These were moved forward so users can see the code before they read the dry reference material.

---

## [DIRECTORY STRUCTURE & INSTALLATION] (Lines 279-283)
> Digestitor organizes its data into three main components...
> To get started, clone the repository...

**Status in README2.md:**
- **Installation:** Moved to **Section 1** (Installation & Quick Start) so new users find it immediately.
- **Structure:** Moved to **Section 6** (Directory Structure and Files) as a final technical reference.

---

## [REDUNDANCY REMOVAL REPORT]
1. **Duplicate Toggles:** Removed accidental duplicate entries for `Save JSON`, `Update Scrape Log`, and `Update Database` that appeared twice in the original file (Lines 53-63 and 160-195).
2. **Instructional Text:** Removed "FOR MANUAL INTEGRATION" headers and "PASTE IN SECTION" instructions, as they are no longer needed now that the sections are fully integrated.
3. **Nomenclature Clean-up:** Universal replacement of `Project` -> `Flair`, `Story Link` -> `Post Link`, and `Source` -> `Job` to reflect the latest system capabilities.
