import os
import sqlite3
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
DB_NAME = "mvsd_guard.db"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def init_db():
    with sqlite3.connect(DB_NAME) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                details TEXT NOT NULL,
                source TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Under Review'
            )
        """)


@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print(f"MVSD Guard aktif: {bot.user}")
    except Exception as error:
        print(f"Komut eşitleme hatası: {error}")


@bot.tree.command(name="health", description="Botun çalışma durumunu kontrol et")
async def health(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🟢 MVSD Guard çalışıyor.",
        ephemeral=True
    )


@bot.tree.command(name="threat", description="Tehdit veritabanında arama yap")
@app_commands.describe(name="Aranacak executor veya script adı")
async def threat(interaction: discord.Interaction, name: str):
    with sqlite3.connect(DB_NAME) as db:
        rows = db.execute(
            """SELECT name, details, source, status
               FROM threats WHERE name LIKE ? LIMIT 5""",
            (f"%{name}%",)
        ).fetchall()

    if not rows:
        await interaction.response.send_message(
            f"🔎 `{name}` için kayıt bulunamadı. Bu, güvenli olduğu anlamına gelmez.",
            ephemeral=True
        )
        return

    result = "\n\n".join(
        f"**{n}** — {status}\n{details}\nKaynak: {source}"
        for n, details, source, status in rows
    )
    await interaction.response.send_message(result[:1900], ephemeral=True)


@bot.tree.command(name="scan", description="Mevcut rapor kayıtlarını kontrol et")
@app_commands.describe(username="İncelenecek Discord kullanıcı adı veya ID")
async def scan(interaction: discord.Interaction, username: str):
    await interaction.response.send_message(
        f"🔎 `{username}` için otomatik olarak doğrulanmış bir sonuç "
        "bulunmuyor. Bu ilk sürüm yalnızca kayıtlı tehditleri arar; "
        "henüz oyuncu raporu veritabanı bağlı değil. Tek başına kullanıcı "
        "adı hile kanıtı değildir.",
        ephemeral=True
    )


def main():
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN gizli değişkeni ayarlanmamış.")

    init_db()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
