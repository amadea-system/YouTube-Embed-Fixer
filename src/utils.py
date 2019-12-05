"""

"""

import logging
import re
from typing import Optional

import discord
from discord.ext import commands
import aiohttp

log = logging.getLogger("YTEmbedFixer.utils")


def find_in_html(_video_html: str, regex_search: str) -> Optional[str]:
    matches = re.findall(regex_search, _video_html)
    if len(matches) > 0:
        # Assume there is only 1 match because there SHOULD only be one match......
        match = matches[0]
        return match
    else:
        return None


async def get_video_webpage(video_id: str) -> Optional[str]:
    video_url = "https://www.youtube.com/watch?v={}".format(video_id)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as r:
                if r.status == 200:
                    return await r.text()  # Got the html of the YT page.
                else:
                    logging.warning("Could not scrape YT page!")
                    return None
    except aiohttp.ClientError as e:
        logging.warning("Could not scrape YT page!\n{}".format(e))
        return None


async def get_video_image_url(video_html: str) -> Optional[str]:
    regex_search_string = r'<meta name="twitter:image" content="(.*)">'
    return find_in_html(video_html, regex_search_string)


async def get_video_title(video_html: str) -> Optional[str]:
    """
    Returns the title of the Video
    """
    regex_search_string = r'<meta name="twitter:title" content="(.*)">'
    return find_in_html(video_html, regex_search_string)


async def get_author_name(video_html: str) -> Optional[str]:
    """
    Returns a Tuple[Author name, Author channel URL]
    """
    regex_search_string = r'<script type="application\/ld\+json" >(?:\n.*)+"name": "(.+)"'
    return find_in_html(video_html, regex_search_string)


async def get_author_url(video_html: str) -> Optional[str]:
    """
    Returns a Tuple[Author name, Author channel URL]
    """
    regex_search_string = r'<script type="application\/ld\+json" >(?:\n.*)+"@id": "(.+)",'
    url = find_in_html(video_html, regex_search_string)
    if url is not None:
        fixed_url = url.replace("\\", "")
        return fixed_url

    return None


async def get_video_description(video_html: str) -> Optional[str]:
    """
    Returns the description of the video
    This is completly unneeded, but discord has it in their embed so why not....
    """
    regex_search_string = r'<meta name="twitter:description" content="(.*)">'
    return find_in_html(video_html, regex_search_string)


async def get_webhook(_client: commands.Bot, channel: discord.TextChannel) -> discord.Webhook:
    """
    Gets the existing webhook from the guild and channel specified. Creates one if it does not exist.
    """

    existing_webhooks = await channel.webhooks()
    webhook = discord.utils.get(existing_webhooks, user=_client.user)

    if webhook is None:
        log.warning("Webhook did not exist in channel {}! Creating new webhook!".format(channel.name))
        webhook = await channel.create_webhook(name="YTEmbedBot", reason="Creating webhook for YTEmbedBot")

    return webhook
