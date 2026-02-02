#!/usr/bin/env python3
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file")
    sys.exit(1)

client = OpenAI(api_key=api_key)

def chat(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        print(chat(message))
    else:
        print("ChatGPT Client")
        print("Usage: python chatgpt_client.py <your message>")
        print("Or run interactively:")
        print()
        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                response = chat(user_input)
                print(f"ChatGPT: {response}\n")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

