import discord
from gtts import gTTS
import os
import asyncio  # Ensure asyncio is imported

# Retrieve the bot token from an environment variable
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Get the bot token securely

# Set up Intents
intents = discord.Intents.default()
intents.members = True  # Enable server member events
intents.voice_states = True  # Enable voice channel events

# Create Discord client with these intents
client = discord.Client(intents=intents)

# Function to convert text to speech
def text_to_speech(text, filename):
    tts = gTTS(text)
    tts.save(filename)

# Event: when the bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

# Event: when a member joins a voice channel
@client.event
async def on_voice_state_update(member, before, after):
    # Only execute when the user joins a new channel
    if before.channel is None and after.channel is not None:
        # The user joined a voice channel
        audio_file = f'{member.name}_welcome.mp3'
        welcome_text = f'Welcome to the voice channel, {member.name}!'
        text_to_speech(welcome_text, audio_file)

        # Join the voice channel and play the audio
        vc = await after.channel.connect()  # Join the voice channel
        vc.play(discord.FFmpegPCMAudio(audio_file))  # Play the audio

        # Wait until the audio is finished
        while vc.is_playing():
            await asyncio.sleep(1)  # Wait until the audio is done

        # Disconnect after playing
        if vc.is_connected():
            await vc.disconnect()  # Disconnect from the voice channel

        # Clean up the audio file after use
        os.remove(audio_file)

# Start the Discord bot
client.run(DISCORD_BOT_TOKEN)
