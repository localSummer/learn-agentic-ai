import os
from dotenv import load_dotenv
import chainlit as cl
from litellm import completion
import json

load_dotenv()

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

if not deepseek_api_key:
    raise ValueError("DEEPSEEK_API_KEY is not set. Please ensure it is defined in your .env file.")

@cl.on_chat_start
async def start():
    cl.user_session.set("chat_history", [])
    await cl.Message(content="Welcome to the Panaversity AI Assistant! How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="Thinking...")
    await msg.send()

    chat_history = cl.user_session.get("chat_history") or []
    chat_history.append({"role": "user", "content": message.content})

    try:
        response = completion(
            model="deepseek/deepseek-chat",
            messages=[{"role": "system", "content": "You are a helpful assistant."}, *chat_history],
            api_key=deepseek_api_key,
        )
        response_content = response["choices"][0]["message"]["content"]
        msg.content = response_content
        await msg.update()

        chat_history.append({"role": "assistant", "content": response_content})
        cl.user_session.set("chat_history", chat_history)

        # Optional: Log the interaction
        print(f"User: {message.content}")
        print(f"Assistant: {response_content}")

    except Exception as e:
        msg.content = f"Error: {str(e)}"
        await msg.update()
        print(f"Error: {str(e)}")

@cl.on_chat_end
async def on_chat_end():
    history = cl.user_session.get("chat_history") or []
    with open("chat_history.json", "w") as f:
        json.dump(history, f, indent=2)
    print("Chat history saved.")
    