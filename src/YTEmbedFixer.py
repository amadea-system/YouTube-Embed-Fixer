"""

"""

import json
import logging
import re
import asyncio
from typing import Optional

import discord
from discord.ext import commands
import utils


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
log = logging.getLogger("YTEmbedFixer")


client = commands.Bot(command_prefix="yt!",
                      max_messages=5000,
                      description="A bot for fixing what Discord can't.\n",
                      owner_id=389590659335716867,
                      case_insensitive=True)


@client.event
async def on_ready():
    log.info('Connected using discord.py {}!'.format(discord.__version__))
    log.info('Username: {0.name}, ID: {0.id}'.format(client.user))
    log.info("Connected to {} servers.".format(len(client.guilds)))
    activity = discord.Game("Fixing what Discord can't since 12/5/2019.".format(client.command_prefix))
    await client.change_presence(status=discord.Status.online, activity=activity)

    log.info('------')


async def fix_yt_embed(message: discord.Message) -> Optional[discord.Embed]:
    regex_search_string = r'(?:https?://)?(?:www[.])?youtu(?:[.]be/|be[.]com/watch[?]v=)([^ ]*)'
    if len(message.embeds) > 0:
        matches = re.findall(regex_search_string, message.content)
        if len(matches) > 0:
            # We have a valid youtube link with Embed! Check if it broken.
            # We are lazy and trying to get this done quickly, so for the time being ignore all other embeds other than the first one.
            if message.embeds[0].type == "link":  # description == 'Enjoy the videos and music you love, upload original content, and share it all with friends, family, and the world on YouTube.':
                # We have a broken embed!

                await asyncio.sleep(2)  # Sleep for a bit to let PK delete the message if it a proxy message

                msg_check = discord.utils.get(client.cached_messages, id=message.id)  # Check if message was deleted by PK.
                if msg_check is not None:

                    html = await utils.get_video_webpage(matches[0])

                    video_url = "https://www.youtube.com/watch?v={}".format(matches[0])

                    video_image = await utils.get_video_image_url(html)
                    video_title = await utils.get_video_title(html)
                    author_name = await utils.get_author_name(html)
                    author_url = await utils.get_author_url(html)

                    if video_title is None and video_image is None and author_name is None and author_url is None:
                        #We got no info from the video. Prehaps the video is dead on youtube or the DOM has totally changed.
                        return None  # Don't post empty embed.
                    embed = build_embed(video_url, video_image, video_title, author_name, author_url)
                    await send_new_embed(message, embed)
    return None


async def send_new_embed(original_msg: discord.Message, embed: discord.Embed):
    webhook: discord.Webhook = await utils.get_webhook(client, original_msg.channel)

    try:
        await original_msg.delete()
        await webhook.send(content=original_msg.content, embed=embed, username=original_msg.author.display_name,
                           avatar_url=original_msg.author.avatar_url)
    except discord.errors.NotFound:
        pass  # SHOULD never get here because we check before deleting, but just in case... Don't post replacement.


def build_embed(_video_url: str, _video_image_url: Optional[str], _video_title: Optional[str],
                _author_name: Optional[str], _author_url: Optional[str]) -> discord.Embed:
    embed = discord.Embed(type="video", colour=discord.Colour.from_rgb(255, 0, 0))

    if _video_image_url is not None:
        embed.set_image(url=_video_image_url)

    if _author_name is not None:
        if _author_url is not None:
            embed.set_author(name=_author_name, url=_author_url)
        else:
            embed.set_author(name=_author_name)

    if _video_title is not None:
        embed.title = _video_title
        embed.url = _video_url
    return embed


# ---- Command Error Handling ----- #
@client.event
async def on_command_error(ctx, error):
    if type(error) == discord.ext.commands.NoPrivateMessage:
        await ctx.send("⚠ This command can not be used in DMs!!!")
        return
    elif type(error) == discord.ext.commands.CommandNotFound:
        await ctx.send("⚠ Invalid Command!!!")
        return
    elif type(error) == discord.ext.commands.MissingPermissions:
        await ctx.send("⚠ You need the **Manage Messages** permission to use this command".format(error.missing_perms))
        return
    elif type(error) == discord.ext.commands.MissingRequiredArgument:
        await ctx.send("⚠ {}".format(error))
    elif type(error) == discord.ext.commands.BadArgument:
        await ctx.send("⚠ {}".format(error))
    else:
        await ctx.send("⚠ {}".format(error))
        raise error


@client.event
async def on_message(message: discord.Message):
    await fix_yt_embed(message)
    await client.process_commands(message)


@client.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    await fix_yt_embed(after)


@client.command(name="invite", brief="Sends the invite link")
async def send_invite_link(ctx: commands.Context):
    # link = "https://discordapp.com/oauth2/authorize?client_id=500711320497160199&scope=bot&permissions=536882176"
    link = "https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=536882176".format(client.user.id)
    await ctx.send(link)


if __name__ == '__main__':

    with open('config.json') as json_data_file:
        config = json.load(json_data_file)

    client.command_prefix = config['bot_prefix']
    client.run(config['token'])

    log.info("cleaning Up and shutting down")
