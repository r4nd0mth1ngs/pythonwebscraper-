# pythonwebscraper-
Just a simple python web scraper with gui using Trafilatura and BeautifulSoup outputting to CSV


Here’s the formatted version for an README.md file:

# Web Scraper GUI with Recursive Crawling

This project is a GUI-based web scraper built using `Tkinter` that recursively crawls a given website, extracts text content, and saves it to a CSV file. The scraper filters URLs based on domain, unwanted file types, and specific terms to avoid unnecessary or irrelevant links.

---

## Features

- **Recursive Scraping:** Crawl websites up to a user-defined depth.
- **Content Extraction:** Extract and save meaningful content (50+ words) from each page.
- **GUI Interface:** Easy-to-use graphical interface for specifying inputs and monitoring progress.
- **URL Filtering:** Skip links based on file extensions, domain mismatches, and excluded terms.
- **CSV Output:** Save scraped content and corresponding URLs into a CSV file.

---

## Requirements

- Python 3.x
- The following Python libraries:
  ```sh
  pip install trafilatura beautifulsoup4

## How to Run
	1.	Clone the repository:

git clone https://github.com/yourusername/web-scraper-gui.git
cd web-scraper-gui


	2.	Install the dependencies:

pip install -r requirements.txt


	3.	Run the application:

python scraper_gui.py

## Usage
	1.	Start the application: Upon running scraper_gui.py, a GUI window will open.
	2.	Enter inputs:
	•	Start URL: The initial URL where the scraper will begin crawling.
	•	Max Depth: The maximum depth of recursion for crawling.
	•	Output CSV File: The name of the CSV file to save scraped content.
	3.	Click “Start Scraping” to begin. Progress and logs will appear in the text box.

## CSV Output

The output CSV will contain:
	•	URL: The scraped URL.
	•	Content: The extracted content from the page.

## URL Filtering
	•	Excluded file extensions: The scraper skips URLs ending with specific extensions like .pdf, .jpg, .aspx, etc.
	•	Excluded terms: URLs containing certain terms like news or # will be ignored.
	•	Domain restriction: Only URLs within the same domain as the start URL will be followed.

## Customisation

To customise the scraper’s behaviour:
	•	Modify the excluded_extensions and excluded_terms lists in scraper_gui.py.
	•	Adjust the delay between requests by changing time.sleep(1) in the recursive_scrape function.

## Future Improvements
	•	Add multithreading support for faster crawling.
	•	Integrate a progress bar for better user feedback.
	•	Expand the exclusion logic with regex-based URL filters.

## License

This project is licensed under the APACHE 2 License. See LICENSE for details.



