import socket
import ssl
from scrape import scrape_func


def send_tcp_request(host, port, request, use_https=False):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if use_https:
        context = ssl.create_default_context()
        client_socket = context.wrap_socket(client_socket, server_hostname=host)

    client_socket.connect((host, port))
    client_socket.sendall(request.encode())

    response = b""
    while True:
        part = client_socket.recv(4096)
        if not part:
            break
        response += part
    client_socket.close()

    return response.decode()


host = 'maximum.md'
path = '/ro/telefoane-si-gadgeturi/telefoane-si-comunicatii/smartphoneuri/'
port = 80

request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

response_str = send_tcp_request(host, port, request)

status_line = response_str.splitlines()[0]
status_code = int(status_line.split()[1])

if status_code == 301:
    headers = response_str.split("\r\n")
    new_location = None
    for header in headers:
        if header.lower().startswith("location:"):
            new_location = header.split(":", 1)[1].strip()
            print(f"Redirecting to {new_location}")
            break

    if new_location:
        if new_location.startswith("https://"):
            use_https = True
            new_location = new_location.replace("https://", "")
            port = 443
        else:
            use_https = False
            new_location = new_location.replace("http://", "")
            port = 80

        new_host, new_path = new_location.split("/", 1)
        new_path = "/" + new_path

        new_request = f"GET {new_path} HTTP/1.1\r\nHost: {new_host}\r\nConnection: close\r\n\r\n"

        new_response_str = send_tcp_request(new_host, port, new_request, use_https)

        response_body = new_response_str.split("\r\n\r\n", 1)[1]

        scrape_func(response_body)

