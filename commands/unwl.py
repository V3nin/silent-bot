from utils.whitelist import remove_wl

@tree.command(
    name="unwl",
    description="Retirer la whitelist d’un client",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.checks.has_role(STAFF_ROLE_NAME)
async def unwl(interaction: discord.Interaction, user: discord.Member):
    role = discord.utils.get(interaction.guild.roles, name=CLIENT_ROLE_NAME)

    if role and role in user.roles:
        await user.remove_roles(role)

    remove_wl(user.id)

    await interaction.response.send_message(
        f"❌ **{user}** retiré de la whitelist."
    )

    log = get_staff_log_channel(interaction.guild)
    if log:
        await log.send(
            f"👤 **{user}** UNWL par **{interaction.user}**"
        )
