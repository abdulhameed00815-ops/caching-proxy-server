import requests


name = input("Enter person's name pls: ")

response = requests.get(f"http://localhost/getage/{name}")

print(response.text)

