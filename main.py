from dotenv import load_dotenv
from discord.ext import commands
from googlesearch import search
from cript_table import CriptTable
import discord, os, random, json


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
            return False
        elif reaction.__str__() == "❌":
            await reaction.message.channel.send("Partie annulée")
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
            users_keys: dict[int, str] = json.load(file)
        for user in users_keys.keys():
            self.cript_tables[self.cript.translate(user)] = CriptTable(self.cript.translate(users_keys[user]))
    
    def is_owner(self):
        async def predicate(ctx: discord.Interaction):
            if ctx.user.id in self.admin:
                return True
            else:
                await ctx.channel.send("Vous n'avez pas assez de droits pour executer cette commande !")
                return False
        return commands.check(predicate)
    
    async def on_ready(self):
        print(f"{self.user.display_name} est connecté au serveur.")
    
    async def on_message(self, message: discord.Message):
        if message.channel.id != 1132312138980012135:
            try:
                print(f"{message.guild.name} - {message.channel.name} : {message.author.name} -> {message.content}")
            except AttributeError:
                return await super().on_message(message)
        
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
async def set_key(ctx: discord.Interaction, key: str):
    new_table = CriptTable(key)
    bot.cript_tables[str(ctx.user.id)] = new_table
    await ctx.response.send_message(ephemeral=True, embed=discord.Embed(title=f'Your key has been is set to : ||{key}||', color=discord.Color.brand_green()))

@bot.slash_command(name="my_key", description="View your key")
async def my_key(ctx: discord.Interaction):
    if str(ctx.user.id) not in bot.cript_tables:
        await ctx.response.send_message(ephemeral=True, embed=discord.Embed(title="You haven't a key", description="You can set one with `/set_key [key]`", color=discord.Color.brand_green()))
        return
    key = bot.cript_tables[str(ctx.user.id)].seed
    await ctx.response.send_message(ephemeral=True, embed=discord.Embed(title=f"Your key : ||{key}||", color=discord.Color.brand_green()))

@bot.slash_command(name="del_key", description="Delete your key")
async def del_key(ctx: discord.Interaction):
    if str(ctx.user.id) not in bot.cript_tables:
        await ctx.response.send_message(ephemeral=True, embed=discord.Embed(title="You haven't a key, nothing to delete...", color=discord.Color.brand_green()))
        return
    key = bot.cript_tables[str(ctx.user.id)].seed
    bot.cript_tables.pop(str(ctx.user.id))
    await ctx.response.send_message(ephemeral=True, embed=discord.Embed(title=f"Your key ||{key}|| has been delete", color=discord.Color.brand_green()))

@bot.slash_command(name="translate", description="Translate a text with the user's key")
async def translate(ctx: discord.Interaction, *, text: str):
    if str(ctx.user.id) not in bot.cript_tables:
        await ctx.response.send_message(ephemeral=True, embed=discord.Embed(title="You haven't a key", description="Please set one with `/set_key [key]`", color=discord.Color.brand_green()))
        return
    table: CriptTable = bot.cript_tables[str(ctx.user.id)]
    translated_text = table.translate(text)
    await ctx.response.send_message(ephemeral=True, embed=discord.Embed(title='Translated text :', description=translated_text, color=discord.Color.brand_green()))

@bot.slash_command(name="repond", description="Répète ce que tu veux")
async def repond(ctx: discord.Interaction, *, text: str):    
    await ctx.response.send_message(text)

@bot.slash_command(name="jouer", description="Joue au nombre mistère")
async def jouer(ctx: discord.Interaction):
    new_message = await ctx.response.send_message("Voulez vous jouer au nombre mistère ?")
    await new_message.add_reaction("✅")
    await new_message.add_reaction("❌")
    bot.jeu.append(NombreMistere(id_user=ctx.user.id, id_message=new_message.id, channel=ctx.channel))

@bot.slash_command(name="sondage", description="Créé un sondage")
async def sondage(ctx: discord.Interaction, *, question: str):
    if ctx.message:
        await ctx.message.delete()
    new_message = await ctx.response.send_message(f"**Nouveau Sondage de {ctx.user.name}:**\n{question}")
    await new_message.add_reaction("✅")
    await new_message.add_reaction("➖")
    await new_message.add_reaction("❌")

@bot.slash_command(name="research", description="Fait une recherche google")
async def research(ctx: discord.Interaction, num_results: int, *, recherche: str):
    try:
        num_results = int(num_results)
    except:
        await ctx.response.send_message(f"ERROR: {bot.command_prefix}research [nombre_de_résultats] [votre_recherche]", ephemeral=True)
        return
    
    liste = "\n"
    liens = search(recherche, num_results=num_results, lang="fr", timeout=2)
    liens = list(liens)
    while len(liens) > num_results:
        liens.pop(-1)
    for lien in liens:
        liste += f"- {lien}\n"
    await ctx.response.send_message(f"Voici ce que j'ai trouvé :{liste}")

@bot.slash_command(name="clear", description="Efface des messages")
@bot.is_owner()
async def clear(ctx: discord.Interaction, nb: int):
    try:
        nb = int(nb)
        messages = ctx.history(limit=nb)
        await ctx.response.defer(ephemeral=True, invisible=False)
        async for message in messages:
            await message.delete()
    except:
        await ctx.response.send_message(f"ERROR: {bot.command_prefix}clear [nombre_de_messages_à_effacer]", ephemeral=True)

@bot.slash_command(name="alea", description="Créé une phrase aléatoire")
async def alea(ctx: discord.Interaction):
    await ctx.response.send_message(f"{random.choice(bot.pronom)} {random.choice(bot.verbe)} {random.choice(bot.gn)}.")

@bot.slash_command(name="pronom", description="Ajoute un pronom pour la création de phrase aléatoire")
async def add_pronom(ctx: discord.Interaction, *, pronom: str):
    await ctx.response.send_message(f"Le pronom '{pronom}' à bien été ajouté !", ephemeral=True)
    bot.pronom.append(pronom)

@bot.slash_command(name="verbe", description="Ajoute un verbe pour la création de phrase aléatoire")
async def add_verbe(ctx: discord.Interaction, *, verbe: str):
    await ctx.response.send_message(f"Le verbe '{verbe}' à bien été ajouté !", ephemeral=True)
    bot.verbe.append(verbe)

@bot.slash_command(name="gn", description="Ajoute un groupe nominal pour la création de phrase aléatoire")
async def add_gn(ctx: discord.Interaction, *, gn: str):
    await ctx.response.send_message(f"Le gn '{gn}' à bien été ajouté !", ephemeral=True)
    bot.gn.append(gn)

@bot.slash_command(name="emoji", description="Ajoute des emojis aléatoires sous le dernier message")
async def emoji(ctx: discord.Interaction, nb: int = 1):
    reaction = bot.data["Reactions"]
    ctx.response.send_message("Ok", ephemeral=True)
    async for message in ctx.channel.history(limit=1):
        for i in range(int(nb)):
            emoji = random.choice(reaction)["emoji"]
            try:
                await message.add_reaction(emoji)
            except:
                try:
                    emoji = random.choice(reaction)["emoji"]
                    await message.add_reaction(emoji)
                except:
                    return

@bot.slash_command(name="add_emoji", description="Ajoute des emojis aléatoires sous le dernier message")
async def add_emoji(ctx: discord.Interaction, emoji):
    async for message in ctx.channel.history(limit=1):
        await message.add_reaction(emoji)
        await ctx.response.send_message("Ok", ephemeral=True)

@bot.slash_command(name="ban", description="Fait en sorte qu'un utilisateur ne puisse plus écrire")
@bot.is_owner()
async def ban(ctx: discord.Interaction, user: discord.Member):
    if user.id in bot.ban:
        await ctx.response.send_message(f"Le membre {user} est déjà banni.", ephemeral=True)
    else:
        bot.ban.append(user.id)
        await ctx.response.send_message(f"Le membre {user} à été banni !")

@bot.slash_command(name="unban", description="Fait en sorte qu'un utilisateur ne sois plus banni")
@bot.is_owner()
async def unban(ctx: discord.Interaction, user: discord.Member):
    if user.id in bot.ban:
        bot.ban.remove(user.id)
        await ctx.response.send_message(f"Le membre {user} à été débanni !")
    else:
        await ctx.response.send_message(f"Le membre {user} n'est pas banni.", ephemeral=True)


@bot.slash_command(name="help", description="View the list of commands")
async def help(ctx: discord.Interaction):
    title = "Liste des commandes :"
    command_list = ""
    
    for command in bot.all_commands.items():
        if not isinstance(command[1], discord.commands.SlashCommand):
            continue
        
        command: discord.commands.SlashCommand = command[1]
        
        command_list += f"\n> **/{command.name}:** {command.description}"
    
    await ctx.response.send_message(embed=discord.Embed(title=title, description=command_list, color=discord.Color.brand_green()))


try:
    bot.run(os.environ.get("TOKEN"))
finally:
    user_keys = {}
    for user in bot.cript_tables.keys():
        user_keys[bot.cript.translate(user)] = bot.cript.translate(bot.cript_tables[user].seed)
    with open('keys_data.json', "w", encoding="utf-8") as file:
        json.dump(user_keys, file)