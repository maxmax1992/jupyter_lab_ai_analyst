import json
import requests


def get_latest_user_request():
    url = "http://65.109.75.37:8000/get_last_msg"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        json_data = response.json()
        return json_data
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


if __name__ == "__main__":
    get_latest_user_request()
