from dotenv import load_dotenv
from discord.ext import commands
from googlesearch import search
from requests.exceptions import HTTPError

from cript_table import CriptTable
from response import response, defer

import discord, os, random, json


MAX_LOGS = 500
load_dotenv('.env')


class NombreMistere:
    def __init__(self, id_user, id_message, channel):
        self.id_user = id_user
        self.id_message = id_message
        self.channel = channel
        self.nb = None
        self.essais = None
        self.messages = []
    
    async def start(self, reaction: discord.Reaction):
        if reaction.__str__() == "✅":
            self.nb = random.randint(1, 100)
            self.essais = 0
            await reaction.message.channel.send("J'ai choisi un nombre entre 1 et 100.\nProposez des nombres pour essayer de le trouver !")
            return False
        elif reaction.__str__() == "❌":
            await reaction.message.channel.send("Partie annulée")
            return True
    
    async def message(self, message: discord.Message):
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
        super().__init__(command_prefix="/", intents=discord.Intents.all(), description="Voici la liste de mes commandes :")
        self.rep = {"Bonjour": ["Bien le boujour !", "Salut !", "Coucou", "Bonjour à toi aussi !", "Salut", "Hey !", "Hello", "Comment tu vas ?", "Bonjour à tous !"]}
        self.jeu = []
        self.admin = [861240797659136012]
        self.ban = []
        self.pronom = ["Je", "Tu", "Il"]
        self.verbe = ["mange", "fais", "roule", "regarde", "ajoute"]
        self.gn = ["de la nourriture", "du caca", "sur la route", "la télé", "des chiffres"]
        self.cript = CriptTable(os.environ.get("TABLE_KEY"))
        with open('data.json', "r", encoding="utf-8") as file:
            self.data = json.load(file)
        self.cript_tables = {}
        with open('keys_data.json', "r", encoding="utf-8") as file:
            users_keys: dict[str, str] = json.load(file)
        with open('logs.json', "r", encoding="utf-8") as file:
            self.logs: list = json.load(file)
        for user in users_keys.keys():
            self.cript_tables[self.cript.translate(user)] = CriptTable(self.cript.translate(users_keys[user]))
    
    def is_owner(self):
        async def predicate(ctx: discord.ApplicationContext):
            if ctx.user.id in self.admin:
                return True
            else:
                await ctx.channel.send("Vous n'avez pas assez de droits pour executer cette commande !")
                return False
        return commands.check(predicate)
    
    async def on_ready(self):
        print(f"{self.user.display_name} est connecté au serveur.")
    
    def on_interaction(self, interaction: discord.interactions.Interaction):
        command = f"/{interaction.data['name']}"
        
        if command in ("/set_key", "/del_key", "/view_key"):
            return super().on_interaction(interaction)
        
        if "options" in interaction.data:
            for option in interaction.data["options"]:
                command += f" {option['name']}:{option['value']}"

        print(f"{interaction.guild.name} - {interaction.channel.name} : {interaction.user.display_name} -> {command}")
        
        self.logs.append({"guild": interaction.guild.id, "channel": interaction.channel.id, "user": interaction.user.id, "command": command})
        
        if len(self.logs) > MAX_LOGS:
            self.logs.pop(-1)
        
        return super().on_interaction(interaction)
    
    async def on_message(self, message: discord.Message):
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
                case 'bonjour' | 'salut' | 'hey' | 'slt' | 'bjr' | "cc" | "coucou" | "bonsoir" | "bonchoir":
                    await message.channel.send(random.choice(self.rep["Bonjour"]))
        return await super().on_message(message)

    async def on_reaction_add(self, reaction, user):
        for jeu in self.jeu:
            if jeu.id_user == user.id and jeu.id_message == reaction.message.id and reaction.message.channel.id == jeu.channel.id:
                if await jeu.start(reaction):
                    self.jeu.remove(jeu)



bot = MatBot()



@bot.slash_command(name="set_key", description="Set your key for the cripted translate")
async def set_key(ctx: discord.ApplicationContext, key: str):
    new_table = CriptTable(key)
    bot.cript_tables[str(ctx.user.id)] = new_table
    await response(ctx, title=f'Your key has been is set to : ||{key}||', embed=True, ephemeral=True)

@bot.slash_command(name="view_key", description="View your key")
async def view_key(ctx: discord.ApplicationContext):
    if str(ctx.user.id) not in bot.cript_tables:
        await response(ctx, title="You haven'y a key", content="You can set one with `/set_key [key]`", embed=True, ephemeral=True)
        return
    key = bot.cript_tables[str(ctx.user.id)].seed
    await response(ctx, ephemeral=True, embed=True, title=f"Your key : ||{key}||")

@bot.slash_command(name="del_key", description="Delete your key")
async def del_key(ctx: discord.ApplicationContext):
    if str(ctx.user.id) not in bot.cript_tables:
        await response(ctx, title="You haven'y a key, nothing to delete...", embed=True, ephemeral=True)
        return
    key = bot.cript_tables[str(ctx.user.id)].seed
    bot.cript_tables.pop(str(ctx.user.id))
    await response(ctx, ephemeral=True, embed=True, title=f"Your key ||{key}|| has been delete")

@bot.slash_command(name="translate", description="Translate a text with the user's key")
async def translate(ctx: discord.ApplicationContext, *, text: str):
    if str(ctx.user.id) not in bot.cript_tables:
        await response(ctx, title="You haven'y a key", content="You can set one with `/set_key [key]`", embed=True, ephemeral=True)
        return
    table: CriptTable = bot.cript_tables[str(ctx.user.id)]
    translated_text = table.translate(text)
    await response(ctx, ephemeral=True, embed=True, title='Translated text :', content=translated_text)

@bot.slash_command(name="repond", description="Répète ce que tu veux")
async def repond(ctx: discord.ApplicationContext, *, text: str):    
    await response(ctx, text)

@bot.slash_command(name="jouer", description="Joue au nombre mistère")
async def jouer(ctx: discord.ApplicationContext):
    msg = await response(ctx, "Voulez vous jouer au nombre mistère ?")
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
    bot.jeu.append(NombreMistere(id_user=ctx.user.id, id_message=msg.id, channel=ctx.channel))

@bot.slash_command(name="research", description="Fait une recherche google")
async def research(ctx: discord.ApplicationContext, number_of_results: int, *, recherche: str):
    if number_of_results > 20:
        await response(ctx, f"Le maximum de résultats est 20...", ephemeral=True)
        return
    
    await defer(ctx, ephemeral=True)
    
    liste = "\n"
    try:
        liens = list(search(recherche, num_results=number_of_results, lang="fr", timeout=5))
    except HTTPError:
        await response(ctx, "Une erreur est survenue, veuillez réessayer plus tard...")
        return
    
    while len(liens) > number_of_results:
        liens.pop(-1)
    
    for lien in liens:
        liste += f"- {lien}\n"
    
    await response(ctx, embed=True, title=f"Voici ce que j'ai trouvé pour {recherche} :", content=liste)

@bot.slash_command(name="alea", description="Créé une phrase aléatoire")
async def alea(ctx: discord.ApplicationContext):
    await response(ctx, f"{random.choice(bot.pronom)} {random.choice(bot.verbe)} {random.choice(bot.gn)}.")

@bot.slash_command(name="pronom", description="Ajoute un pronom pour la création de phrase aléatoire")
async def add_pronom(ctx: discord.ApplicationContext, *, pronom: str):
    bot.pronom.append(pronom)
    await response(ctx, f"Le pronom '{pronom}' à bien été ajouté !", ephemeral=True)

@bot.slash_command(name="verbe", description="Ajoute un verbe pour la création de phrase aléatoire")
async def add_verbe(ctx: discord.ApplicationContext, *, verbe: str):
    bot.verbe.append(verbe)
    await response(ctx, f"Le verbe '{verbe}' à bien été ajouté !", ephemeral=True)

@bot.slash_command(name="gn", description="Ajoute un groupe nominal pour la création de phrase aléatoire")
async def add_gn(ctx: discord.ApplicationContext, *, gn: str):
    bot.gn.append(gn)
    await response(ctx, f"Le gn '{gn}' à bien été ajouté !", ephemeral=True)

@bot.slash_command(name="emoji", description="Ajoute des émojis aléatoires sous le dernier message")
async def emoji(ctx: discord.ApplicationContext, number: int = 1):
    await defer(ctx, ephemeral=True)
    reaction = bot.data["Reactions"]
    async for message in ctx.channel.history(limit=1):
        x = 0
        for i in range(int(number)):
            try:
                emoji = random.choice(reaction)["emoji"]
                await message.add_reaction(emoji)
                x += 1
            except:
                continue
        await response(ctx, f"Ajout de {x} émoji(s) sur le message de {message.author.display_name}")

@bot.slash_command(name="add_emoji", description="Ajoute un émoji sous le dernier message")
async def add_emoji(ctx: discord.ApplicationContext, emoji: discord.Emoji):
    await defer(ctx, ephemeral=True)
    async for message in ctx.channel.history(limit=1):
        await message.add_reaction(emoji)
        await response(ctx, f"Ajout de l'émoji {emoji} sous le message de {message.author.display_name}", ephemeral=True)

@bot.slash_command(name="clear", description="Efface des messages")
@bot.is_owner()
async def clear(ctx: discord.ApplicationContext, number: int):
    await defer(ctx, ephemeral=True)
    messages = ctx.history(limit=number)
    async for message in messages:
        await message.delete()
    await response(ctx, f"{number} message(s) ont bien été supprimés", ephemeral=True)

@bot.slash_command(name="ban", description="Fait en sorte qu'un utilisateur ne puisse plus écrire")
@bot.is_owner()
async def ban(ctx: discord.ApplicationContext, user: discord.Member):
    if user.id in bot.ban:
        await response(ctx, title=f"Le membre {user.display_name} est déjà banni.", embed=True, ephemeral=True)
    else:
        bot.ban.append(user.id)
        await response(ctx, title=f"Le membre {user.display_name} à été banni !", embed=True)

@bot.slash_command(name="unban", description="Fait en sorte qu'un utilisateur ne sois plus banni")
@bot.is_owner()
async def unban(ctx: discord.ApplicationContext, user: discord.Member):
    if user.id in bot.ban:
        bot.ban.remove(user.id)
        await response(ctx, title=f"Le membre {user.display_name} à été débanni !", embed=True)
    else:
        await response(ctx, title=f"Le membre {user.display_name} n'est pas banni.", embed=True, ephemeral=True)

@bot.slash_command(name="logs", description="Voir l'historique des commandes")
@bot.is_owner()
async def logs(ctx: discord.ApplicationContext, numbers: int = 20):
    if numbers > 500:
        await response(ctx, f"Le maximum de nombre de commandes est 500...", ephemeral=True)
        return
    await defer(ctx)
    
    logs = ""
    nb_log = 0
    for log in bot.logs:
        if nb_log >= numbers:
            continue
        if log["guild"] == ctx.guild_id:
            nb_log += 1
            logs += f"> {bot.get_channel(log['channel']).name} -> {bot.get_user(log['user']).display_name}: **{log['command']}**\n"
    
    await response(ctx, embed=True, title=f"Historique des {numbers} dernières commandes :", content=logs)

@bot.slash_command(name="help", description="Affiche la liste des commandes")
async def help(ctx: discord.ApplicationContext):
    title = "Liste des commandes :"
    command_list = ""
    
    for command in bot.all_commands.items():
        if not isinstance(command[1], discord.commands.SlashCommand):
            continue
        
        command: discord.commands.SlashCommand = command[1]
        
        command_list += f"\n> **/{command.name}:** {command.description}"
    
    await response(ctx, embed=True, title=title, content=command_list)


try:
    bot.run(os.environ.get("TOKEN"))
finally:
    user_keys = {}
    for user in bot.cript_tables.keys():
        user_keys[bot.cript.translate(user)] = bot.cript.translate(bot.cript_tables[user].seed)
    with open('keys_data.json', "w", encoding="utf-8") as file:
        json.dump(user_keys, file)
    with open('logs.json', "w", encoding="utf-8") as file:
        json.dump(bot.logs, file)