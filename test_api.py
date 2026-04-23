import json
import socket
import threading
import time
import unittest
import urllib.error
import urllib.request

TEST_PORT = 8081


def _run_test_server():
    from urllib.parse import unquote

    from dice_model import Dice

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("localhost", TEST_PORT))
    srv.listen(5)
    srv.settimeout(1.0)

    def make_json(data, status="200 OK"):
        body = json.dumps(data)
        return f"HTTP/1.1 {status}\r\nContent-Type: application/json\r\n\r\n{body}"

    def parse_qs(path):
        params = {}
        if "?" in path:
            qs = unquote(path.split("?", 1)[1])
            for pair in qs.split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    params[k] = v
        return params

    while _server_running:
        try:
            conn, _ = srv.accept()
        except socket.timeout:
            continue

        req = conn.recv(2048).decode("utf-8")
        first_line = req.split("\n")[0]
        path = first_line.split(" ")[1] if len(first_line.split(" ")) > 1 else "/"

        if path.startswith("/roll_dice"):
            try:
                params = parse_qs(path)
                probs = list(map(float, params["probabilities"].split(",")))
                n = int(params["number"])
                dice = Dice(probabilities=probs, num_rolls=n)
                result = dice.roll()
                resp = make_json({"status": "success", **result.to_dict()})
            except Exception as e:
                resp = make_json(
                    {"status": "error", "error": str(e)}, "400 Bad Request"
                )
        elif path.startswith("/myjson"):
            resp = make_json({"status": "success", "message": "Hello, KU!"})
        else:
            resp = "HTTP/1.1 404 Not Found\r\n\r\n"

        conn.sendall(resp.encode("utf-8"))
        conn.close()

    srv.close()


_server_running = True
_server_thread = threading.Thread(target=_run_test_server, daemon=True)


def _get(path: str):
    url = f"http://localhost:{TEST_PORT}{path}"
    with urllib.request.urlopen(url, timeout=5) as resp:
        return json.loads(resp.read().decode())


def _get_error(path: str):
    url = f"http://localhost:{TEST_PORT}{path}"
    try:
        urllib.request.urlopen(url, timeout=5)
        raise AssertionError("Expected HTTPError")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


class TestAPI(unittest.TestCase):
    def test_roll_success(self):
        data = _get("/roll_dice?probabilities=0.1,0.2,0.3,0.1,0.2,0.1&number=10")
        self.assertEqual(data["status"], "success")

    def test_roll_length(self):
        data = _get("/roll_dice?probabilities=0.1,0.2,0.3,0.1,0.2,0.1&number=15")
        self.assertEqual(len(data["results"]), 15)

    def test_faces_valid(self):
        data = _get("/roll_dice?probabilities=0.1,0.2,0.3,0.1,0.2,0.1&number=50")
        for f in data["results"]:
            self.assertIn(f, [1, 2, 3, 4, 5, 6])

    def test_counts_sum(self):
        n = 30
        data = _get(f"/roll_dice?probabilities=0.1,0.2,0.3,0.1,0.2,0.1&number={n}")
        self.assertEqual(sum(data["counts"].values()), n)

    def test_deterministic_case(self):
        data = _get("/roll_dice?probabilities=1,0,0,0,0,0&number=10")
        self.assertTrue(all(x == 1 for x in data["results"]))

    def test_missing_parameters(self):
        code, body = _get_error("/roll_dice?number=5")
        self.assertEqual(code, 400)
        self.assertIn("error", body)

    def test_invalid_probability_sum(self):
        code, _ = _get_error(
            "/roll_dice?probabilities=0.2,0.2,0.2,0.2,0.2,0.5&number=5"
        )
        self.assertEqual(code, 400)

    def test_invalid_number(self):
        code, _ = _get_error(
            "/roll_dice?probabilities=0.1,0.2,0.3,0.1,0.2,0.1&number=abc"
        )
        self.assertEqual(code, 400)

    def test_myjson_endpoint(self):
        data = _get("/myjson")
        self.assertEqual(data["status"], "success")
        self.assertIn("message", data)


# lifecycle
def setUpModule():
    global _server_running
    _server_running = True
    _server_thread.start()
    time.sleep(0.3)


def tearDownModule():
    global _server_running
    _server_running = False
    _server_thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
