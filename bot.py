import os
import requests
from dotenv import load_dotenv
from discord import Intents, Client, Message

# Load the token from somewhere safe
load_dotenv()

# Make it a constant
TOKEN = os.getenv('DISCORD_TOKEN')
COHERE_API_KEY = os.getenv('COHERE_API_KEY')  # Set this in your .env

# Bot setup
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('Message was empty.')
        return

    is_private = user_message[0] == '?'
    if is_private:
        user_message = user_message[1:]

    try:
        # Call the Cohere API for a response
        headers = {
            "Authorization": f"Bearer {COHERE_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "command-xlarge",  # Ensure you're using a valid model
            "prompt": user_message,
            "max_tokens": 100,  # Increased max tokens for longer responses
            "temperature": 0.7,  # Adjusted for more coherent responses
            "stop_sequences": [],  # Removed stop sequences
            "return_prompt": False  # Changed to False since we only need the response
        }
        response = requests.post("https://api.cohere.ai/generate", headers=headers, json=data)

        # Check if the request was successful
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            await message.channel.send("Sorry, I couldn't generate a response right now.")
            return
        
        response_json = response.json()
        
        # Debugging information to see the full response
        #print("API Response:", response_json)

        # Access the AI response directly from the 'text' key
        ai_response = response_json.get('text', 'I couldn’t generate a response.')
        ai_response = ai_response.strip()  # Clean up any leading/trailing whitespace

        await message.author.send(ai_response) if is_private else await message.channel.send(ai_response)

    except Exception as e:
        print("An exception occurred:", e)
        await message.channel.send("An error occurred while trying to generate a response.")



# Handling the startup for the bot
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running.')

# Handle incoming messages    
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] [{username}]: "{user_message}"')
    await send_message(message, user_message)

# Main entry point
def main() -> None:
    client.run(TOKEN)

if __name__ == '__main__':
    main()
