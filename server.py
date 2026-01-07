import requests


cached_responses = []


url = input("enter request URL: ")

response = requests.get(url)

cached_response = {
        "key": url,
        "status_code": response.status_code,
        "content": response.text
}


