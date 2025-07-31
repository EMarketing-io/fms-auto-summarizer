import requests
from bs4 import BeautifulSoup


# Function to extract text from a URL
def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Remove scripts and styles to clean up the text
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    
    return "\n".join(line for line in lines if line)
