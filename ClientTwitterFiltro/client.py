import requests
import os
import json
import socket

def get_simple_url():
    return "https://api.twitter.com/2/tweets/sample/stream"

def get_filter_url():
    return "https://api.twitter.com/2/tweets/search/stream/"    

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def get_rules(headers, bearer_token):
    response = requests.get(
        get_filter_url() + "rules", headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(headers, bearer_token, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        get_filter_url() + "rules",
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(headers, delete, bearer_token):
    # You can adjust the rules if needed
    sample_rules = [#TODO: CRIAR UM ARQUIVO JSON PARA DEIXAR ESSAS REGRAS DINAMICAS
        {"value": "dog has:images", "tag": "dog pictures"},
        {"value": "cat has:images -grumpy", "tag": "cat pictures"},
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        get_filter_url() + "rules",
        headers=headers,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream(headers, set, bearer_token):
    response = requests.get(
        get_filter_url() , headers=headers, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            print(json.dumps(json_response, indent=4, sort_keys=True))


def connect_to_endpoint(url, headers, conn):
    response = requests.request("GET", url, headers=headers, stream=True)
    print(response.status_code)
    for response_line in response.iter_lines():
        if response_line:
            send_tweets_to_spark(response_line,conn)
            #json_response = json.loads(response_line)
            #print(json.dumps(json_response, indent=4, sort_keys=True))
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )

def send_tweets_to_spark(line,conn):
    try:
         full_tweet = json.loads(line)
         tweet_text = full_tweet['data']['text']
         print("Tweet Text: " + tweet_text)
         print ("------------------------------------------")
         b = bytes(tweet_text + '\n', 'utf-8') 
         conn.send(b) 
    except Exception as e:
        print(f"Error: {str(e)}")
      

def initFilterStream():
    with open('Keys/keys.json') as keys_json:
        bearer_token = json.load(keys_json)['BEARER_TOKEN']
        headers = create_headers(bearer_token)
        rules = get_rules(headers, bearer_token)
        delete = delete_all_rules(headers, bearer_token, rules)
        set = set_rules(headers, delete, bearer_token)
        get_stream(headers, set, bearer_token)

def initStream():
    with open('Keys/keys.json') as keys_json:
        bearer_token = json.load(keys_json)['BEARER_TOKEN']
        url = get_simple_url()
        headers = create_headers(bearer_token)
        timeout = 0

        TCP_IP = '192.168.2.9'
        TCP_PORT = 9999
        conn = None
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# criando com ipv4

        s.bind((TCP_IP, TCP_PORT))##
        s.listen(1)

        print("Waiting for TCP connection...")
        conn, addr = s.accept()
        while True:
            connect_to_endpoint(url, headers,conn)
            timeout += 1

if __name__ == "__main__":
    initFilterStream()