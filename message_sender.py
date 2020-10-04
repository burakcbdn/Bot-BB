async def send_embedded(ctx, content):
    embed = discord.Embed(color=0x00ff00, description=content)
    await ctx.send(embed=embed)