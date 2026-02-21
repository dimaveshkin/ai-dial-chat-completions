import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import DialClient as CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role

async def start() -> None:
    #TODO:
    # 1.1. Create DialClient
    # (you can get available deployment_name via https://ai-proxy.lab.epam.com/openai/models
    #  you can import Postman collection to make a request, file in the project root `dial-basics.postman_collection.json`
    #  don't forget to add your API_KEY)
    # 1.2. Create CustomDialClient
    # 2. Create Conversation object
    # 3. Get System prompt from console or use default -> constants.DEFAULT_SYSTEM_PROMPT and add to conversation
    #    messages.
    # 4. Use infinite cycle (while True) and get yser message from console
    # 5. If user message is `exit` then stop the loop
    # 6. Add user message to conversation history (role 'user')
    # 7. If `stream` param is true -> call DialClient#stream_completion()
    #    else -> call DialClient#get_completion()
    # 8. Add generated message to history
    # 9. Test it with DialClient and CustomDialClient
    # 10. In CustomDialClient add print of whole request and response to see what you send and what you get in response

    client_type = input("Choose client (1 - dial / 2 - custom (prints raw data)): ").strip()

    if client_type == "1":
        client = DialClient(deployment_name="gemini-3-flash-preview")
    elif client_type == "2":
        client = CustomDialClient(deployment_name="gemini-3-flash-preview")
    else:
        raise ValueError("Invalid client type. Please choose '1' for DialClient or '2' for CustomDialClient.")

    mode = input("Choose mode (1 - stream / 2 - regular): ").strip()

    if mode != "1" and mode != "2":
        raise ValueError("Invalid mode. Please choose '1' for stream or '2' for regular.")

    system_prompt = input("Enter system prompt (or press Enter to use default): ").strip()

    if not system_prompt:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    conversation = Conversation()

    system_message = Message(role=Role.SYSTEM, content=system_prompt)
    conversation.add_message(system_message)

    while True:
        user_input = input("\nYou: ")
        print()

        if user_input.lower() == "exit":
            print("Exiting the chat. Goodbye!.")
            break

        if not user_input.strip():
            print("Empty input. Please enter a message.")
            continue

        user_message = Message(role=Role.USER, content=user_input)
        conversation.add_message(user_message)

        if mode == "1":
            ai_message = await client.stream_completion(conversation.messages)
        else:
            ai_message = client.get_completion(conversation.messages)

        conversation.add_message(ai_message)

asyncio.run(
    start()
)
