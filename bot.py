import discord
import asyncio
import sqlite3
import subprocess
import random
import requests
import string
import time
from discord import app_commands
from discord.ext import commands

def init_keys_db():
    conn = sqlite3.connect(KEYS_DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS access_keys (
            token TEXT PRIMARY KEY,
            pubkey TEXT NOT NULL,
            expires_at INTEGER,
            created_at INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def generate_token():
    parts = [
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        for _ in range(4)
    ]
    return "SILENT-" + "-".join(parts)

def extract_pubkey(conf: str) -> str:
    for line in conf.splitlines():
        if line.startswith("PublicKey"):
            return line.split("=")[1].strip()
    raise ValueError("PublicKey not found")

def save_access_key(token, pubkey, expires_at):
    conn = sqlite3.connect(KEYS_DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO access_keys(token, pubkey, expires_at, created_at) VALUES (?,?,?,?)",
        (token, pubkey, expires_at, int(time.time()))
    )
    conn.commit()
    conn.close()

# =========================
# CONFIG
# =========================
import os
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1467924864118689853
TICKET_CATEGORY_ID = 1467934909665513595

STAFF_ROLE_NAME = "𝘝𝘦𝘯𝘥𝘦𝘶𝘳"
CLIENT_ROLE_NAME = "𝘊𝘭𝘪𝘦𝘯𝘵𝘴"
STAFF_LOG_CHANNEL_NAME = "staff-logs"
KEYS_DB_PATH = "./keys.db"
ADD_PEER_BIN = "/usr/local/bin/add-peer-conf"
API_BASE_URL = "http://68.183.0.250:8080"

# =========================
# BOT INIT
# =========================
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    init_keys_db()
    # ⚠️ SUPPRESSION DES COMMANDES GLOBALES
    tree.clear_commands(guild=None)
    await tree.sync()

    print("🔥 Global slash commands PURGED")

    # ✅ Recréation des commandes du serveur
    guild = discord.Object(id=GUILD_ID)
    await tree.sync(guild=guild)

    print("✅ Guild slash commands synced")
    print(f"Bot connecté : {bot.user}")
# =========================
# TICKET CLIENTS
# =========================
async def create_client_ticket(guild, user, days_remaining):
    category = guild.get_channel(TICKET_CATEGORY_ID)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)
    if staff_role:
        overwrites[staff_role] = discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True
        )

    channel_name = f"{days_remaining}j-{user.name}".lower()

    channel = await guild.create_text_channel(
        name=channel_name,
        category=category,
        overwrites=overwrites
    )

    await channel.send(
        f"🔐 **Espace personnel de {user.mention}**\n\n"
        f"📅 Durée restante : **{days_remaining} jour(s)**\n\n"
        "⚠️ Ce salon est **confidentiel**.\n"
        "La clé VPN sera envoyée ici."
    )

    return channel
# =========================
# TICKET PANEL
# =========================
@tree.command(
    name="ticket-panel",
    description="Afficher le panneau de tickets",
    guild=discord.Object(id=GUILD_ID)
)
async def ticket_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 Support SILENT VPN",
        description="Clique sur le bouton ci-dessous pour ouvrir un ticket.",
        color=0x8B0000
    )

    view = discord.ui.View(timeout=None)

    async def create_ticket(i: discord.Interaction):
        guild = i.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            i.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{i.user.name}",
            category=category,
            overwrites=overwrites
        )

        await channel.send(
            f"{i.user.mention} merci pour ton intérêt.\n"
            "Indique **l’offre choisie** et **le moyen de paiement**.",
            view=CloseTicketView()
)


        log = get_staff_log_channel(guild)
        if log:
            await log.send(f"🎫 Ticket créé par **{i.user}** → {channel.mention}")

        await i.response.send_message("✅ Ticket créé.", ephemeral=True)

    button = discord.ui.Button(label="Ouvrir un ticket", style=discord.ButtonStyle.danger)
    button.callback = create_ticket
    view.add_item(button)

    await interaction.response.send_message(embed=embed, view=view)

# =========================
# PRICING
# =========================
@tree.command(
    name="embed_pricing",
    description="Afficher les tarifs SILENT VPN",
    guild=discord.Object(id=GUILD_ID)
)
async def embed_pricing(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔒 SILENT VPN — Tarifs",
        description=(
            "**Architecture no-log stricte**\n"
            "Aucun trafic • Aucun DNS • Aucune activité\n\n"
            "🟢 **7 jours — 6 €**\n"
            "• 1 appareil\n\n"
            "🔵 **30 jours — 15 € (Recommandé)**\n"
            "• Jusqu’à 2 appareils\n\n"
            "🟣 **12 mois — 90 €**\n"
            "• Jusqu’à 3 appareils\n\n"
            "🔴 **Accès privé — 140 €**\n"
            "• Jusqu’à 5 appareils\n\n"
            "⚠️ Aucun anonymat absolu. Activités illégales interdites."
        ),
        color=0x8B0000
    )

    view = discord.ui.View(timeout=None)

    async def buy_callback(i: discord.Interaction):
        guild = i.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            i.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"achat-{i.user.name}",
            category=category,
            overwrites=overwrites
        )

        await channel.send(
    f"{i.user.mention} merci pour ton intérêt.\n"
    "Indique **l’offre choisie** et **le moyen de paiement**.",
    view=CloseTicketView()
)

        log = get_staff_log_channel(guild)
        if log:
            await log.send(f"🛒 Ticket achat ouvert par **{i.user}** → {channel.mention}")

        await i.response.send_message("🛒 Ticket d’achat ouvert.", ephemeral=True)

    button = discord.ui.Button(label="🛒 Acheter maintenant", style=discord.ButtonStyle.success)
    button.callback = buy_callback
    view.add_item(button)

    await interaction.response.send_message(embed=embed, view=view)

# =========================
# PAYMENTS
# =========================
@tree.command(
    name="embed_payments",
    description="Afficher les moyens de paiement",
    guild=discord.Object(id=GUILD_ID)
)
async def embed_payments(interaction: discord.Interaction):
    embed = discord.Embed(
        title="💳 Moyens de paiement — SILENT VPN",
        color=0x8B0000
    )

    embed.add_field(name="PayPal", value="https://www.paypal.me/EnfantDivin", inline=False)
    embed.add_field(name="ETH / BNB", value="`0x31740bDC64C795E16d46e1eC72E4eB3ef422275F`", inline=False)
    embed.add_field(name="Bitcoin", value="`bc1q2xkwz7aczxfymjajhvf3a50kfk3pm25tvyqeay`", inline=False)
    embed.add_field(name="Solana", value="`DLqPtX1XSoeLr9SSFFubNSTkPD84ce8NREmMGhT9znRz`", inline=False)

    await interaction.response.send_message(embed=embed)

# =========================
# RULES
# =========================
@tree.command(
    name="embed_rules",
    description="Afficher le règlement",
    guild=discord.Object(id=GUILD_ID)
)
async def embed_rules(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 Règlement SILENT VPN",
        description=(
            "• Activités illégales interdites\n"
            "• Revente interdite\n"
            "• Clés personnelles\n"
            "• Expiration automatique\n"
            "• Respect du staff"
        ),
        color=0x8B0000
    )
    await interaction.response.send_message(embed=embed)

# =========================
# PRIVACY
# =========================
@tree.command(
    name="embed_privacy",
    description="Politique de confidentialité",
    guild=discord.Object(id=GUILD_ID)
)
async def embed_privacy(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔐 Politique de confidentialité",
        description=(
            "SILENT VPN applique une politique **no-log stricte**.\n"
            "Aucun journal de trafic, DNS ou activité.\n"
            "Les accès expirés sont définitivement révoqués."
        ),
        color=0x8B0000
    )
    await interaction.response.send_message(embed=embed)

# =========================
# UPDATE
# =========================
@tree.command(
    name="update",
    description="Annonce une mise à jour",
    guild=discord.Object(id=GUILD_ID)
)
async def update(interaction: discord.Interaction, message: str):
    embed = discord.Embed(
        title="🔄 Mise à jour",
        description=message,
        color=0x8B0000
    )
    await interaction.response.send_message(embed=embed)

    log = get_staff_log_channel(interaction.guild)
    if log:
        await log.send(f"🔄 Update postée par **{interaction.user}**")

# =========================
# WL
# =========================
from utils.whitelist import add
# + la fonction create_client_ticket

@tree.command(
    name="wl",
    description="Whitelist un client et ouvre son ticket privé",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.checks.has_role(STAFF_ROLE_NAME)
async def wl(interaction, user: discord.Member, jours: int):
    role = discord.utils.get(interaction.guild.roles, name=CLIENT_ROLE_NAME)

    await user.add_roles(role)
    add(user.id, jours)

    ticket = await create_client_ticket(
        interaction.guild,
        user,
        jours
    )

    await interaction.response.send_message(
        f"✅ {user.mention} whitelist **{jours} jour(s)**.\n"
        f"🎫 Ticket personnel créé : {ticket.mention}",
        ephemeral=True
    )
# =========================
# UNWL
# =========================


from utils.whitelist import remove

@tree.command(
    name="unwl",
    description="Retirer un client de la whitelist",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.checks.has_role(STAFF_ROLE_NAME)
async def unwl(
    interaction: discord.Interaction,
    user: discord.Member
):
    role = discord.utils.get(interaction.guild.roles, name=CLIENT_ROLE_NAME)
    if role and role in user.roles:
        await user.remove_roles(role)

    remove(user.id)

    await interaction.response.send_message(
        f"❌ {user.mention} retiré de la whitelist."
    )

# =========================
# LOCK
# =========================
@tree.command(
    name="lock",
    description="Verrouiller le salon (empêche les messages)",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.checks.has_role(STAFF_ROLE_NAME)
async def lock(interaction: discord.Interaction):
    channel = interaction.channel
    guild = interaction.guild

    if not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message(
            "❌ Cette commande fonctionne uniquement dans un salon texte.",
            ephemeral=True
        )
        return

    overwrites = channel.overwrites

    # Bloque @everyone
    overwrites[guild.default_role] = discord.PermissionOverwrite(
        send_messages=False
    )

    await channel.edit(overwrites=overwrites)

    await interaction.response.send_message(
        f"🔒 Salon **{channel.name}** verrouillé."
    )
# =========================
# UNLOCK
# =========================

@tree.command(
    name="unlock",
    description="Déverrouiller le salon",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.checks.has_role(STAFF_ROLE_NAME)
async def unlock(interaction: discord.Interaction):
    channel = interaction.channel
    guild = interaction.guild

    if not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message(
            "❌ Cette commande fonctionne uniquement dans un salon texte.",
            ephemeral=True
        )
        return

    overwrites = channel.overwrites

    # Supprime le blocage de @everyone
    if guild.default_role in overwrites:
        overwrites[guild.default_role] = discord.PermissionOverwrite(
            send_messages=None
        )

    await channel.edit(overwrites=overwrites)

    await interaction.response.send_message(
        f"🔓 Salon **{channel.name}** déverrouillé."
    )
# =========================
# CLOSE
# =========================
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔒 Fermer le ticket",
        style=discord.ButtonStyle.danger,
        custom_id="close_ticket"
    )
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        await interaction.response.send_message(
            "🗑️ Ticket fermé dans 3 secondes...",
            ephemeral=True
        )
        await asyncio.sleep(3)
        await channel.delete()
# =========================
# GENKEY
# =========================

@tree.command(
    name="genkey",
    description="Génère une clé VPN (jours ou infinite)",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.checks.has_role(STAFF_ROLE_NAME)
async def genkey(interaction: discord.Interaction, durée: str):
    await interaction.response.defer(ephemeral=True)

    payload = {
        "duration": durée
    }

    try:
        r = requests.post(
            "http://68.183.0.250:8080/genkey",
            json=payload,
            timeout=10
        )
    except Exception as e:
        await interaction.followup.send(
            "❌ Impossible de contacter le serveur VPN.",
            ephemeral=True
        )
        return

    if r.status_code != 200:
        await interaction.followup.send(
            "❌ Erreur serveur lors de la génération.",
            ephemeral=True
        )
        return

    data = r.json()

    await interaction.followup.send(
        f"🔐 **Clé SILENT VPN générée**\n\n"
        f"**Clé :** `{data['token']}`\n"
        f"**Durée :** {data['label']}",
        ephemeral=True
    )
# =========================
# RUN
# =========================
bot.run(TOKEN)
