from utils.whitelist import add_wl

@tree.command(
    name="wl",
    description="Whitelist un client avec expiration",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.checks.has_role(STAFF_ROLE_NAME)
async def wl(
    interaction: discord.Interaction,
    user: discord.Member,
    jours: int
):
    role = discord.utils.get(interaction.guild.roles, name=CLIENT_ROLE_NAME)
    if not role:
        await interaction.response.send_message("❌ Rôle Client introuvable.", ephemeral=True)
        return

    duration_seconds = jours * 86400
    add_wl(user.id, duration_seconds)

    await user.add_roles(role)

    await interaction.response.send_message(
        f"✅ **{user}** whitelist pour **{jours} jour(s)**."
    )

    log = get_staff_log_channel(interaction.guild)
    if log:
        await log.send(
            f"👤 **{user}** WL {jours}j par **{interaction.user}**"
        )
