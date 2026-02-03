from discord.ext import commands
from utils.permissions import wl_or_admin

class Gen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @wl_or_admin()
    async def gen(self, ctx):
        await ctx.reply("🔐 Accès autorisé, génération en cours...")

def setup(bot):
    bot.add_cog(Gen(bot))

from utils.whitelist import is_valid

if not is_valid(interaction.user.id):
    await interaction.response.send_message(
        "⛔ Accès expiré ou non autorisé.", ephemeral=True
    )
    return

