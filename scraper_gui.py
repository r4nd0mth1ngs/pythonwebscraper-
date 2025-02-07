import os
import time
import threading
import csv
from urllib.parse import urlparse, urljoin, urlunparse

import trafilatura
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, messagebox


def normalize_url(url, base_url=None):
    """
    Normalize a URL:
      - If base_url is provided, join relative URLs.
      - Lower-case the scheme and domain.
      - Remove default ports and trailing slashes.
    """
    try:
        if base_url and not url.startswith(('http://', 'https://')):
            url = urljoin(base_url, url)
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        # Optionally remove default ports
        if (scheme == 'http' and netloc.endswith(':80')) or (scheme == 'https' and netloc.endswith(':443')):
            netloc = netloc.rsplit(':', 1)[0]
        path = parsed.path.rstrip('/') or '/'
        normalized = urlunparse((scheme, netloc, path, '', '', ''))
        return normalized
    except Exception as e:
        print(f"Error normalizing URL '{url}': {e}")
        return None


def scrape_page_content(url):
    """
    Fetch the URL with trafilatura and extract text content.
    Only return content if it has more than 50 words.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            content = trafilatura.extract(downloaded)
            if content and len(content.split()) > 50:
                return content
    except Exception as e:
        print(f"Error fetching/extracting content from {url}: {e}")
    return None


def find_links(html, base_url, excluded_extensions, main_domain, excluded_terms):
    """
    Parse HTML using BeautifulSoup and extract links.
    Filter links that:
      - Have unwanted file extensions.
      - Belong to a domain other than main_domain.
      - Contain any excluded term.
    """
    links = set()
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        normalized = normalize_url(href, base_url)
        if not normalized:
            continue
        parsed = urlparse(normalized)
        if parsed.scheme not in ('http', 'https'):
            continue
        # Skip unwanted file types.
        if any(parsed.path.lower().endswith(ext) for ext in excluded_extensions):
            continue
        # Only follow links within the same domain.
        if parsed.netloc != main_domain:
            continue
        # Skip URLs containing excluded terms.
        if any(term in normalized.lower() for term in excluded_terms):
            continue
        links.add(normalized)
    return links


def recursive_scrape(url, visited, depth, max_depth, excluded_extensions, excluded_terms, csv_writer, log_func):
    """
    Recursively scrape pages starting from the given URL up to max_depth.
    For each page that meets the content requirement, write a row to the CSV
    file (URL, content). log_func is used for updating progress.
    """
    if depth > max_depth:
        return

    normalized_url = normalize_url(url)
    if not normalized_url or normalized_url in visited:
        return

    visited.add(normalized_url)
    log_func(f"Scraping (depth {depth}): {normalized_url}")

    content = scrape_page_content(normalized_url)
    if content:
        try:
            csv_writer.writerow([normalized_url, content])
            log_func(f"Scraped content from {normalized_url}")
        except Exception as e:
            log_func(f"Error writing CSV row for {normalized_url}: {e}")
    else:
        log_func(f"No sufficient content at {normalized_url}")

    time.sleep(1)  # Delay for polite scraping

    html = trafilatura.fetch_url(normalized_url)
    if html:
        main_domain = urlparse(normalized_url).netloc
        links = find_links(html, normalized_url, excluded_extensions, main_domain, excluded_terms)
        for link in links:
            if link not in visited:
                recursive_scrape(link, visited, depth + 1, max_depth,
                                 excluded_extensions, excluded_terms, csv_writer, log_func)


class ScraperGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Web Scraper GUI")
        self.create_widgets()

    def create_widgets(self):
        # Frame for inputs
        input_frame = ttk.Frame(self.master, padding="10")
        input_frame.grid(row=0, column=0, sticky="ew")

        # Start URL
        ttk.Label(input_frame, text="Start URL:").grid(row=0, column=0, sticky="w")
        self.url_entry = ttk.Entry(input_frame, width=50)
        self.url_entry.insert(0, "https://")
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)

        # Maximum Depth
        ttk.Label(input_frame, text="Max Depth:").grid(row=1, column=0, sticky="w")
        self.depth_entry = ttk.Entry(input_frame, width=10)
        self.depth_entry.insert(0, "10")
        self.depth_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Output CSV File
        ttk.Label(input_frame, text="Output CSV File:").grid(row=2, column=0, sticky="w")
        self.file_entry = ttk.Entry(input_frame, width=50)
        self.file_entry.insert(0, "scraped_content.csv")
        self.file_entry.grid(row=2, column=1, padx=5, pady=5)

        # Start Button
        self.start_button = ttk.Button(input_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Log Text widget for progress messages
        log_frame = ttk.Frame(self.master, padding="10")
        log_frame.grid(row=1, column=0, sticky="nsew")
        self.log_text = tk.Text(log_frame, height=15, wrap="word", state="normal")
        self.log_text.pack(expand=True, fill="both")
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)

    def log(self, message):
        """Thread-safe log update."""
        self.log_text.after(0, lambda: self.log_text.insert(tk.END, message + "\n"))
        self.log_text.after(0, lambda: self.log_text.see(tk.END))

    def start_scraping(self):
        """Disable the start button and begin scraping in a separate thread."""
        # Basic validation of inputs.
        start_url = self.url_entry.get().strip()
        if not start_url:
            messagebox.showerror("Input Error", "Please enter a start URL.")
            return
        try:
            max_depth = int(self.depth_entry.get().strip())
        except ValueError:
            messagebox.showerror("Input Error", "Max Depth must be an integer.")
            return

        output_file = self.file_entry.get().strip()
        if not output_file:
            messagebox.showerror("Input Error", "Please specify an output file name.")
            return

        self.start_button.config(state=tk.DISABLED)
        self.log("Starting scraper...")
        thread = threading.Thread(target=self.run_scraper, args=(start_url, max_depth, output_file))
        thread.daemon = True
        thread.start()

    def run_scraper(self, start_url, max_depth, output_file):
        try:
            # Remove output file if it exists.
            if os.path.exists(output_file):
                os.remove(output_file)

            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                # Write header row.
                csv_writer.writerow(["URL", "Content"])
                visited = set()
                excluded_extensions = ['.pdf', '.jpg', '.aspx', '.docx', '.doc', '.jpeg']
                excluded_terms = ['news', '#']

                recursive_scrape(start_url, visited, depth=1, max_depth=max_depth,
                                 excluded_extensions=excluded_extensions,
                                 excluded_terms=excluded_terms,
                                 csv_writer=csv_writer,
                                 log_func=self.log)
            self.log("Scraping complete!")
        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            # Re-enable the start button when done.
            self.start_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()