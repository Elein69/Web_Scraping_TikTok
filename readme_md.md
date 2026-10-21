# TikTok Profile and Video Scraper (Playwright)

This project is an automated Python web scraper built with Playwright. It extracts public data from a TikTok user's profile and their most recent videos without requiring an official API. By simulating real human interactions, it effectively bypasses common anti-bot mechanisms.

## Features

* **Object-Oriented Design:** Structured using a `ScraperTikTok` class, making it easy to understand, maintain, and integrate into larger projects or databases.
* **Profile Data Extraction:** Retrieves the user's handle, total followers, following count, total account likes, and biography.
* **Video Metrics Extraction:** Navigates the immersive video feed to collect data from the latest N videos, including:
  * Likes
  * Comments
  * Shares
  * Saves (Bookmarks)
  * Video Description
  * Hashtags
* **Advanced Anti-Blocking Mechanisms:**
  * Uses a non-headless browser to bypass immediate bot detection.
  * Navigates videos organically using keyboard simulations (`ArrowDown`).
  * Implements an auto-recovery system: presses `Escape` to close intrusive pop-ups and clicks a "dead zone" (coordinates 10,10) to regain keyboard focus before scrolling.

## Prerequisites

* Python 3.7 or higher
* Stable internet connection

## Installation

1. Clone or download this repository to your local machine.
2. Open a terminal in the project folder.
3. Install the required Playwright library:
   ```bash
   pip install playwright
   ```
4. Install the Playwright browser binaries:
   ```bash
   playwright install
   ```

## Usage

1. Open the Python script (e.g., `scraper.py`) in your preferred code editor.
2. Scroll to the **MAIN EXECUTION BLOCK** at the bottom of the file.
3. Change the target username in the class instantiation. Do not include the "@" symbol.
   ```python
   scraper = ScraperTikTok(usuario="samsole_1", max_videos=10)
   ```
4. Run the script from your terminal:
   ```bash
   python scraper.py
   ```

## How It Works (Code Structure)

The script is built around the `ScraperTikTok` class, which contains the following core methods:

* `iniciar()`: Launches a visible Chromium browser with automation-detection features disabled. Sets a standard viewport and User-Agent.
* `_obtener_texto()`: A safe helper method that attempts to locate an HTML element and extract its text. If the element is not found, it returns a default value ("0") without crashing the program.
* `raspar_perfil()`: Navigates to the user's URL and waits for the profile data to load. **Note:** It allows up to 60 seconds of waiting time so the user can manually solve any initial slide-puzzle CAPTCHAs.
* `raspar_videos()`: Clicks on the first video to open the modal view. It then loops through the specified number of videos, extracting metrics and sending an `ArrowDown` keystroke to load the next one.
* `cerrar()`: Ensures the browser and Playwright context are properly closed upon completion or in the event of a critical error.

## Important Considerations

* **Manual Intervention:** Because TikTok aggressively monitors traffic, the browser is set to visible (`headless=False`). If a CAPTCHA puzzle appears upon loading the profile, you must solve it manually using your mouse. The script will wait for you to do so.
* **Dynamic Selectors:** TikTok frequently changes its internal HTML attributes (`data-e2e`). If the script stops extracting data, these selectors in the code may need to be updated to match TikTok's new layout.

## Disclaimer

This script is for educational purposes only. Web scraping TikTok may violate their Terms of Service. Do not use this tool to make high-frequency, massive requests, as it may result in a temporary or permanent ban of your IP address. Use at your own risk.