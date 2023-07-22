import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import random
from googlesearch import search

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
        self.messages = []
    
    async def start(self, reaction):
        if reaction.__str__() == "✅":
            self.nb = random.randint(1, 100)
            self.essais = 0
            await reaction.message.channel.send("J'ai choisi un nombre entre 1 et 100.\nProposez des nombres pour essayer de le trouver !")
        elif reaction.__str__() == "❌":
            await reaction.message.channel.send("Partie Annulé")
            return True
    
    async def message(self, message):
        if self.nb == None:
            return
        try:
            message_int = int(message.content)
        except:
            await message.channel.send("Ceci n'est pas un nombre")
            return
        if message_int > self.nb:
            self.essais += 1
            await message.channel.send(f"Mon nombre est plus petit que {message_int}")
        elif message_int < self.nb:
            self.essais += 1
            await message.channel.send(f"Mon nombre est plus grand que {message_int}")
        else:
            await message.channel.send(f"Bien joué ! Mon nombre est bien : {message_int}")
            await message.channel.send(f"Je te met un score de {20-self.essais}/20")
            return True


class MatBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=intents)
        self.rep = {"bonjour": ["Bien le boujour !", "Salut !", "Coucou", "Bonjour à toi aussi !", "Salut", "Hey !", "Hello"]}
        self.jeu = []
        self.admin = [861240797659136012]
        self.ban = [] # [1072216355757113384]
        self.pronom = ["Je", "Tu", "Il"]
        self.verbe = ["mange", "fais", "roule", "regarde", "ajoute"]
        self.gn = ["de la nourriture", "du caca", "sur la route", "la télé", "des chiffres"]

    def get_args(self, message):
        ls = message.content.split(' ')
        m = ''
        for i in ls:
            if i == ls[0]:
                continue
            m = m + ' ' + i
        return m
    
    async def on_ready(self):
        print(f"{self.user.display_name} est connecté au serveur.")    
    
    async def on_message(self, message):
        if message.channel.id != 1132312138980012135:
            print(message.author.name+": "+message.content)
            # await self.get_channel(1132312138980012135).send(message.author.name+": "+message.content)
        
        if message.author.id == 1069896287765401630:
            return
        elif message.author.id in self.ban:
            await message.delete()
        else:
            for j in self.jeu:
                if j.id_user == message.author.id and message.channel == j.channel:
                    if await j.message(message):
                        self.jeu.remove(j)
                    return
            match message.content.lower().split(' ')[0]:
                case 'bonjour' | 'salut' | 'hey' | 'slt' | 'bjr' | "cc" | "coucou" | "bonsoir" | "bonchoir":
                    await message.add_reaction("👋")
                    await message.channel.send(self.rep["bonjour"][random.randint(0, len(self.rep["bonjour"]))])
                case '/jouer':
                    new_message = await message.channel.send("Voulez vous jouer au nombre mistère ?")
                    await new_message.add_reaction("✅")
                    await new_message.add_reaction("❌")
                    self.jeu.append(NombreMistere(id_user=message.author.id, id_message=new_message.id, channel=message.channel))
                case '/sondage':
                    m = self.get_args(message=message)
                    if m != "":
                        new_message = await message.channel.send(m)
                    await new_message.add_reaction("✅")
                    await new_message.add_reaction("🔸")
                    await new_message.add_reaction("❌")
                    await message.delete()
                case '/repond' | '/répond':
                    m = self.get_args(message=message)
                    if m != "":
                        new_message = await message.channel.send(m)
                    await message.delete()
                case '/clear':
                    if not message.author.id in self.admin:
                        await message.channel.send("Vous n'avez pas assez de droits pour effectuer cette commande.")
                        return
                    try:
                        m = self.get_args(message=message)
                        m_int = int(m)
                        mess = message.channel.history(limit=m_int+1)
                        async for ms in mess:
                            await ms.delete()
                    except:
                        await message.channel.send("Arguments incorrecte.")
                case "/search":
                    m = self.get_args(message=message)
                    await message.channel.send(f"Voici ce que j'ai trouvé :")
                    for lien in search(m, num_results=3, lang="fr", timeout=2):
                        await message.channel.send(f" - {lien}")
                case "/alea" | "/aléa":
                    await message.channel.send(f"{random.choice(self.pronom)} {random.choice(self.verbe)} {random.choice(self.gn)}.")
                case "/pronom":
                    m = self.get_args(message=message)
                    self.pronom.append(m)
                    await message.channel.send(f"Le pronom '{m}' à bien été ajouté !")
                case "/gn":
                    m = self.get_args(message=message)
                    self.gn.append(m)
                    await message.channel.send(f"Le groupe nominal '{m}' à bien été ajouté !")
                case "/verbe":
                    m = self.get_args(message=message)
                    self.verbe.append(m)
                    await message.channel.send(f"Le verbe '{m}' à bien été ajouté !")
                    
    

bot = MatBot()

@bot.event
async def on_reaction_add(reaction, user):
    for j in bot.jeu:
        if j.id_user == user.id and j.id_message == reaction.message.id and reaction.message.channel == j.channel:
            if await j.start(reaction):
                bot.jeu.remove(j)

bot.run(os.environ.get("TOKEN"))
