from dotenv import load_dotenv
from openai import AsyncOpenAI, AuthenticationError
import discord
import os
import datetime

load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_KEY') 

def log(message):
    """Custom function to ensure all debug messages are timestamped and prefixed."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Using print() here to ensure output
    print(f"[{timestamp}] [PIRATE_LOG] {message}")

# --- Initialize OpenAI Client ---
log("STARTUP: Attempting to initialize OpenAI client...")
try:
    oa_client = AsyncOpenAI(api_key=OPENAI_KEY)
    log("STARTUP: SUCCESS - OpenAI client initialized.")
except Exception as e:
    log(f"!!! CRITICAL INIT ERROR: Failed to initialize OpenAI client: {type(e).__name__}: {e}")

# --- OpenAI Function ---
async def call_openai(question):
    log("--- STARTING OpenAI API call ---")
    try:
        completion = await oa_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": f"Respond like a pirate to the following question: {question}",
                },
            ]
        )
        response = completion.choices[0].message.content
        log(f"SUCCESS: OpenAI API call complete. Response length: {len(response)}")
        return response
    except AuthenticationError as e:
        log(f"!!! ERROR: OpenAI API call failed: AuthenticationError. Check key and billing. Details: {e}")
        return "Garr! Me bank account be empty, matey! (Authentication Error)"
    except Exception as e:
        log(f"!!! ERROR: OpenAI API call failed: {type(e).__name__}: {e}")
        return "Shiver me timbers! The magic compass is broken! (OpenAI General Error)"


# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    # This MUST be the new log message!
    log(f'DISCORD: SUCCESSFULLY LOGGED IN AS {client.user}')

@client.event
async def on_message(message):
    # Log ALL messages received 
    log(f"-> MESSAGE INBOUND: from {message.author}: '{message.content}'")

    if message.author == client.user:
        return

    # Handle $hello command
    if message.content.startswith('$hello'):
        log("-> COMMAND: $hello detected. Sending response.") 
        await message.channel.send('Hello')
        return

    # Handle $question command
    if message.content.startswith('$question'):
        log("-> COMMAND: $question detected. Attempting API interaction.")
        
        try:
            # Robust parsing
            message_content = message.content.strip().split("$question", 1)[1].strip()
            
            if not message_content:
                await message.channel.send("Ye need to ask a *real* question!")
                return
                
            log(f"-> PARSED QUESTION: '{message_content}'. Calling OpenAI...")

            response = await call_openai(message_content) 
            
            log("-> RESPONSE READY. Sending to channel.")
            await message.channel.send(response)

        except Exception as e:
            log(f"!!! CRITICAL ERROR in on_message: {type(e).__name__}: {e}")
            await message.channel.send("By the Kraken's beard! An unexpected bot error occurred!")

client.run(os.getenv('TOKEN'))