import discord
from discord.ext import commands
from gtts import gTTS
import os
import asyncio
import logging

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blocked_users = {}

    def text_to_speech(self, text, filename):
        tts = gTTS(text)
        tts.save(filename)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            guild_id = member.guild.id
            if guild_id not in self.blocked_users:
                self.blocked_users[guild_id] = set()
            
            if not member.bot and member.id not in self.blocked_users[guild_id]:
                try:
                    if not self.bot.voice_clients:
                        vc = await after.channel.connect()
                    else:
                        vc = self.bot.voice_clients[0]
                        if vc.channel != after.channel:
                            await vc.move_to(after.channel)

                    audio_file = f'{member.name}_welcome.mp3'
                    welcome_text = f'Welcome to the voice channel, {member.name}!'
                    self.text_to_speech(welcome_text, audio_file)

                    if not os.path.exists(audio_file):
                        logging.error(f"Error: The audio file {audio_file} was not created.")
                        return

                    vc.play(discord.FFmpegPCMAudio(audio_file))

                    while vc.is_playing():
                        await asyncio.sleep(1)

                    if vc.is_connected():
                        await vc.disconnect()

                    # Clean up the audio file after use
                    os.remove(audio_file)
                except Exception as e:
                    logging.exception(f"Error in on_voice_state_update: {e}")

    async def cog_unload(self):
        for vc in self.bot.voice_clients:
            await vc.disconnect()

async def setup(bot):
    cog = Voice(bot)
    await bot.add_cog(cog)
