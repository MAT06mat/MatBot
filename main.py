import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import random
from googlesearch import search
import json

load_dotenv('.env')

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
        super().__init__(command_prefix="!", intents=discord.Intents.all(), description="Ceci est un bot test créé par MAT06mat !")
        self.rep = {"Bonjour": ["Bien le boujour !", "Salut !", "Coucou", "Bonjour à toi aussi !", "Salut", "Hey !", "Hello", "Comment tu vas ?", "Bonjour à tous !"]}
        self.jeu = []
        self.admin = [861240797659136012]
        self.ban = []
        self.pronom = ["Je", "Tu", "Il"]
        self.verbe = ["mange", "fais", "roule", "regarde", "ajoute"]
        self.gn = ["de la nourriture", "du caca", "sur la route", "la télé", "des chiffres"]
        with open('data.json', "r", encoding="utf-8") as file:
            self.data = json.load(file)
    
    def is_owner(self):
        async def predicate(ctx):
            if ctx.author.id in self.admin:
                return True
            else:
                await ctx.channel.send("Vous n'avez pas assez de droits pour executer cette commande !")
                return False
        return commands.check(predicate)
    
    async def on_ready(self):
        print(f"{self.user.display_name} est connecté au serveur.")
    
    async def on_message(self, message):
        if message.channel.id != 1132312138980012135:
            print(message.author.name+": "+message.content)
        
        if message.author.id == 1069896287765401630:
            return await super().on_message(message)
        elif message.author.id in self.ban:
            await message.delete()
            return await super().on_message(message)
        else:
            for j in self.jeu:
                if j.id_user == message.author.id and message.channel == j.channel:
                    if await j.message(message):
                        self.jeu.remove(j)
                    return await super().on_message(message)
            match message.content.lower().split(' ')[0]:
                case 'bonjour' | 'salut' | 'hey' | 'slt' | 'bjr' | "cc" | "coucou" | "bonsoir" | "bonchoir" | "bienvenue":
                    await message.channel.send(random.choice(self.rep["Bonjour"]))
        return await super().on_message(message)

    async def on_reaction_add(self, reaction, user):
        for jeu in self.jeu:
            if jeu.id_user == user.id and jeu.id_message == reaction.message.id and reaction.message.channel.id == jeu.channel.id:
                if await jeu.start(reaction):
                    self.jeu.remove(jeu)



bot = MatBot()

@bot.hybrid_command(name="repond", help="Répète ce que tu veux")
async def repond(ctx, *, arg):
    if ctx.message:
        await ctx.message.delete()
    await ctx.send(arg)

@bot.hybrid_command(name="jouer", help="Joue au nombre mistère")
async def jouer(ctx):
    new_message = await ctx.send("Voulez vous jouer au nombre mistère ?")
    await new_message.add_reaction("✅")
    await new_message.add_reaction("❌")
    bot.jeu.append(NombreMistere(id_user=ctx.message.author.id, id_message=new_message.id, channel=ctx.channel))

@bot.hybrid_command(name="sondage", help="Créé un sondage")
async def sondage(ctx, *, args: str):
    if ctx.message:
        await ctx.message.delete()
    new_message = await ctx.send(f"**Nouveau Sondage de {ctx.author}:**\n{args}")
    await new_message.add_reaction("✅")
    await new_message.add_reaction("🔸")
    await new_message.add_reaction("❌")

@bot.hybrid_command(name="research", help="Fait une recherche google")
async def research(ctx, num_results: int = 1, *, args: str):
    try:
        num_results = int(num_results)
    except:
        await ctx.send(f"ERROR: {bot.command_prefix}research [nombre_de_résultats] [votre_recherche]")
        return
    await ctx.send(f"Voici ce que j'ai trouvé :")
    for lien in search(args, num_results=num_results, lang="fr", timeout=2):
        await ctx.send(f" - {lien}")

@bot.hybrid_command(name="clear", help="Efface des messages")
@bot.is_owner()
async def clear(ctx, nb: int = 1):
    try:
        nb = int(nb)
        messages = ctx.history(limit=nb+1)
        async for message in messages:
            await message.delete()
    except:
        await ctx.send(f"ERROR: {bot.command_prefix}clear [nombre_de_messages_à_effacer]")

@bot.hybrid_command(name="alea", help="Créé une phrase aléatoire")
async def alea(ctx):
    await ctx.send(f"{random.choice(bot.pronom)} {random.choice(bot.verbe)} {random.choice(bot.gn)}.")

@bot.hybrid_command(name="pronom", help="Ajoute un pronom pour la création de phrase aléatoire")
async def add_pronom(ctx, *, pronom: str):
    await ctx.send(f"Le pronom '{pronom}' à bien été ajouté !")
    bot.pronom.append(pronom)

@bot.hybrid_command(name="verbe", help="Ajoute un verbe pour la création de phrase aléatoire")
async def add_verbe(ctx, *, verbe: str):
    await ctx.send(f"Le verbe '{verbe}' à bien été ajouté !")
    bot.verbe.append(verbe)

@bot.hybrid_command(name="gn", help="Ajoute un gn pour la création de phrase aléatoire")
async def add_gn(ctx, *, gn: str):
    await ctx.send(f"Le gn '{gn}' à bien été ajouté !")
    bot.gn.append(gn)

@bot.hybrid_command(name="emoji", help="Ajoute des emojis aléatoires sous le dernier message")
async def emoji(ctx, nb: int = 1):
    reaction = bot.data["Reactions"]
    if int(nb) > 20:
        nb = 20
    await ctx.message.delete()
    async for message in ctx.channel.history(limit=1):
        for i in range(int(nb)):
            emoji = random.choice(reaction)["emoji"]
            await message.add_reaction(emoji)

@bot.hybrid_command(name="add_emoji", help="Ajoute l'emoji selectionné sous le dernier message")
async def add_emoji(ctx, emoji: discord.Emoji):
    await ctx.message.delete()
    async for message in ctx.channel.history(limit=1):
        await message.add_reaction(emoji)

@bot.hybrid_command(name="ban", help="Fait en sorte qu'un utilisateur ne puisse plus écrire")
@bot.is_owner()
async def ban(ctx, user: discord.Member):
    if user.id in bot.ban:
        await ctx.send(f"Le membre {user} est déjà banni.")
    else:
        bot.ban.append(user.id)
        await ctx.send(f"Le membre {user} à été banni !")

@bot.hybrid_command(name="unban", help="Fait en sorte qu'un utilisateur ne sois plus banni")
@bot.is_owner()
async def ban(ctx, user: discord.Member):
    if user.id in bot.ban:
        bot.ban.remove(user.id)
        await ctx.send(f"Le membre {user} à été débanni !")
    else:
        await ctx.send(f"Le membre {user} n'est pas banni.")

bot.run(os.environ.get("TOKEN"))
