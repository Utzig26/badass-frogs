import os
import csv
import requests
import tweepy
from bs4 import BeautifulSoup
"""
can't use twitter API v2 until they add the upload media func.

client = tweepy.Client(
    bearer_token = str(os.environ.get('TWITTER_BADASSFROGS_BEARER_TOKEN')),
    consumer_key= str(os.environ.get('TWITTER_BADASSFROGS_CONSUMER_KEY')),
    consumer_secret= str(os.environ.get('TWITTER_BADASSFROGS_CONSUMER_SECRET')),
    access_token= str(os.environ.get('TWITTER_BADASSFROGS_ACCESS_TOKEN')),
    access_token_secret= str(os.environ.get('TWITTER_BADASSFROGS_ACCESS_TOKEN_SECRET'))
)
"""
ACCESS_KEY = str(os.environ.get('TWITTER_BADASSFROGS_ACCESS_TOKEN'))
ACCESS_SECRET = str(os.environ.get('TWITTER_BADASSFROGS_ACCESS_TOKEN_SECRET'))

CONSUMER_KEY = str(os.environ.get('TWITTER_BADASSFROGS_CONSUMER_KEY'))
CONSUMER_SECRET = str(os.environ.get('TWITTER_BADASSFROGS_CONSUMER_SECRET'))

CALPHOTOS_URL = 'https://calphotos.berkeley.edu' #/cgi/img_query?enlarge=1111+1111+1111+2648
PHOTOS_URL = CALPHOTOS_URL+'/cgi/img_query?where-taxon=' #Alytes+cisternasii

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

with open('frog_id.txt','r+') as frog_file:
  frog_id = int(frog_file.readlines()[0])
  frog_file.seek(0)
  frog_file.write(str(int(frog_id)+1))
  frog_file.truncate()

with open('frogs.txt') as frogs:
  frogs = csv.reader(frogs, delimiter=',')
  for frog_line in frogs:
    if frogs.line_num == frog_id:
      frog = frog_line

photos_page = requests.get(PHOTOS_URL + frog[0].replace(" ", "+")).content
soup = BeautifulSoup(photos_page,features="html.parser")
table = soup.find('table', {"width":"100%"})
tds = table.findAll('td')

photo_page = requests.get(CALPHOTOS_URL + tds[0].a.get('href')).content
soup = BeautifulSoup(photo_page,features="html.parser")
table = soup.findAll('table', {"align":"center"})
tds = table[1].findAll('td')
image = CALPHOTOS_URL+tds[0].img.get('src')
photo_reference = tds[1].text[:len(tds[1].text)-1]

frog_quote = []
frog_quote.append('Badass Frog #' + str(frog_id) + ' - ' + str(frog[0]) + ' (' + str(frog[2]) + ')')
if frog[1]:
  frog_quote.append('Common Name: ' + str(frog[1]))
frog_quote.append('\nImage by ' + photo_reference)
frog_quote = '\n'.join(frog_quote)

frog_image = requests.get(image, stream=True)
filename = 'frog.jpg'

with open(filename, 'wb') as img:
    for chunk in frog_image:
        img.write(chunk)
try:
    response = api.update_status_with_media(status=frog_quote, filename=filename)
    os.remove(filename)
    print(response.id_str + '\n' + response.text)
except Exception as e:
    print(e)
    os.remove(filename)   