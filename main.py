import os, json, threading
import discord
from discord.ext import commands
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "World Otaku Online 🌸"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix="!", intents=intents)

STATS_FILE="stats.json"
def load_stats():
    try:
        with open(STATS_FILE,"r") as f: return json.load(f)
    except: return {"users":{},"channels":{},"total":0}
def save_stats(d):
    with open(STATS_FILE,"w") as f: json.dump(d,f,indent=4)

@bot.event
async def on_ready():
    print(f"Connecté {bot.user}")
    await bot.tree.sync()
    print(" /stats prêt!")

@bot.event
async def on_message(msg):
    if msg.author.bot or not msg.guild: return
    data=load_stats()
    data["users"][str(msg.author.id)]=data["users"].get(str(msg.author.id),0)+1
    data["channels"][str(msg.channel.id)]=data["channels"].get(str(msg.channel.id),0)+1
    data["total"]+=1
    save_stats(data)
    await bot.process_commands(msg)

async def build_stats(guild):
    data=load_stats()
    total=guild.member_count
    bots=len([m for m in guild.members if m.bot])
    online=len([m for m in guild.members if m.status!=discord.Status.offline])
    top=sorted(data["users"].items(), key=lambda x:x[1], reverse=True)[:5]
    txt=""
    for i,(uid,c) in enumerate(top,1):
        m=guild.get_member(int(uid))
        txt+=f"**{i}. {m.display_name if m else uid}** - {c} msgs\n"
    if not txt: txt="Pas encore de données"
    if data["channels"]:
        top_id=max(data["channels"], key=data["channels"].get)
        ch=guild.get_channel(int(top_id))
        top_chan=f"{ch.mention} ({data['channels'][top_id]})" if ch else "Inconnu"
    else: top_chan="Aucun"
    emb=discord.Embed(title=f"📊 Stats de {guild.name}", color=discord.Color.purple())
    emb.set_thumbnail(url=guild.icon.url if guild.icon else None)
    emb.add_field(name="👥 Membres", value=f"Total: {total}\nHumains: {total-bots}\nBots: {bots}", inline=True)
    emb.add_field(name="🟢 Présences", value=f"En ligne: {online}\nOffline: {total-online}", inline=True)
    emb.add_field(name="💬 Top Parleurs", value=txt, inline=False)
    emb.add_field(name="🔥 Salon actif", value=top_chan, inline=True)
    emb.add_field(name="✉️ Total", value=f"{data['total']} msgs", inline=True)
    return emb

@bot.tree.command(name="stats", description="Affiche les stats du serveur")
async def stats(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(embed=await build_stats(interaction.guild))

@bot.tree.command(name="states", description="Alias de /stats")
async def states(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(embed=await build_stats(interaction.guild))

threading.Thread(target=run_flask).start()
bot.run(os.getenv("DISCORD_TOKEN"))
