import json
import time
from typing import Any, Dict

import aiohttp


async def aiohttp_request(
    request_type: str,
    url: str,
    data: Any = None,
    headers: Dict = None,
    cookies: Dict = None,
    timeout_allowed: int = 10,
) -> Dict:
    """Function used for performing a http request asynchronously.

    :param cookies:
    :param request_type: String GET/POST/PUT
    :param url: String
    :param data: Dict  Nullable
    :param headers: Dict Nullable
    :param timeout_allowed: int Max timeout allowed for API call
    :return: Tuple with status_code and json response


    Example:
    resp1 = await aiohttp_request('GET', 'http://localhost:8000/ping/', data={'a': 1})
    print(resp1)

    resp2 = await aiohttp_request('POST', 'http://localhost:8000/pong/', data={'a': 1})
    print(resp2)
    """
    start_time = time.time()
    timeout = aiohttp.ClientTimeout(total=timeout_allowed)
    response = {
        "url": url,
        "method": request_type,
        "payload": data,
        "status_code": None,
        "text": "",
        "headers": "",
        "cookies": None,
        "error_message": "",
        "latency": 0,
        "json": {}
    }

    async with aiohttp.ClientSession(
            cookies=cookies, headers=headers,
            timeout=timeout, json_serialize=json.dumps
    ) as session:
        try:
            filters = {}
            if isinstance(data, dict):
                filters = {"json": data}
            else:
                if not isinstance(data, str):
                    data = json.dumps(data)
                filters = {"data": data}

            request_obj = getattr(session, request_type.lower())
            session_obj = request_obj(url, **filters)

            async with session_obj as resp:
                response["status_code"] = resp.status
                response["headers"] = dict(resp.headers)
                response["cookies"] = dict(resp.cookies)

                if request_type == "GET":
                    try:
                        response["content"] = await resp.content.read()  # resp.content is a StreamReader
                        response["text"] = response["content"].decode()  # converting to str
                    except UnicodeDecodeError as err:
                        response["error_message"] = f"Error occurred while converting bytes to string - {err}"
                else:
                    response["text"] = await resp.text()

            response["latency"] = time.time() - start_time
            response["json"] = json.loads(response["text"])

        except Exception as request_error:
            response["status_code"] = 999
            response["latency"] = (time.time() - start_time)
            response["text"] = request_error
            response["json"] = {}

        return response
