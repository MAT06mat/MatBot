import discord

MISSING = discord.utils.MISSING

async def response(
    ctx: discord.ApplicationContext, 
    content: str = None,
    *,
    title: str = None, 
    embed: bool = False,
    embed_fields: list[discord.EmbedField] = None,
    ephemeral: bool = False,
    view: discord.ui.View = None,
    tts: bool = False,
    allowed_mentions: discord.AllowedMentions = None,
    file: discord.File = None,
    files: list[discord.File] = None,
    delete_after: float = None,
    ) -> discord.InteractionMessage | None:
    
    if not isinstance(ctx, discord.ApplicationContext):
        raise TypeError("ctx must be an ApplicationContext class")
    
    if embed:
        response_embed = discord.Embed(title=title, description=content, color=discord.Color.brand_green(), fields=embed_fields)
        kwargs = {'embed': response_embed, 'view': view, 'tts': tts, 'ephemeral': ephemeral, 'allowed_mentions': allowed_mentions, 'file': file, 'files': files, 'delete_after': delete_after}
    else:
        kwargs = {'content': content, 'view': view, 'tts': tts, 'ephemeral': ephemeral, 'allowed_mentions': allowed_mentions, 'file': file, 'files': files, 'delete_after': delete_after}
    
    kwargs = simplify(**kwargs)
    
    if ctx.response.is_done():
        await ctx.followup.send(**kwargs)
        return
    else:
        msg = await ctx.response.send_message(**kwargs)
        return await msg.original_response()


async def defer(
    ctx: discord.ApplicationContext,
    *, 
    ephemeral: bool = False,
    invisible: bool = True
    ) -> None:
    
    if not isinstance(ctx, discord.ApplicationContext):
        raise TypeError("ctx must be an ApplicationContext class")
    
    await ctx.response.defer(ephemeral=ephemeral, invisible=invisible)


def simplify(**kwargs):
    """Remove no used kwargs"""
    for kw in list(kwargs.keys()):
        if kwargs[kw] == None:
            del kwargs[kw]
    return kwargs