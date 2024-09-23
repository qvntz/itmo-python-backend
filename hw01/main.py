import json
import math
from functools import lru_cache
from urllib.parse import parse_qs


async def app(scope, receive, send):
    assert scope["type"] == "http"

    path = scope["path"]
    method = scope["method"]

    if method == "GET" and path == "/factorial":
        query_string = scope["query_string"].decode()
        query_params = parse_qs(query_string)
        n_values = query_params.get("n", [])

        if not n_values or not n_values[0].lstrip("-").isdigit():
            await send_response(send, 422, {"error": "Unprocessable Entity"})
            return

        n = int(n_values[0])
        if n < 0:
            await send_response(send, 400, {"error": "Bad Request"})
            return

        result = math.factorial(n)
        await send_response(send, 200, {"result": result})

    elif method == "GET" and path.startswith("/fibonacci"):
        try:
            n = int(path.split("/")[-1])
        except ValueError:
            await send_response(send, 422, {"error": "Unprocessable Entity"})
            return

        if n < 0:
            await send_response(send, 400, {"error": "Bad Request"})
            return

        result = fibonacci(n)
        await send_response(send, 200, {"result": result})

    elif method == "GET" and path == "/mean":
        body = await receive_body(receive)
        try:
            numbers = json.loads(body)
            if not isinstance(numbers, list) or not all(
                isinstance(x, (int, float)) for x in numbers
            ):
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            await send_response(send, 422, {"error": "Unprocessable Entity"})
            return

        if not numbers:
            await send_response(send, 400, {"error": "Bad Request"})
            return

        result = sum(numbers) / len(numbers)
        await send_response(send, 200, {"result": result})

    else:
        await send_response(send, 404, {"error": "Not Found"})


async def receive_body(receive):
    body = b""
    more_body = True
    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)
    return body


async def send_response(send, status, content):
    response = json.dumps(content).encode()
    headers = [
        (b"content-type", b"application/json"),
    ]
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": response})


@lru_cache
def fibonacci(n):
    phi = (1 + math.sqrt(5)) / 2
    psi = (1 - math.sqrt(5)) / 2
    return int((phi**n - psi**n) / math.sqrt(5))
