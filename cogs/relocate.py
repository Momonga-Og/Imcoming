import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio

class Relocate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.relocating_messages = {}  # Dictionary to keep track of relocating messages

    @app_commands.command(name="relocate", description="Relocate a message to a different channel")
    async def relocate(self, interaction: discord.Interaction, message_id: str, target_channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)  # Defer the response to give time for processing

        logging.info(f"Relocate command invoked by {interaction.user} for message {message_id} to {target_channel}")

        try:
            # Fetch the message by ID
            channel = interaction.channel
            message = await channel.fetch_message(message_id)

            # Check if the message is already being relocated
            if message_id in self.relocating_messages:
                await interaction.followup.send("This message is already being relocated.")
                return

            # Mark the message as being relocated
            self.relocating_messages[message_id] = True

            logging.info(f"Fetched message: {message.content if message.content else 'Image/Embed'}")

            # Relocate message content or attachments
            relocated = False
            if message.content:
                await target_channel.send(f"**Message from {message.author.name} in {channel.mention}:**\n{message.content}")
                relocated = True
            elif message.attachments:
                for attachment in message.attachments:
                    await target_channel.send(file=await attachment.to_file())
                relocated = True
            else:
                await interaction.followup.send("The message has no content or attachments to relocate.")
                return

            # Ensure only one relocation happens
            if relocated:
                await asyncio.sleep(1)  # Small delay to ensure the message is sent before deleting the original

                # Check for the necessary permissions to delete the message
                if not channel.permissions_for(interaction.guild.me).manage_messages:
                    logging.warning("Missing permission to manage messages in the source channel.")
                    await interaction.followup.send("Relocation was successful, but the bot lacks permissions to delete the original message.")
                else:
                    # Delete the original message
                    try:
                        await message.delete()
                        logging.info("Original message deleted")
                        await interaction.followup.send("Message relocated successfully.")
                    except discord.errors.NotFound:
                        logging.warning("Message was not found or already deleted")
                        await interaction.followup.send("Message was not found or already deleted.")
        except discord.errors.NotFound:
            logging.error("The message ID provided does not exist")
            await interaction.followup.send("The message ID provided does not exist.")
        except discord.errors.Forbidden:
            logging.error("The bot lacks permissions to perform this action")
            await interaction.followup.send("The bot lacks permissions to perform this action. Please ensure the bot has 'Manage Messages' permission.")
        except Exception as e:
            logging.exception(f"Error in relocate command: {e}")
            await interaction.followup.send(f"An error occurred while processing your request: {e}")
        finally:
            # Clear the relocating state for the message
            self.relocating_messages.pop(message_id, None)

async def setup(bot):
    cog = Relocate(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('relocate'):
        bot.tree.add_command(cog.relocate)
