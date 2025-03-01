import re
import asyncio
import discord
from discord.ext import commands, tasks
import random
from datetime import timedelta
import time
from datetime import datetime
from datetime import datetime, timezone 
from keep_alive import keep_alive

## Au dessus tout les import..;

intents = discord.Intents.default() ## Intents de discord.
intents.messages = True 
intents.guilds = True
intents.message_content = True
intents.members = True 
bot = commands.Bot(command_prefix='?', intents=intents, help_command=None) ## Préfix configurable change le '?' par se que vous souhaitez.


AUTHORIZED_USER_ID = ''  ## Id de l'utilisateur qui souhaite avoir acces au commands approfondi du bot ! 


LOG_CHANNEL_ID = '' ## ID du channel ou se trouve les logs du bot, 

AFK_CHANNEL_ID = '' ## ID du channel ou se trouvera l'embed du classement du system d'afk/

guild_id = '' # ID du serveur demander 


afk_users = {}


async def create_afk_embed(guild):
    
    sorted_afk = sorted(afk_users.items(), key=lambda x: x[1]["time"])

    leaderboard = ""
    for i, (user_id, afk_info) in enumerate(sorted_afk[:10]):
        member = guild.get_member(user_id) or await guild.fetch_member(user_id)
        user_name = member.name if member else 'Utilisateur inconnu'
        
        afk_time = time.time() - afk_info["time"]
        
        
        days_afk = int(afk_time // (24 * 3600))
        hours_afk = int((afk_time % (24 * 3600)) // 3600)
        minutes_afk = int((afk_time % 3600) // 60)

       
        leaderboard += f"{i + 1}. {user_name}: {days_afk} jour{'s' if days_afk != 1 else ''}, {hours_afk} heure{'s' if hours_afk != 1 else ''}, {minutes_afk} minute{'s' if minutes_afk != 1 else ''}\n"

    embed = discord.Embed(
        title="Classement des utilisateurs AFK",
        description="Voici le classement des utilisateurs avec le plus d'heures d'AFK.",
        color=discord.Color.blue(),
        timestamp=datetime.now(timezone.utc)  
    )

    embed.add_field(name="Top 10 des utilisateurs AFK", value=leaderboard, inline=False)
    return embed


@tasks.loop(seconds=5)
async def change_status():
    afk_count = len(afk_users)   

    
    status_list = [ 
        "Entrain de Dev.", # Texte configurabke a votre guise   
        "Propriétaire du bot - CRYT0S", # Texte configurabke a votre guise  
        "Actuellement en AFK" # Texte configurabke a votre guise  
    ]

    status = random.choice(status_list)

    
    if "AFK" in status:
        status = f"Actuellement en AFK ({afk_count} utilisateur{'s' if afk_count != 1 else ''} AFK)"
    
    
    activity = discord.Game(name=status)
    await bot.change_presence(activity=activity)
    print(f"Statut changé en: {status}")


@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt !")
    
    
    guild = discord.utils.get(bot.guilds, id=guild_id)
    if guild is None:
        print(f"Guilde avec l'ID {guild_id} non trouvé.")
        return
    
    
    embed = await create_afk_embed(guild)

    
    channel = bot.get_channel(AFK_CHANNEL_ID)
    if channel is None:
        print(f"Le canal avec l'ID {AFK_CHANNEL_ID} n'a pas été trouvé.")
        return
    
    
    await channel.send(embed=embed)
    print("Premier embed envoyé au démarrage du bot.")

    
    change_status.start()  

    
    refresh_afk_embed.start()


@tasks.loop(minutes=1)
async def refresh_afk_embed():
    channel = bot.get_channel(AFK_CHANNEL_ID)

    if channel is None:
        print(f"Le canal avec l'ID {AFK_CHANNEL_ID} n'a pas été trouvé.")
        return

    guild = discord.utils.get(bot.guilds, id=guild_id)
    if guild is None:
        print(f"Guilde avec l'ID {guild_id} non trouvé.")
        return

    embed = await create_afk_embed(guild)

    
    async for message in channel.history(limit=1):
        if message.author == bot.user:
            await message.edit(embed=embed)  
            print("Embed mis à jour.")
            break
    else:
        await channel.send(embed=embed)  
        print("Nouvel embed envoyé.")


async def log_command(ctx, command_name, additional_info=""):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        current_time = discord.utils.format_dt(ctx.message.created_at, style="F") 
        embed = discord.Embed(
            title="Commande exécutée",
            description=f"**Nom de l'utilisateur :** {ctx.author.name} ({ctx.author.id})\n"
                        f"**Commande :** {command_name}\n"
                        f"**Date et Heure :** {current_time}\n"
                        f"{additional_info}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Logs du bot")
        await log_channel.send(embed=embed)


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Commandes disponibles", color=0xffffff) ## Couleur de l'embed configurable 
    embed.add_field(name="----------- admin -----------", value="\u200b", inline=False) 
    embed.add_field(name="?role", value="Donne un role souhaité a un utilisateur", inline=False)  # Texte configurabke a votre guise  
    embed.add_field(name="?ban", value="Bannit un membre du serveur", inline=False) # Texte configurabke a votre guise  
    embed.add_field(name="?clear", value="Supprime un certain nombre de messages du canal.", inline=False) # Texte configurabke a votre guise   
    embed.add_field(name="?kick", value="Expulse un membre du serveur", inline=False) # Texte configurabke a votre guise   
    embed.add_field(name="?lock", value="Verrouille le canal actuel.", inline=False) # Texte configurabke a votre guise  
    embed.add_field(name="?renew", value="Supprime puis recrée le canal avec les mêmes paramètres.", inline=False) # Texte configurabke a votre guise   
    embed.add_field(name="?timeout", value="Met un membre en timeout", inline=False) # Texte configurabke a votre guise   
    embed.add_field(name="?unban", value="Débanit un membre du serveur", inline=False) # Texte configurabke a votre guise   
    embed.add_field(name="?unlock", value="Déverrouille le canal actuel.", inline=False) # Texte configurabke a votre guise   
    embed.add_field(name="?untimeout", value="Retire le timeout d'un membre", inline=False) # Texte configurabke a votre guise  
    embed.add_field(name="----------- info -----------", value="\u200b", inline=False) # Texte configurabke a votre guise  
    embed.add_field(name="?Owner", value="Envoie les infos de l'owner du bot.", inline=False) # Texte configurabke a votre guise  
    embed.add_field(name="----------- misc -----------", value="\u200b", inline=False) # Texte configurabke a votre guise  
    embed.add_field(name="?ping", value="Renvoie Pong et affiche la latence du bot", inline=False) # Texte configurabke a votre guise  
    embed.add_field(name="?safk", value="Met un utilisateur Souhaitez AFK (Seulement les Admin)", inline=False) # Texte configurabke a votre guise  
    embed.add_field(name="?afk", value="Empeche les ping inutile en vous mettant AFK", inline=False) # Texte configurabke a votre guise   
    embed.add_field(name="?Afklist", value="Montre la liste des personne en AFK", inline=False) # Texte configurabke a votre guise  
    embed.add_field(name="?afkstarttime", value="Lance un utilisateur en afk avec un temps defini 1d,1h,1m", inline=False) # Texte configurabke a votre guise  
    embed.add_field(name="----------- FUN -----------", value="\u200b", inline=False) # Texte configurabke a votre guise  
    embed.add_field(name="?rban", value="Ban une personne random du serveur", inline=False) # Texte configurabke a votre guise  
    await ctx.send(embed=embed)


    await log_command(ctx, "help")





WELCOME_MESSAGE = "Bienvenue {member.mention} sur **{guild.name}** ! Nous sommes heureux de t'accueillir parmi nous ! 🎉" # Texte configurabke a votre guise  
WELCOME_GIF_URL = "" ##  GIF DE BIENVENUE A CONFIG ...  



SHOW_WELCOME_CHANNEL = False 


@bot.event
async def on_member_join(member):

    target_guild_id = ''  ## Ici  mettre l'ID de la guild

 
    if member.guild.id != target_guild_id:
        return  


    welcome_channel = bot.get_channel() ##  Entre les () Mettre l'ID du salon ou seras envoyée l'embed de bienvenue


    welcome_message = WELCOME_MESSAGE.format(member=member, guild=member.guild)


    embed = discord.Embed(
        title="Bienvenue !",
        description=welcome_message,
        color=discord.Color(0xD50000) 
    )
    embed.set_image(url=WELCOME_GIF_URL)

  
    if SHOW_WELCOME_CHANNEL:
        embed.add_field(name="Dev. By cryt0s", value=str(welcome_channel.name)) 


    if welcome_channel:
        await welcome_channel.send(embed=embed)


    await log_member_join(member, welcome_channel)

async def log_member_join(member, welcome_channel):
    log_channel_1 = bot.get_channel(LOG_CHANNEL_ID)  
    log_channel_2 = bot.get_channel() ## Channel configurable si il y a  besoin d'un autre salon de logs.  

    if log_channel_1:
        current_time = discord.utils.format_dt(member.joined_at, style="F") 
        embed = discord.Embed(
            title="Nouveau membre rejoint",
            description=f"**Nom de l'utilisateur :** {member.name} ({member.id})\n"
                        f"**Serveur :** {member.guild.name}\n"
                        f"**Date et Heure de rejoindre :** {current_time}\n"
                        f"**ID du salon de bienvenue :** {welcome_channel.id}",
            color=discord.Color(0xD50000)  
        )
        embed.set_footer(text="Logs du bot")
        
       
        await log_channel_1.send(embed=embed)
        
    
        await log_channel_2.send(embed=embed)


@bot.command()
async def afk(ctx, *, reason="Aucune Raison."):

    afk_users[ctx.author.id] = {
        "reason": reason,
        "time": time.time()  
    }


    await ctx.send(f"{ctx.author.mention} est maintenant en mode AFK.\nRaison: {reason}")


    await log_command(ctx, "afk", f"Raison: {reason}")


@bot.event
async def on_message(message):

    if message.author == bot.user:
        return


    mentioned_user_ids = [user.id for user in message.mentions]
    afk_mentions = [user_id for user_id in mentioned_user_ids if user_id in afk_users]

    if afk_mentions:
        for user_id in afk_mentions:
            afk_info = afk_users[user_id]
            afk_time = time.time() - afk_info["time"]
            

            days_afk = int(afk_time // (24 * 3600))
            hours_afk = int((afk_time % (24 * 3600)) // 3600)
            minutes_afk = int((afk_time % 3600) // 60)
            seconds_afk = int(afk_time % 60)
            reason = afk_info["reason"]

            await message.delete()

    
            await message.channel.send(f"{message.author.mention} a mentionné un utilisateur en mode AFK.\n"
                                       f"L'utilisateur est AFK depuis {days_afk} jours, {hours_afk} heures, "
                                       f"{minutes_afk} minutes et {seconds_afk} secondes.\n"
                                       f"Raison: {reason}")


    if message.author.id in afk_users:
        afk_info = afk_users.pop(message.author.id)  
        afk_time = time.time() - afk_info["time"]
        
    
        days_afk = int(afk_time // (24 * 3600))
        hours_afk = int((afk_time % (24 * 3600)) // 3600)
        minutes_afk = int((afk_time % 3600) // 60)
        seconds_afk = int(afk_time % 60)

     
        await message.channel.send(f"{message.author.mention} est de retour !\n"
                                   f"{message.author.mention} était AFK pendant {days_afk} jours, {hours_afk} heures, "
                                   f"{minutes_afk} minutes et {seconds_afk} secondes.")


    await bot.process_commands(message)


@bot.command(aliases=["afklist"])
async def Afklist(ctx):

    sorted_afk_users = sorted(afk_users.items(), key=lambda item: time.time() - item[1]["time"], reverse=True)

   
    embed = discord.Embed(
        title="Classement des utilisateurs AFK",
        description="Voici le classement des utilisateurs AFK en fonction du temps passé AFK.", 
        color=discord.Color.blue()
    )


    for i, (user_id, afk_info) in enumerate(sorted_afk_users[:10]): 
        afk_time = time.time() - afk_info["time"]
        
        days_afk = int(afk_time // (24 * 3600))
        hours_afk = int((afk_time % (24 * 3600)) // 3600)
        minutes_afk = int((afk_time % 3600) // 60)
        seconds_afk = int(afk_time % 60)
        
        user = await bot.fetch_user(user_id)
        embed.add_field(
            name=f"{i+1}. {user.name}",
            value=f"{days_afk} jours, {hours_afk} heures, {minutes_afk} minutes, {seconds_afk} secondes",
            inline=False
        )

 
    await ctx.send(embed=embed)

 
    await ctx.send(embed=embed)

@bot.command()
async def stopafk(ctx, identifier: str = None):

    if identifier is None:
        user = ctx.author
    else:
       
        if identifier.isdigit():

            user_id = int(identifier)
            user = ctx.guild.get_member(user_id)
        else:
      
            user = ctx.message.mentions[0] if ctx.message.mentions else None

    
        if user is None:
            await ctx.send("Utilisateur non trouvé. Assurez-vous que l'ID ou la mention est valide.")
            return


    if user.id in afk_users:

        afk_info = afk_users.pop(user.id)


        afk_time = time.time() - afk_info["time"]
        days_afk = int(afk_time // (24 * 3600))
        hours_afk = int((afk_time % (24 * 3600)) // 3600)
        minutes_afk = int((afk_time % 3600) // 60)
        seconds_afk = int(afk_time % 60)

   
        await ctx.send(f"{user.mention} n'est plus en mode AFK.\n"
                       f"{user.mention} était AFK pendant {days_afk} jours, {hours_afk} heures, "
                       f"{minutes_afk} minutes et {seconds_afk} secondes.")
    else:
    
        await ctx.send(f"{user.mention} n'est pas en mode AFK.")


@bot.command()
async def safk(ctx, user_id: int, *, reason="Aucune raison fournie"):
    """
    Commande pour mettre un utilisateur en mode AFK avec une raison spécifiée.
    Le user_id doit être un entier représentant l'ID Discord de l'utilisateur.
    """

    user = await bot.fetch_user(user_id)
    if not user:
        await ctx.send(f"L'utilisateur avec l'ID {user_id} n'a pas pu être trouvé.")
        return
    
 
    afk_users[user.id] = {
        "reason": reason,
        "time": time.time()  
    }


    await ctx.send(f"{user.mention} est maintenant en mode AFK.\nRaison: {reason}")


    await log_command(ctx, "safk", f"Utilisateur: {user.mention}, Raison: {reason}")



@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    gif_url = "" # gif de la command ban a config. 


    private_embed = discord.Embed(
        title="Vous avez été banni",
        description=f"Vous avez été banni de **{ctx.guild.name}**.\nRaison: {reason or 'Aucune raison fournie.'}",
        color=0xff0000  
    )
    private_embed.set_image(url=gif_url)  


    try:
        await member.send(embed=private_embed)
    except discord.Forbidden:
        await ctx.send(f"Impossible d'envoyer un message privé à {member.mention}.")


    await member.ban(reason=reason)


    embed = discord.Embed(
        title="Le membre est parti dans un nouveau monde ;) ", # Texte configurabke a votre guise  
        description=f"{member.mention} C'est TCHAO \nRaison: {reason or 'Pas besoin de parler'}", # Texte configurabke a votre guise  
        color=0xff0000  
    )
    embed.set_image(url=gif_url)  
    await ctx.send(embed=embed)


    await log_command(ctx, "ban")


@bot.command()
async def afkstarttime(ctx, duration: str, identifier: str = None): # commands uniquement utilisable part authorized id 
  
    if ctx.author.id != AUTHORIZED_USER_ID:
        await ctx.send("Désolé, vous n'êtes pas autorisé à utiliser cette commande.")
        return

 
    if identifier is None:
        user = ctx.author
    else:
      
        if identifier.isdigit():
           
            user_id = int(identifier)
            user = ctx.guild.get_member(user_id)
        else:
          
            user = ctx.message.mentions[0] if ctx.message.mentions else None

       
        if user is None:
            await ctx.send("Utilisateur non trouvé. Assurez-vous que l'ID ou la mention est valide.")
            return

  
    pattern = re.compile(r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?")
    match = pattern.fullmatch(duration)

    if not match:
        await ctx.send("Le format de la durée est invalide. Utilisez `Xd Yh Zm` (ex: 1d 2h 30m).")
        return


    days = int(match.group(1) or 0)
    hours = int(match.group(2) or 0)
    minutes = int(match.group(3) or 0)

 
    afk_seconds = timedelta(days=days, hours=hours, minutes=minutes).total_seconds()

 
    afk_users[user.id] = {
        "reason": "Manuel (via afkstarttime)", 
        "time": time.time() - afk_seconds 
    }


    await ctx.send(f"{user.mention} est maintenant en mode AFK avec une durée de {days} jours, {hours} heures et {minutes} minutes.")



@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    deleted_messages = await ctx.channel.purge(limit=amount)

    gif_url = "" ## gif de la command clear a config.

    embed = discord.Embed(
        title="Vous n'avez rien vu : )", # Texte configurabke a votre guise  
        description="Vous avez vu quelque chose ? PAS MOI 👀​.", # Texte configurabke a votre guise  
        color=0xffffff   
    )
    embed.set_image(url=gif_url)  

    message = await ctx.send(embed=embed)

    await asyncio.sleep(5)
    await message.delete()

  
    await log_command(ctx, "clear")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)

    gif_url = "" ## gif de la command kick a config. 

    embed = discord.Embed(
        title="Il est parti faire un tour...", # Texte configurabke a votre guise  
        description=f"{member.mention} fait une petite sieste. \nRaison: {reason or 'Aucune raison fournie.'}", # Texte configurabke a votre guise  
        color=0x00ff00  
    )
    embed.set_image(url=gif_url)  

    await ctx.send(embed=embed)

   
    await log_command(ctx, "kick")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
  
    bot_role = ctx.guild.get_member(ctx.bot.user.id).roles[-1]  


    for role in ctx.guild.roles:
     
        if role >= bot_role: 
            continue
        
        if not role.permissions.administrator:  
        
            await ctx.channel.set_permissions(role, send_messages=False)
    
    gif_url = "" ## Gif de la command lock a config.

    embed = discord.Embed(
        title="Hop, plus personne ne parle.", # Texte configurabke a votre guise  
        description="Vous ne pouvez plus écrire ;) ", # Texte configurabke a votre guise   
        color=0x0000ff  
    )
    embed.set_image(url=gif_url)

    await ctx.send(embed=embed)

    await log_command(ctx, "lock")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def renew(ctx):
    channel = ctx.channel
    await channel.delete()
    
    new_channel = await ctx.guild.create_text_channel(channel.name, category=channel.category)

    gif_url = "" ## Gif de la command Renew a config.   

    embed = discord.Embed(
        title="Te revoila", # Texte configurabke a votre guise  
        description=f"Le canal est de retour !", # Texte configurabke a votre guise  
        color= 0x000000  
    )
    embed.set_image(url=gif_url)  

    await new_channel.send(embed=embed)

   
    await log_command(ctx, "renew")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, duration: int):
    await member.timeout(discord.utils.utcnow() + timedelta(minutes=duration))

    gif_url = "" ## Gif de la command timeout a config.   

    embed = discord.Embed(
        title="Membre c'est endormi", # Texte configurabke a votre guise  
        description=f"{member.mention} dort pendant {duration} minutes.", # Texte configurabke a votre guise   
        color=0x000000  
    )
    embed.set_image(url=gif_url)  

    await ctx.send(embed=embed)


    await log_command(ctx, "timeout")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User):
    await ctx.guild.unban(user)

    gif_url = "" ## Gif de la command unban a config.    

    embed = discord.Embed(
        title="De retour parmis nous", # Texte configurabke a votre guise  
        description=f"{user.mention} est de retour.", # Texte configurabke a votre guise   
        color=0xffffff  
    )
    embed.set_image(url=gif_url)  

    await ctx.send(embed=embed)

  
    await log_command(ctx, "unban")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
   
    bot_role = ctx.guild.get_member(ctx.bot.user.id).roles[-1] 

   
    for role in ctx.guild.roles:
        
        if role >= bot_role or role.permissions.administrator:
            continue
        
       
        await ctx.channel.set_permissions(role, send_messages=True)
    
    gif_url = "" ## gif de la command unlock a config.

    embed = discord.Embed(
        title="Et c'est reparti !", # Texte configurabke a votre guise   
        description="Vous pouvez reparler !", # Texte configurabke a votre guise  
        color=0xffff00  
    )
    embed.set_image(url=gif_url)

    await ctx.send(embed=embed)

  
    await log_command(ctx, "unlock")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):
    await member.timeout(None)

    gif_url = "" ## Gif de la command untimeout a config.   

    embed = discord.Embed(
        title="Le membre est reveiller de force", # Texte configurabke a votre guise   
        description=f"{member.mention} se reveil !", # Texte configurabke a votre guise   
        color=0xff0000  
    )
    embed.set_image(url=gif_url)  

    await ctx.send(embed=embed)

  
    await log_command(ctx, "untimeout")

@bot.command()
async def Owner(ctx):
    gif_url = "" ## Gif de la commands Owner a config.  

    embed = discord.Embed(
        title="Propriétaire du Bot",
        description="L'owner du bot est <@>. Dm moi si tu as besoin ;)", # <-- Mettre ton ID dans la mention soit <@TON ID>
        color=0xff0000  
    )
    embed.set_image(url=gif_url)  

    await ctx.send(embed=embed)

    
    await log_command(ctx, "Owner")

@bot.command()
async def ping(ctx):
    latency = bot.latency * 1000  

    gif_url = "" ## Gif de la commands 'Ping' pour voirs la latences a config.  

    embed = discord.Embed(
        title="Pong!", # Texte configurabke a votre guise   
        description=f"Latence: {latency:.2f}ms",
        color=0x0000ff  
    )
    embed.set_image(url=gif_url)  

    await ctx.send(embed=embed)

 
    await log_command(ctx, "ping")

@bot.command()
@commands.has_permissions(ban_members=True)
async def rban(ctx):
 
    if not ctx.guild.me.guild_permissions.ban_members:
        await ctx.send("Je n'ai pas la permission de bannir des membres.")
        await log_command(ctx, ",rban", f"{ctx.author} a essayé de bannir un utilisateur, mais le bot n'a pas la permission.")
        return

    try:
      
        members = []
        async for member in ctx.guild.fetch_members():
            if not member.bot:  # Evite de random ban, les bots.
                members.append(member)

        if len(members) == 0:
            await ctx.send("Aucun utilisateur non-bot n'a été trouvé pour bannir.")
            await log_command(ctx, ",rban", "Aucun membre non-bot trouvé pour bannir.")
            return

       
        await log_command(ctx, ",rban", f"Nombre de membres disponibles pour bannir : {len(members)}")

        random_member = random.choice(members)  

        
        warning_gif_url = ""   ## Gif a config, Gif envoyée dans l'embed priver envoyée avant le ban.

      
        try:
            dm_embed = discord.Embed(
                title="Tu viens de te faire random ban !",
                description=f"Tu viens d'être banni du serveur **{ctx.guild.name}**. Si cela ne te convient pas, contacte (Met ton nom.)", ## Config ton nom.
                color=discord.Color(0x000000)
            )
            dm_embed.set_image(url=warning_gif_url)  
            await random_member.send(embed=dm_embed)
            await log_command(ctx, ",rban", f"Avertissement envoyé à {random_member.name} avant le ban.")
        except discord.Forbidden:
           
            await log_command(ctx, ",rban", f"Impossible d'envoyer un MP à {random_member.name}.")

     
        try:
            await random_member.ban(reason="Ban random")  
            await ctx.send(f"{random_member.mention} a été banni du serveur !")
            await log_command(ctx, ",rban", f"{random_member.name} a été banni par {ctx.author.name}.")

         
            custom_gif_url = "" ## Gif envoyée dans le chat ou est fait la commands. 

          
            embed = discord.Embed(
                title="Ban aléatoire exécuté",
                description=f"{random_member.mention} a été banni par {ctx.author.mention}.\nRaison: Ban random.",
                color=discord.Color.from_rgb(0, 0, 0)  # Couleur de l'embed [[Le changer que si besoin]]
            )
            embed.set_image(url=custom_gif_url)
            await ctx.send(embed=embed)

           
            await log_command(ctx, ",rban", f"Ban aléatoire exécuté pour {random_member.name}.")

        except discord.Forbidden:
            await ctx.send("Je n'ai pas la permission de bannir cet utilisateur.")
            await log_command(ctx, ",rban", f"Erreur : Le bot n'a pas la permission de bannir {random_member.name}.")
        except discord.HTTPException as e:
            await ctx.send(f"Une erreur s'est produite lors du bannissement de {random_member.mention}: {e}")
            await log_command(ctx, ",rban", f"Erreur HTTP lors du bannissement de {random_member.name}: {e}")

    except discord.Forbidden:
    
        await ctx.send("Je n'ai pas la permission de voir les membres du serveur.")
        await log_command(ctx, ",rban", f"Erreur : Le bot n'a pas la permission de voir les membres du serveur.")
    except discord.HTTPException as e:
     
        await ctx.send(f"Une erreur s'est produite lors de la récupération des membres : {e}")
        await log_command(ctx, ",rban", f"Erreur HTTP lors de la récupération des membres : {e}")
    except Exception as e:
    
        await ctx.send(f"Une erreur inattendue s'est produite : {e}")
        await log_command(ctx, ",rban", f"Erreur inattendue : {e}")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, user: discord.Member = None, *, role_name: str = None):
    """Attribue ou retire un rôle à un utilisateur mentionné ou par ID"""


    if user is None or role_name is None:
        await ctx.send("Veuillez mentionner un utilisateur et spécifier le rôle à attribuer.")
        return


    role = None

   
    try:
        role_id = int(role_name) 
        role = discord.utils.get(ctx.guild.roles, id=role_id)
    except ValueError:

        role = discord.utils.get(ctx.guild.roles, name=role_name)

 
    if role is None:
        await ctx.send(f"Le rôle '{role_name}' n'existe pas dans ce serveur.")
        return


    if role.position >= ctx.author.top_role.position:
        await ctx.send("Vous ne pouvez pas attribuer ce rôle car il est plus élevé que le vôtre.")
        return


    if role in user.roles:
        try:
         
            await user.remove_roles(role)
            await ctx.send(f"Le rôle '{role.name}' a été retiré de {user.mention}.")
        except discord.Forbidden:
            await ctx.send("Je n'ai pas la permission de retirer ce rôle à cet utilisateur.")
        except discord.HTTPException as e:
            await ctx.send(f"Une erreur est survenue lors du retrait du rôle : {e}")
    else:
     
        try:
            await user.add_roles(role)
            await ctx.send(f"Le rôle '{role.name}' a été attribué à {user.mention}.")
        except discord.Forbidden:
            await ctx.send("Je n'ai pas la permission de donner ce rôle à cet utilisateur.")
        except discord.HTTPException as e:
            await ctx.send(f"Une erreur est survenue lors de l'attribution du rôle : {e}")

 
    await log_command(ctx, "role")

@bot.command(name='bview')
async def bview(ctx):
    try:
     
        banned_members_list = []
        
  
        bans = await ctx.guild.bans()

   
        if not bans:
            await ctx.send("Il n'y a pas de personnes bannies sur ce serveur.") 
            return
        
        
        for entry in bans:
            user = entry.user 
            if isinstance(user, discord.User): 
                banned_members_list.append(f"{user.name}#{user.discriminator}")

 
        banned_members = "\n".join(banned_members_list)
        
      
        if len(banned_members) > 2000: 
            await ctx.send("La liste des bannis est trop longue, voici la première partie :")
            first_part = "\n".join(banned_members_list[:10])  
            await ctx.send(first_part)
            await ctx.send("Il y a plus de bannis, contactez un administrateur pour plus d'informations.")
        else:
         
            await ctx.send(f"Voici les membres bannis du serveur :\n{banned_members}")
    
    except Exception as e:
        await ctx.send(f"Une erreur est survenue : {str(e)}")


keep_alive() # keep alive OPTION [Pas obligatoire.]
 
bot.run('') 