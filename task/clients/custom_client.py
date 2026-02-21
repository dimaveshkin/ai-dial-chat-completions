import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):
    _endpoint: str

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        # TODO:
        # Take a look at README.md of how the request and regular response are looks like!
        # 1. Create headers dict with api-key and Content-Type
        # 2. Create request_data dictionary with:
        #   - "messages": convert messages list to dict format using msg.to_dict() for each message
        # 3. Make POST request using requests.post() with:
        #   - URL: self._endpoint
        #   - headers: headers from step 1
        #   - json: request_data from step 2
        # 4. Get content from response, print it and return message with assistant role and content
        # 5. If status code != 200 then raise Exception with format: f"HTTP {response.status_code}: {response.text}"

        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }

        request_data = {
            "messages": [msg.to_dict() for msg in messages]
        }

        print('Request Raw Data:\n', json.dumps(request_data, indent=2))

        response = requests.post(
            url=self._endpoint,
            headers=headers,
            json=request_data
        )

        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        response_data = response.json()

        print('\nResponse Raw Data:\n', json.dumps(response_data, indent=2))

        if "choices" not in response_data or not response_data["choices"]:
            raise Exception("No choices in response found")

        content = response_data["choices"][0]["message"]["content"]

        print('\nAI: ', content)

        return Message(role=Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        # TODO:
        # Take a look at README.md of how the request and streamed response chunks are looks like!
        # 1. Create headers dict with api-key and Content-Type
        # 2. Create request_data dictionary with:
        #    - "stream": True  (enable streaming)
        #    - "messages": convert messages list to dict format using msg.to_dict() for each message
        # 3. Create empty list called 'contents' to store content snippets
        # 4. Create aiohttp.ClientSession() using 'async with' context manager
        # 5. Inside session, make POST request using session.post() with:
        #    - URL: self._endpoint
        #    - json: request_data from step 2
        #    - headers: headers from step 1
        #    - Use 'async with' context manager for response
        # 6. Get content from chunks (don't forget that chunk start with `data: `, final chunk is `data: [DONE]`), print
        #    chunks, collect them and return as assistant message

        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        request_data = {
            "messages": [msg.to_dict() for msg in messages],
            "stream": True
        }
        contents = []
        raw_chunks = []

        print('Request Raw Data:\n', json.dumps(request_data, indent=2))

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=self._endpoint,
                    headers=headers,
                    json=request_data
            ) as response:

                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"HTTP {response.status}: {text}")

                print('\nAI (streaming): ', end="", flush=True)

                async for line in response.content:
                    decoded_line = line.decode('utf-8').strip()
                    raw_chunks.append(decoded_line)
                    data_prefix = "data: "
                    done_data = "[DONE]"

                    if decoded_line.startswith(data_prefix):
                        data = decoded_line[len(data_prefix):]

                        if data == done_data:
                            print('\n\nRaw Chunks:\n', '\n'.join(raw_chunks))
                            break

                        try:
                            chunk_data = json.loads(data)
                            content_chunk = chunk_data["choices"][0]["delta"].get("content")

                            if content_chunk:
                                print(content_chunk, end="", flush=True)
                                contents.append(content_chunk)
                        except json.JSONDecodeError:
                            continue

        full_content = "".join(contents)

        return Message(role=Role.AI, content=full_content)