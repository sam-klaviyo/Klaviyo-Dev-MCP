# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json
import dotenv, os
import re
from bs4 import BeautifulSoup

dotenv.load_dotenv(dotenv_path="/Users/sam.onuallain/Klaviyo-Dev-MCP/kvyo-mcp/.env", override=True)

def parse_confluence_content(html_content):
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
        'link_count': len(links)
    }

# Extract page ID from the URL
web_url = "https://klaviyo.atlassian.net/wiki/spaces/EN/pages/3029139515/API+Review+Council+ARC"
page_id = "3029139515"  # Extracted from the URL

# Use the correct API v2 endpoint
api_url = f"https://klaviyo.atlassian.net/wiki/api/v2/pages/{page_id}"

auth = HTTPBasicAuth("sam.onuallain@klaviyo.com", os.getenv('CONFLUENCE_API_TOKEN'))

headers = {
  "Accept": "application/json"
}

# Query parameters
params = {"body-format": "storage"}

response = requests.request(
   "GET",
   api_url,
   headers=headers,
   auth=auth,
   params=params
)

print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")

if response.status_code == 200:
    data = response.json()
    
    # Parse the HTML content
    html_content = data['body']['storage']['value']
    parsed_content = parse_confluence_content(html_content)
    
    print("\n=== PARSED CONTENT ===")
    print(f"Word count: {parsed_content['word_count']}")
    print(f"Link count: {parsed_content['link_count']}")
    
    print("\n=== CLEAN TEXT ===")
    print(parsed_content['clean_text'][:1000] + "..." if len(parsed_content['clean_text']) > 1000 else parsed_content['clean_text'])
    
    print("\n=== EXTRACTED LINKS ===")
    for i, link in enumerate(parsed_content['links'][:10], 1):  # Show first 10 links
        print(f"{i}. {link['text']} -> {link['url']}")
    
    if len(parsed_content['links']) > 10:
        print(f"... and {len(parsed_content['links']) - 10} more links")
    
    print("\n=== RAW JSON ===")
    print(json.dumps(data, sort_keys=True, indent=4, separators=(",", ": ")))
else:
    print(f"\nError: {response.status_code} - {response.reason}")
    print(response.text)