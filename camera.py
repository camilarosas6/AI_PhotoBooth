import requests

class Camera:
    def __init__(self, ip):
        self.ip = ip

    def get_snapshot(self):
        url = f"http://{self.ip}/capture"

        response = requests.get(url, timeout=5)

        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.content