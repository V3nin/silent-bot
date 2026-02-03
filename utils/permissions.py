from discord.ext import commands
from utils.whitelist import is_whitelisted

def wl_or_admin():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        return is_whitelisted(ctx.author.id)

    return commands.check(predicate)
