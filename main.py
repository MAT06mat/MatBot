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
        self.ban = [] # [1072216355757113384]
        self.pronom = ["Je", "Tu", "Il"]
        self.verbe = ["mange", "fais", "roule", "regarde", "ajoute"]
        self.gn = ["de la nourriture", "du caca", "sur la route", "la télé", "des chiffres"]
    
    def is_owner(self):
        async def predicate(ctx):
            return ctx.author.id in [861240797659136012]
        return commands.check(predicate)
    
    async def on_ready(self):
        print(f"{self.user.display_name} est connecté au serveur.")
    
    async def on_message(self, message):
        if message.channel.id != 1132312138980012135:
            print(message.author.name+": "+message.content)
            # await self.get_channel(1132312138980012135).send(message.author.name+": "+message.content)
        
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

@bot.command(name="repond", help="Répète ce que tu veux")
async def repond(ctx, *arg):
    await ctx.message.delete()
    await ctx.send(" ".join(arg))

@bot.command(name="jouer", help="Joue au nombre mistère")
async def jouer(ctx):
    new_message = await ctx.send("Voulez vous jouer au nombre mistère ?")
    await new_message.add_reaction("✅")
    await new_message.add_reaction("❌")
    bot.jeu.append(NombreMistere(id_user=ctx.message.author.id, id_message=new_message.id, channel=ctx.channel))

@bot.command(name="sondage", help="Créé un sondage")
async def sondage(ctx, *args):
    await ctx.message.delete()
    new_message = await ctx.send("**Nouveau Sondage :**\n"+" ".join(args))
    await new_message.add_reaction("✅")
    await new_message.add_reaction("🔸")
    await new_message.add_reaction("❌")

@bot.command(name="research", help="Fait une recherche google")
async def research(ctx, num_results, *args):
    try:
        num_results = int(num_results)
    except:
        await ctx.send(f"ERROR: {bot.command_prefix}research [nombre_de_résultats] [votre_recherche]")
        return
    await ctx.send(f"Voici ce que j'ai trouvé :")
    for lien in search(" ".join(args), num_results=num_results, lang="fr", timeout=2):
        await ctx.send(f" - {lien}")

@bot.command(name="clear", help="Efface des messages")
@bot.is_owner()
async def clear(ctx, nb):
    try:
        nb = int(nb)
        messages = ctx.history(limit=nb+1)
        async for message in messages:
            await message.delete()
    except:
        await ctx.send(f"ERROR: {bot.command_prefix}clear [nombre_de_messages_à_effacer]")

@bot.command(name="alea", help="Créé une phrase aléatoire")
async def alea(ctx):
    await ctx.send(f"{random.choice(bot.pronom)} {random.choice(bot.verbe)} {random.choice(bot.gn)}.")

@bot.command(name="pronom", help="Ajoute un pronom pour la création de phrase aléatoire")
async def add_pronom(ctx, pronom):
    bot.pronom.append(pronom)
    await ctx.send(f"Le pronom '{pronom}' à bien été ajouté !")

@bot.command(name="verbe", help="Ajoute un verbe pour la création de phrase aléatoire")
async def add_verbe(ctx, verbe):
    bot.verbe.append(verbe)
    await ctx.send(f"Le verbe '{verbe}' à bien été ajouté !")

@bot.command(name="gn", help="Ajoute un gn pour la création de phrase aléatoire")
async def add_gn(ctx, gn):
    bot.gn.append(gn)
    await ctx.send(f"Le gn '{gn}' à bien été ajouté !")

@bot.hybrid_command()
async def test(ctx):
    await ctx.send("This is a hybrid command!")

bot.run(os.environ.get("TOKEN"))
