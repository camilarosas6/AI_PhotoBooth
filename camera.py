import requests

class Camera:
    def __init__(self, ip):
        self.ip = ip

    def get_snapshot(self):
        url = f"http://{self.ip}/capture"

        print(f"Solicitando foto a: {url}")

        response = requests.get(url, timeout=15)

        print(f"Estado HTTP: {response.status_code}")
        print(f"Tipo de contenido: {response.headers.get('Content-Type')}")
        print(f"Tamaño recibido: {len(response.content)} bytes")

        response.raise_for_status()

        return response.content