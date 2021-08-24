import asyncio
from datetime import datetime

from ..core.managers import edit_or_reply
from . import PING_PIC, PING_TEXT, codex, hmention, reply_id

plugin_category = "tools"


@codex.cod_cmd(
    pattern="ping( -a|$)",
    command=("ping", plugin_category),
    info={
        "header": "check how long it takes to ping your userbot",
        "flags": {"-a": "average ping"},
        "usage": ["{tr}ping", "{tr}ping -a"],
    },
)
async def _(event):
    "To check ping"
    flag = event.pattern_match.group(1)
    start = datetime.now()
    if flag == " -a":
        codevent = await edit_or_reply(event, "`!....`")
        await asyncio.sleep(0.3)
        await codevent.edit("`..!..`")
        await asyncio.sleep(0.3)
        await codevent.edit("`....!`")
        end = datetime.now()
        tms = (end - start).microseconds / 1000
        ms = round((tms - 0.6) / 3, 3)
        await codevent.edit(f"**☞ Average Pong!**\n➥ {ms} ms")
    else:
        codevent = await edit_or_reply(event, "<b><i>☞ Pong!</b></i>", "html")
        end = datetime.now()
        ms = (end - start).microseconds / 1000
        await codevent.edit(
            f"<b><i>☞ Pong</b></i>\n➥ {ms} <b><i>ms\n➥ Bot of {hmention}</b></i>",
            parse_mode="html",
        )


@codex.cod_cmd(
    pattern="pping$",
    command=("pping", plugin_category),
    info={
        "header": "check how long it takes to ping your userbot.",
        "option": "To show media in this cmd you need to set PING_PIC with media link, get this by replying the media by .tgm",
        "usage": [
            "{tr}pping",
        ],
    },
)
async def _(event):
    "To check ping with pic"
    if event.fwd_from:
        return
    reply_to_id = await reply_id(event)
    start = datetime.now()
    cod = await edit_or_reply(
        event,
        "<b><i>“Everyone fails at who they are supposed to be. The measure of a person, of a hero…is how well they succeed at being who they are” !! ⚡ </b></i>",
        "html",
    )
    end = datetime.now()
    await asyncio.sleep(2.5)
    await cod.delete()
    ms = (end - start).microseconds / 1000
    if PING_PIC:
        caption = f"<b><i>{PING_TEXT}<i><b>\n<code> {ms} ms</code>\n <b><i>  Aѵҽղցҽɾ  ☞  {hmention}</b></i>"
        await event.client.send_file(
            event.chat_id,
            PING_PIC,
            caption=caption,
            parse_mode="html",
            reply_to=reply_to_id,
            link_preview=False,
            allow_cache=True,
        )
    else:
        await edit_or_reply(event, "<code>Add PING_PIC first nubh.<code>", "html")
