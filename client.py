import requests


choice = input(
        """
what request you want to do?
"post" for a post request,
and "get" for a get request: 
        """
        )

while choice.lower() != 'q':
    if choice.lower() == "get":
        name = input("Enter person's name pls: ")

        response = requests.get(f"http://localhost/getage/{name}")

        print(response.text)
    elif choice.lower() == "post":
        name = input("Enter person's name pls: ")

        data = {
                "name": name
        }

        response = requests.post(f"http://127.0.0.1:8000/checkonperson", json=data)
        print(response.text)
