"""
basic_http.py — Simple HTTP server that uses the Dice class for /roll_dice
"""

import json
import socket
from urllib.parse import unquote

from dice_model import Dice, RollResult

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("localhost", 8081))
server_socket.listen(1)
print("Server is listening on port 8081...")


def parse_query_string(path: str) -> dict:
    """Return a dict of query parameters from a URL path string."""
    if "?" not in path:
        return {}
    qs = unquote(path.split("?", 1)[1])
    params = {}
    for pair in qs.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            params[key] = value
    return params


def make_json_response(data: dict, status: str = "200 OK") -> str:
    body = json.dumps(data)
    return f"HTTP/1.1 {status}\r\nContent-Type: application/json\r\n\r\n{body}"


while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address} established.")

    request = client_socket.recv(1024).decode("utf-8")
    print(f"Request received ({len(request)} bytes)")

    # ── /myjson ──────────────────────────────────────────────────────────────
    if request.startswith("GET /myjson"):
        response = make_json_response({"status": "success", "message": "Hello, KU!"})

    # ── /roll_dice ────────────────────────────────────────────────────────────
    elif request.startswith("GET /roll_dice"):
        try:
            first_line = request.split("\n")[0]
            path = first_line.split(" ")[1]
            params = parse_query_string(path)

            if "probabilities" not in params or "number" not in params:
                raise ValueError(
                    "Missing required query parameters: 'probabilities' and 'number'."
                )

            probabilities = list(map(float, params["probabilities"].split(",")))
            num_rolls = int(params["number"])

            dice = Dice(probabilities=probabilities, num_rolls=num_rolls)
            result = dice.roll()

            response = make_json_response(
                {
                    "status": "success",
                    **result.to_dict(),
                }
            )

        except (ValueError, KeyError) as e:
            response = make_json_response(
                {"status": "error", "error": str(e)}, "400 Bad Request"
            )

    elif request.startswith("GET"):
        response = (
            "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
            f"<html><body><h1>Hello, World!</h1><hr><pre>{request}</pre></body></html>"
        )

    else:
        response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"

    client_socket.sendall(response.encode("utf-8"))
    client_socket.close()
    print("Waiting for the next request...")
