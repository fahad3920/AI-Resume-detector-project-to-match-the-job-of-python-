import requests

session = requests.Session()

def register(username, password):
    url = "http://127.0.0.1:5000/register"
    data = {"username": username, "password": password}
    response = session.post(url, data=data)
    print("Register status:", response.status_code)
    print("Register response URL:", response.url)

def login(username, password):
    url = "http://127.0.0.1:5000/login"
    data = {"username": username, "password": password}
    response = session.post(url, data=data)
    print("Login status:", response.status_code)
    print("Login response URL:", response.url)

def access_main_page():
    url = "http://127.0.0.1:5000/"
    response = session.get(url)
    print("Main page status:", response.status_code)
    if response.status_code == 200:
        print("Main page content preview:")
        print(response.text[:500])  # print first 500 chars

if __name__ == "__main__":
    username = "testuser"
    password = "testpass"

    print("Starting test sequence...")
    register(username, password)
    login(username, password)
    access_main_page()
    print("Test sequence completed.")
