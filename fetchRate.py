from bs4 import BeautifulSoup
import requests

def fetchRate(url: str):
  res = requests.get(url.replace("https://", "http://"))
  res.raise_for_status()
  soup = BeautifulSoup(res.content, "html.parser")
  rates = soup.find_all('table')[2].find_all('tr')
  
  return [x.find('td').get_text(strip=True) for x in rates]