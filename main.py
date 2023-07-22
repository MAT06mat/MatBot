import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import random

load_dotenv('.env')

intents = discord.Intents().all()
client = discord.Client(intents=intents)


class NombreMistere:
    def __init__(self, id_user, id_message, channel):
        self.id_user = id_user
        self.id_message = id_message
        self.channel = channel
        self.nb = None
        self.essais = None
    
    async def start(self, reaction):
        if self.nb != None:
            return
        if reaction.__str__() == "✅":
            self.nb = random.randint(1, 100)
            self.essais = 0
            await reaction.message.channel.send("J'ai choisi un nombre entre 1 et 100.\nProposez des nombres pour essayer de le trouver !")
        elif reaction.__str__() == "❌":
            await reaction.message.channel.send("Partie Annulé")
            return True
    
    async def nombre(self, message):
        if self.nb == None:
            return
        try:
            message_int = int(message.content)
        except:
            await message.channel.send("Ceci n'est pas un nombre")
        if message_int > self.nb:
            self.essais += 1
            await message.channel.send(f"Mon nombre est plus petit que {message_int}")
        elif message_int < self.nb:
            self.essais += 1
            await message.channel.send(f"Mon nombre est plus grand que {message_int}")
        else:
            await message.channel.send(f"Bien joué ! Mon nombre est bien : {message_int}")
            await message.channel.send(f"Je te met un score de {20-self.essais*2}/20")
            return True


class MatBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=intents)
        self.rep = {"bonjour": ["Bien le boujour !", "Salut !", "Coucou", "Bonjour à toi aussi !", "Salut", "Hey !", "Hello"]}
        self.jeu = []

    async def on_ready(self):
        print(f"{self.user.display_name} est connecté au serveur.")    
    
    async def on_member_join(member):
        await member.create_dm()
        await member.dm_channel.send(f'Hi {member.name}, welcome to the test Discord server!')
    
    async def on_message(self, message):
        print(message.author.name+": "+message.content)
        
        if message.author.id == 1069896287765401630:
            return
        else:
            for j in self.jeu:
                if j.id_user == message.author.id and message.channel == j.channel:
                    if await j.nombre(message):
                        self.jeu.remove(j)
                    return
            match message.content.lower().split(' ')[0]:
                case 'bonjour' | 'salut' | 'hey' | 'slt' | 'bjr' | "cc" | "coucou" | "bonsoir" | "bonchoir":
                    await message.add_reaction("👋")
                    await message.channel.send(self.rep["bonjour"][random.randint(0, len(self.rep["bonjour"]))])
                case 'jouer':
                    new_message = await message.channel.send("Voulez vous jouer au nombre mistère ?")
                    await new_message.add_reaction("✅")
                    await new_message.add_reaction("❌")
                    self.jeu.append(NombreMistere(id_user=message.author.id, id_message=new_message.id, channel=message.channel))
                case 'sondage':
                    await message.add_reaction("✅")
                    await message.add_reaction("🔸")
                    await message.add_reaction("❌")
                case 'repond' | 'répond':
                    ls = message.content.split(' ')
                    m = ''
                    for i in ls:
                        if i.lower() == "repond" or i.lower() == "répond":
                            continue
                        m = m + ' ' + i
                    if m != "":
                        new_message = await message.channel.send(m)
                    await message.delete()
    

bot = MatBot()

@bot.event
async def on_reaction_add(reaction, user):
    for j in bot.jeu:
        if j.id_user == user.id and j.id_message == reaction.message.id and reaction.message.channel == j.channel:
            if await j.start(reaction):
                bot.jeu.remove(j)

bot.run(os.environ.get("TOKEN"))
