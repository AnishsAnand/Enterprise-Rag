import asyncio
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import random
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import trafilatura
import json
import pandas as pd
import io
import os
import hashlib
from datetime import datetime
from app.core.config import settings

OUTPUT_DIR = os.path.join(os.getcwd(), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class WebScraperService:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })

    async def scrape_url(self, url: str, scrape_params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            print(f"[INFO] Scraping: {url}")
            self.session.headers['User-Agent'] = self.ua.random
            await asyncio.sleep(random.uniform(0.5, 1.5))  # gentler delay

            for method in ['trafilatura', 'requests', 'selenium']:
                try:
                    content = await getattr(self, f"_scrape_with_{method}")(url, scrape_params)
                    if content and content.get('text'):
                        await self._save_to_output_file(url, content, scrape_params.get('output_format', 'json'))
                        return {
                            'url': url,
                            'method': method,
                            'content': content,
                            'status': 'success',
                            'timestamp': datetime.now().isoformat()
                        }
                except Exception as e:
                    print(f"[WARN] {method} failed for {url}: {e}")
                    continue

            return {'url': url, 'content': None, 'status': 'failed', 'error': 'All methods failed'}
        except Exception as e:
            return {'url': url, 'content': None, 'status': 'error', 'error': str(e)}

    async def _save_to_output_file(self, url: str, content: Dict[str, Any], output_format: str):
        try:
            filename = f"{hashlib.md5(url.encode()).hexdigest()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format.lower()}"
            filepath = os.path.join(OUTPUT_DIR, filename)
            file_bytes = await self._process_to_format(content, output_format)
            with open(filepath, "wb") as f:
                f.write(file_bytes)
            print(f"[INFO] Output saved to {filepath}")
        except Exception as e:
            print(f"[ERROR] Failed saving file: {e}")

    async def _scrape_with_requests(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')
        self._clean_html(soup)

        content = self._extract_common_content(url, soup, params)
        return content

    async def _scrape_with_selenium(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        options = uc.ChromeOptions()
        for arg in ['--headless', '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--disable-extensions']:
            options.add_argument(arg)
        options.add_argument(f'--user-agent={self.ua.random}')

        driver = None
        try:
            driver = uc.Chrome(options=options)
            driver.set_page_load_timeout(30)
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            if params.get('wait_for_element'):
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, params['wait_for_element'])))
                except:
                    pass

            if params.get('scroll_page'):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(1.5)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            self._clean_html(soup)
            return self._extract_common_content(url, soup, params)
        finally:
            if driver:
                driver.quit()

    async def _scrape_with_trafilatura(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return {}
        text = trafilatura.extract(downloaded, include_comments=False, include_tables=True)
        metadata = trafilatura.extract_metadata(downloaded)
        return {
            'title': metadata.title if metadata else '',
            'author': metadata.author if metadata else '',
            'date': metadata.date if metadata else '',
            'text': text or ''
        }

    async def discover_urls(self, base_url: str, max_depth: int = 2, max_urls: int = 100) -> List[str]:
        print(f"[INFO] Discovering URLs from: {base_url}")
        discovered, to_visit, visited = set(), [(base_url, 0)], set()
        base_domain = urlparse(base_url).netloc

        while to_visit and len(discovered) < max_urls:
            current_url, depth = to_visit.pop(0)
            if current_url in visited or depth > max_depth:
                continue
            visited.add(current_url)

            try:
                self.session.headers['User-Agent'] = self.ua.random
                resp = self.session.get(current_url, timeout=15)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.content, 'html.parser')

                for a in soup.find_all('a', href=True):
                    href = urljoin(current_url, a['href'].strip())
                    parsed = urlparse(href)
                    if parsed.netloc == base_domain and not any(href.lower().endswith(ext) for ext in ['.pdf', '.jpg', '.png', '.gif', '.css', '.js']):
                        if href not in discovered and href not in visited:
                            discovered.add(href)
                            if depth < max_depth:
                                to_visit.append((href, depth + 1))

                await asyncio.sleep(random.uniform(0.5, 1.2))
            except Exception as e:
                print(f"[WARN] URL discovery failed at {current_url}: {e}")

        return list(discovered)

    def _clean_html(self, soup: BeautifulSoup):
        for tag in ["script", "style", "nav", "footer", "header", "aside"]:
            for match in soup.find_all(tag):
                match.decompose()

    def _extract_common_content(self, url: str, soup: BeautifulSoup, params: Dict[str, Any]) -> Dict[str, Any]:
        content = {'title': soup.title.get_text(strip=True) if soup.title else ''}

        if params.get('extract_text', True):
            main = soup.find('main') or soup.find('article') or soup.find('div', class_=['content', 'main', 'post'])
            content['text'] = main.get_text(strip=True, separator=' ') if main else soup.get_text(strip=True, separator=' ')

        if params.get('extract_links', False):
            content['links'] = self._extract_links(url, soup)

        if params.get('extract_images', False):
            content['images'] = self._extract_images(url, soup)

        if params.get('extract_tables', False):
            content['tables'] = self._extract_tables(soup)

        return content

    def _extract_links(self, base_url: str, soup: BeautifulSoup) -> List[Dict[str, str]]:
        return [{'url': urljoin(base_url, a['href']), 'text': a.get_text(strip=True)}
                for a in soup.find_all('a', href=True) if a.get_text(strip=True)]

    def _extract_images(self, base_url: str, soup: BeautifulSoup) -> List[Dict[str, str]]:
        return [{'url': urljoin(base_url, img['src']), 'alt': img.get('alt', '')}
                for img in soup.find_all('img', src=True)]

    def _extract_tables(self, soup: BeautifulSoup) -> List[List[List[str]]]:
        tables = []
        for table in soup.find_all('table'):
            rows = [[cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])] for row in table.find_all('tr')]
            tables.append([row for row in rows if any(row)])
        return tables

    async def _process_to_format(self, content: Dict[str, Any], output_format: str) -> bytes:
        try:
            fmt = output_format.lower()
            if fmt == 'json':
                return json.dumps(content, indent=2, ensure_ascii=False).encode('utf-8')
            elif fmt == 'csv':
                df = pd.DataFrame([{
                    'title': content.get('title', ''),
                    'text': content.get('text', ''),
                    'links_count': len(content.get('links', [])),
                    'images_count': len(content.get('images', [])),
                    'tables_count': len(content.get('tables', []))
                }])
                buf = io.StringIO()
                df.to_csv(buf, index=False)
                return buf.getvalue().encode('utf-8')
            elif fmt == 'txt':
                return f"Title: {content.get('title', '')}\n\n{content.get('text', '')}".encode('utf-8')
            elif fmt == 'markdown':
                return f"# {content.get('title', '')}\n\n{content.get('text', '')}".encode('utf-8')
            else:
                return json.dumps(content, indent=2, ensure_ascii=False).encode('utf-8')
        except Exception as e:
            print(f"[ERROR] Processing format {output_format}: {e}")
            return json.dumps(content, indent=2, ensure_ascii=False).encode('utf-8')


scraper_service = WebScraperService()
