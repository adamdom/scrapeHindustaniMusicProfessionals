from bs4 import BeautifulSoup
import requests
import json
from  __builtin__ import any as b_any
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

BASE_URL = "http://chandrakantha.com/teachers/"

#india sections 2,3,4
def get_all_india_sections():
    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    body = soup.find("body")
    content = body.find("div", id="Content")
    outerHTML = content.find_all("ul")[2]
    lis = outerHTML.find_all("li")
    links = []
    for l in lis:
      if "New Jersey" not in l:
        links.append(l.find("a")["href"])
    outerHTML = content.find_all("ul")[3]
    lis = outerHTML.find_all("li")
    for l in lis:
      if "California" not in l:
        links.append(l.find("a")["href"])
    outerHTML = content.find_all("ul")[4]
    lis = outerHTML.find_all("li")
    for l in lis:
      if "New Jersey" not in l:
        links.append(l.find("a")["href"])
    return links

def get_names_from_link(link):
    r = requests.get(link)
    if "There are no listings for" in r.text:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    body = soup.find("body")
    content = body.find("div", id="Content")
    listings = content.find_all("p")[2]
    split = (str(listings)).split("<br")
    return [a for a in split if ("Name:" in a and (b_any("sitar" in x for x in split) or (b_any("Sitar" in x for x in split))))]

def extract_names(results):
  results = [a[a.index("Name:") + 6:] for a in results] 
  results = [a[0:a.index("\n")] if "\n" in a else a for a in results]
  return results

def combine_names_from_links():
  results = []
  for l in get_all_india_sections():
    a = get_names_from_link(BASE_URL + l)
    if a:
      for b in a:
        results.append(b)
  results = extract_names(results)
  return results

def sort_names(names): 
  CLASSIFY_URL = "https://api.genderize.io/?name="
  num_females = 0
  num_males = 0
  f = open("output.txt", "r")
  f.close()
  f = open("output.txt", "a+")
  now = " ".join(f.readlines())
  for n in names:
    components = n.split(" ")
    max_prob = 0
    gender = 'unclassified'
    for c in components:
      if "&" in c or n in now:
        continue
      try:
        r = requests.get(CLASSIFY_URL + c)
        if ("gender" in json.loads(r.text)) and (not (json.loads(r.text)['gender'] is None)):
          probability = json.loads(r.text)['probability']
          if probability > max_prob:
            max_prob = probability
            gender = json.loads(r.text)['gender']
      except:
          continue
    if gender == "male":
      num_males = num_males + 1
    elif gender == "female":
      num_females = num_females + 1
    if not (gender == "undefined"):
      try: 
        f.write(n  + " " + gender + "\n")
      except:
        f.write("###" + gender)
      print gender
  f.close()
sort_names(combine_names_from_links())
