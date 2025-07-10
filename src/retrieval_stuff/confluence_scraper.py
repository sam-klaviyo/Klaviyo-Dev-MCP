import requests
from requests.auth import HTTPBasicAuth
import json
import dotenv, os
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import argparse

dotenv.load_dotenv(dotenv_path="kvyo-mcp/.env", override=True)
BASE_URL = "https://klaviyo.atlassian.net/wiki/api/v2"

class ConfluenceScraper:
    def __init__(self, dir_path: str, space_keys: list[str]):
        self.base_url = BASE_URL
        self.auth = HTTPBasicAuth(os.getenv("KLAVIYO_EMAIL"), os.getenv('CONFLUENCE_API_TOKEN'))
        print(os.getenv("KLAVIYO_EMAIL"))
        print(os.getenv('CONFLUENCE_API_TOKEN'))
        self.headers = {
            "Accept": "application/json"
        }
        self.space_keys_to_ids = self._get_space_keys_to_ids(space_keys)
        
        self.dir_path = dir_path
        os.makedirs(self.dir_path, exist_ok=True)



    def _make_request(self, path: str, params: dict[str, str]):
        print(f"Making request to {self.base_url + path} with params {params}")
        try:
            response = requests.get(self.base_url + path, auth=self.auth, headers=self.headers, params=params)
            return response.status_code, response.json()
        except Exception as e:
            print(f"Error making request to {self.base_url + path}: {e}")
            return None, None



    def get_page(self, page_id: str, body_format: str):
        status_code, response = self._make_request(f"/pages/{page_id}", {"body-format": body_format})
        if status_code == 200:
            return self._parse_confluence_content(response['body'][body_format]['value'], title=response["title"])
        else:
            print(f"Error getting page {page_id}: {response}")
            return None
        

    
    def _get_space_keys_to_ids(self, keys: list[str]):
        status_code, response = self._make_request(f"/spaces", {"keys": ",".join(keys)})
        if status_code == 200:
            # Print out the id and spaceKey for each space in the response
            key_to_id = {}
            for space in response["results"]:
                space_id = space.get("id")
                space_key = space.get("key")
                key_to_id[space_key] = int(space_id)
            return key_to_id
        else:
            print(f"Error getting space info: {response}")
            return None
    

    def _download_page(self, processed_page: dict, sub_dir: str = ""):
        # clean file title
        file_name = processed_page['title'].replace(" ", "_").replace("/", "-").replace(".", "")
        file_name += ".json"
        with open(os.path.join(self.dir_path, sub_dir, file_name), "w") as f:
            json.dump(processed_page, f)
        

    
    def get_pages_in_space(self, space_key: str, limit: int = 100, body_format: str | None = None):
        params = {"limit": limit}
        if body_format:
            params["body-format"] = body_format
        
        status_code, response = self._make_request(f"/spaces/{self.space_keys_to_ids[space_key]}/pages", params)
        if status_code == 200:
            return response["results"]
        else:
            print(f"Error getting pages in space {space_key}: {response}")
            return None



    def _parse_confluence_content(self, html_content, title: str):
        """
        Parse Confluence HTML content to extract clean text and links.
        
        Args:
            html_content: Raw HTML string from Confluence
            
        Returns:
            dict: Clean text and extracted links
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract all links
        links = []
        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True)
            link_href = link['href']
            links.append({
                'text': link_text,
                'url': link_href
            })
        
        # Extract clean text (removes all HTML tags)
        clean_text = soup.get_text(separator='\n', strip=True)
        
        # Clean up extra whitespace
        clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)  # Remove extra blank lines
        clean_text = re.sub(r' +', ' ', clean_text)  # Remove extra spaces
        
        return {
            'clean_text': clean_text,
            'links': links,
            'word_count': len(clean_text.split()),
            'link_count': len(links),
            'title': title
        }

    def download_pages(self):
        """
        Download all pages from all specified spaces.
        """
        failed_pages = []
        
        for space in self.space_keys_to_ids.keys():
            os.makedirs(os.path.join(self.dir_path, space), exist_ok=True)
            pages = self.get_pages_in_space(space)
            if not pages:
                print(f"No pages found in space {space}")
                continue
                
            print(f"Downloading {len(pages)} pages from space {space}")
            for page in tqdm(pages):
                page_data = self.get_page(page["id"], "storage")
                if not page_data:
                    failed_pages.append(page["id"])
                    continue
                
                # Download the page
                try:
                    self._download_page(page_data, sub_dir=space)
                except Exception as e:
                    print(f"Error downloading page {page['id']}: {e}")
                    failed_pages.append(page["id"])

        print("Download completed!")
        if failed_pages:
            print(f"Failed to download {len(failed_pages)} pages")
            print("Failed page IDs:", failed_pages)
        else:
            print("All pages downloaded successfully!")



def main(args):
    scraper = ConfluenceScraper(dir_path=args.dir_path, space_keys=args.space_keys)
    failed_pages = []
    
    for space in args.space_keys:
        os.makedirs(os.path.join(scraper.dir_path, space), exist_ok=True)
        pages = scraper.get_pages_in_space(space)
        print(f"Downloading {len(pages)} pages from space {space}")
        for page in tqdm(pages):
            page_data = scraper.get_page(page["id"], "storage")
            if not page_data:
                failed_pages.append(page["id"])
                continue
            
            # Download the page
            try:
                scraper._download_page(page_data, sub_dir=space)
            except Exception as e:
                print(f"Error downloading page {page['id']}: {e}")
                failed_pages.append(page["id"])

    print("Done")
    if failed_pages:
        print(f"Failed to download {len(failed_pages)} pages")
        print("------------\n".join(map(str, failed_pages)))
    else:
        print("All pages downloaded successfully!")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--space_keys", nargs="+", default=["ResDev", "EN"])
    parser.add_argument("--dir_path", default="confluence_pages")
    args = parser.parse_args()
    
    main(args)