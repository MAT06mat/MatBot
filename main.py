import os
import discord
from discord.ext import commands
import random

intents = discord.Intents().all()
client = discord.Client(intents=intents)

class MatBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=intents)
        self.rep = {"bonjour": ["Bien le boujour !", "Salut !", "Coucou", "Bonjour à toi aussi !", "Salut", "Hey !", "Hello"]}

    async def on_ready(self):
        print(f"{self.user.display_name} est connecté au serveur.")    
    
    async def on_message(self, message):
        print(message.author.name+": "+message.content)
        if message.author.id == 1069896287765401630:
            return
        match message.content.lower().split(' ')[0]:
            case 'bonjour' | 'salut' | 'hey' | 'slt' | 'bjr' | "cc" | "coucou" | "bonsoir" | "bonchoir":
                await message.add_reaction("👋")
                await message.channel.send(self.rep["bonjour"][random.randint(0, len(self.rep["bonjour"]))])
            case 'jouer':
                await message.add_reaction("👍")
                await message.channel.send("D'accord, mais à quoi ?")
        
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Commande invalide. Utilisez '/help' pour afficher les commandes disponibles.")


bot = MatBot()

def get_token():
    with open("config", "r") as config_file:
        return config_file.read().split("=")[1]

bot.run(get_token())
