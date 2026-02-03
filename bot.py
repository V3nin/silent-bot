import discord
from discord import app_commands
from discord.ext import commands

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
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Bot connecté : {bot.user}")

def get_staff_log_channel(guild: discord.Guild):
    return discord.utils.get(guild.text_channels, name=STAFF_LOG_CHANNEL_NAME)

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
            f"{i.user.mention} bienvenue.\n"
            "Merci d’indiquer **le sujet de votre demande**."
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
            "Indique **l’offre choisie** et **le moyen de paiement**."
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
@tree.command(
    name="wl",
    description="Attribuer le rôle Client",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.checks.has_role(STAFF_ROLE_NAME)
async def wl(interaction: discord.Interaction, user: discord.Member):
    role = discord.utils.get(interaction.guild.roles, name=CLIENT_ROLE_NAME)
    if not role:
        await interaction.response.send_message("❌ Rôle Client introuvable.", ephemeral=True)
        return

    await user.add_roles(role)
    await interaction.response.send_message(f"✅ **{user}** est maintenant Client.")

    log = get_staff_log_channel(interaction.guild)
    if log:
        await log.send(f"👤 **{user}** whitelist par **{interaction.user}**")

# =========================
# RUN
# =========================
bot.run(TOKEN)
