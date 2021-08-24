import random
import re
import time
from platform import python_version

from telethon import version
from telethon.errors.rpcerrorlist import (
    MediaEmptyError,
    WebpageCurlFailedError,
    WebpageMediaEmptyError,
)
from telethon.events import CallbackQuery

from ..Config import Config
from ..core.managers import edit_or_reply
from ..helpers.functions import check_data_base_heal_th, codalive, get_readable_time
from ..helpers.utils import reply_id
from ..sql_helper.globals import gvarstatus
from . import StartTime, codex, codversion, mention

plugin_category = "utils"


@codex.cod_cmd(
    pattern="alive$",
    command=("alive", plugin_category),
    info={
        "header": "To check bot's alive status",
        "options": "To show media in this cmd you need to set ALIVE_PIC with media link, get this by replying the media by .tgm",
        "usage": [
            "{tr}alive",
        ],
    },
)
async def amireallyalive(event):
    "A kind of showing bot details"
    reply_to_id = await reply_id(event)
    uptime = await get_readable_time((time.time() - StartTime))
    _, check_sgnirts = check_data_base_heal_th()
    EMOJI = gvarstatus("ALIVE_EMOJI") or "•"
    ALIVE_TEXT = gvarstatus("ALIVE_TEXT") or "「 CODEX IS RUNNING SUCCESSFULLY 」"
    COD_IMG = gvarstatus("ALIVE_PIC")
    if COD_IMG:
        A_IMG = [x for x in COD_IMG.split()]
        PIC = random.choice(A_IMG)
        cod_caption = f"**{ALIVE_TEXT}**\n\n"
        cod_caption += f"=================================\n"
        cod_caption += f"{EMOJI} `User :` {mention}\n"
        cod_caption += f"`— — — — — >`\n"
        cod_caption += f"{EMOJI} `Uptime :` __{uptime}__\n"
        cod_caption += f"`— — — — — — — >`\n"
        cod_caption += f"{EMOJI} `Codex    :` __v{codversion}__\n"
        cod_caption += f"`— — — — — — — — >`\n"
        cod_caption += f"{EMOJI} `Telethon   :` __v{version.__version__}__\n"
        cod_caption += f"`— — — — — — — — — — >`\n"
        cod_caption += f"{EMOJI} `Python       :` __v{python_version()}__\n"
        cod_caption += f"`— — — — — — — — — — — — >`\n"
        cod_caption += f"{EMOJI} `Database       :` __{check_sgnirts}__\n"
        cod_caption += f"=================================\n"
        try:
            await event.client.send_file(
                event.chat_id, PIC, caption=cod_caption, reply_to=reply_to_id
            )
            await event.delete()
        except (WebpageMediaEmptyError, MediaEmptyError, WebpageCurlFailedError):
            return await edit_or_reply(
                event,
                f"**Media Value Error!!**\n__Change the link by __`.setdv`\n\n**__Can't get media from this link :-**__ `{PIC}`",
            )
    else:
        await edit_or_reply(
            event,
            f"**{ALIVE_TEXT}**\n\n"
            f"=================================\n"
            f"{EMOJI} `User :` {mention}\n"
            f"`— — — — — >`\n"
            f"{EMOJI} `Uptime :` __{uptime}__\n"
            f"`— — — — — — — >`\n"
            f"{EMOJI} `Codex    :` __v{codversion}__\n"
            f"`— — — — — — — — >`\n"
            f"{EMOJI} `Telethon   :` __v{version.__version__}__\n"
            f"`— — — — — — — — — — >`\n"
            f"{EMOJI} `Python       :` __v{python_version()}__\n"
            f"`— — — — — — — — — — — — >`\n"
            f"{EMOJI} `Database       :` __{check_sgnirts}__\n"
            f"=================================\n",
        )


@codex.cod_cmd(
    pattern="ialive$",
    command=("ialive", plugin_category),
    info={
        "header": "To check bot's alive status via inline mode",
        "options": "To show media in this cmd you need to set ALIVE_PIC with media link, get this by replying the media by .tgm",
        "usage": [
            "{tr}alive",
        ],
    },
)
async def amireallyalive(event):
    "A kind of showing bot details by your inline bot"
    reply_to_id = await reply_id(event)
    EMOJI = gvarstatus("ALIVE_EMOJI") or "•"
    cod_caption = f"**Codex** `is Up` and __Running...__\n\n"
    cod_caption += f"{EMOJI} `Telethon :` __v{version.__version__}__\n"
    cod_caption += f"{EMOJI} `Codex    :` __v{codversion}__\n"
    cod_caption += f"{EMOJI} `Python   :` __v{python_version()}__\n"
    cod_caption += f"{EMOJI} `User     :` {mention}\n"
    results = await event.client.inline_query(Config.TG_BOT_USERNAME, cod_caption)
    await results[0].click(event.chat_id, reply_to=reply_to_id, hide_via=True)
    await event.delete()


@codex.tgbot.on(CallbackQuery(data=re.compile(b"stats")))
async def on_plug_in_callback_query_handler(event):
    statstext = await codalive(StartTime)
    await event.answer(statstext, cache_time=0, alert=True)
