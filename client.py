import socket
import sys
import requests

import requests_oauthlib
import json
from bs4 import BeautifulSoup
from requests.models import Response


ACCESS_TOKEN = '911753131087851520-uJbfaAOeIboiKdlBZ8A9yQVqOJWshcN'
ACCESS_SECRET = '8xPzdiw6ECuWnTGMcdA4BOlATS2AkjPUNBQhLW7U7yRm8'
CONSUMER_KEY = '2hnglcuJB8L5NHvBeeiwDWx4w'
CONSUMER_SECRET = '2KC4Y2PwjEF5WJW6meNesBei74PcdV71ugvmkuvZqMn6brfAnM'
BEARER_TOKEN = {
    "Content-type": "application/json",
    "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAAMjPMAEAAAAA%2B4%2B3RgyTxBq6lQEY3qClJP%2FJczo%3D35hA06N9kJl7zRP8eYL9MZmMrEK3JzYozs2MIGXZPECbLMo4RG"
}


def get_tweets(track: str = None, lang: str = None):
    # url = 'https://api.twitter.com/2/tweets/search/stream/rules'

    url = 'https://stream.twitter.com/1.1/statuses/filter.json'	

    query_data = [('locations', '-130,-20,100,50')]
    
    if lang:
        query_data.append(('language', lang,))
    else:
        query_data.append(('language', 'en',))

    if track:
        query_data.append(('track', track,))
    else:
        query_data.append(('track', '#',))

    query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
    response = requests.get(query_url, auth=my_auth, stream=True)
    print(query_url, response.content)
    return response


def send_tweets_to_spark(http_resp, tcp_connection):
    for line in http_resp.iter_lines():
      try:
         full_tweet = json.loads(line)
         tweet_text = full_tweet['text']
         print("Tweet Text: " + tweet_text)
         print ("------------------------------------------")
         b = bytes(tweet_text + '\n', 'utf-8')
         tcp_connection.send(b)
      except Exception as e:
         print(f"Error: {e}")

   

if __name__ == '__main__':
    my_auth = requests_oauthlib.OAuth1(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET
    )

    track = None
    lang = None
    niter = 10

    args = sys.argv
    try:
        for i in range(1, len(args)):
            if args[i] == '--help':
                print("Twitter Client Tool")
                print("------------------------")
                print("Usage <python client.py [OPTIONS] [ARGUMENTS]>")
                print("------------------------")
                print("[OPTIONS]")
                print("--help : See the client usage tutorial")
                print("--track : Set the track for tweets extraction. The tracks need to be separeted by comma.")
                print("--lang : Set the language in twitter extraction api.\n")
                print("--iter : Set the number of iterations in the streaming process.\n")
                sys.exit(1)
            if args[i] == '--track':
                track = args[i+1]
                i += 1
            if args[i] == '--iter':
                niter = int(args[i+1])
                i += 1
            if args[i] == '--lang':
                lang = args[i+1]
                i += 1
            
    except IndexError as e:
        print("Wrong usage. Execute with --help to see more.")
        sys.exit(1)

    TCP_IP = 'localhost'
    TCP_PORT = 9017
    conn = None
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    print("Waiting for TCP connection...")
    conn, addr = s.accept()

    print("Connected... Starting getting tweets.")

    # for i in range(niter):
    resp = get_tweets(track=track, lang=lang)
    send_tweets_to_spark(resp, conn)