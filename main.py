 import discord
from discord.ext import commands
from discord import app_commands
import os
import aiohttp

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} commandes slash synchronisées")
    except Exception as e:
        print(f"Erreur sync: {e}")

@bot.tree.command(name="anime", description="Cherche un anime et donne ses infos")
@app_commands.describe(nom="Nom de l'anime à chercher")
async def anime(interaction: discord.Interaction, nom: str):
    await interaction.response.defer()
    try:
        url = f"https://api.jikan.moe/v4/anime?q={nom}&limit=1&sfw=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

        if not data.get('data'):
            await interaction.followup.send(f"Aucun anime trouvé pour **{nom}** 😭")
            return

        anime_data = data['data'][0]

        title = anime_data.get('title', 'Inconnu')
        synopsis = anime_data.get('synopsis') or "Pas de synopsis disponible."
        if len(synopsis) > 500:
            synopsis = synopsis[:500] + "..."
        score = anime_data.get('score') or "N/A"
        episodes = anime_data.get('episodes') or "Inconnu"
        status = anime_data.get('status') or "Inconnu"
        anime_url = anime_data.get('url')
        image_url = anime_data['images']['jpg']['large_image_url']
        anime_type = anime_data.get('type') or "Inconnu"

        embed = discord.Embed(
            title=title,
            description=synopsis,
            color=discord.Color.purple(),
            url=anime_url
        )
        embed.add_field(name="⭐ Score", value=f"{score} / 10", inline=True)
        embed.add_field(name="📺 Épisodes", value=str(episodes), inline=True)
        embed.add_field(name="📅 Statut", value=status, inline=True)
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Type: {anime_type} | Source: MyAnimeList")

        await interaction.followup.send(embed=embed)
    except Exception as e:
        print(f"Erreur /anime: {e}")
        await interaction.followup.send(f"Erreur : {e}")

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
