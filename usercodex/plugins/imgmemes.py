#  Copyright (C) 2020  sandeep.n(π.$)
# credits to @mrconfused (@sandy1709)
import asyncio
import os
import re

from usercodex import codex

from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import reply_id
from . import (
    changemymind,
    deEmojify,
    fakegs,
    kannagen,
    moditweet,
    reply_id,
    trumptweet,
    tweets,
)

plugin_category = "fun"


@codex.cod_cmd(
    pattern="fakegs(?:\s|$)([\s\S]*)",
    command=("fakegs", plugin_category),
    info={
        "header": "Fake google search meme",
        "usage": "{tr}fakegs search query ; what you mean text",
        "examples": "{tr}fakegs Codexuserbot ; One of the Popular userbot",
    },
)
async def nekobot(cod):
    "Fake google search meme"
    text = cod.pattern_match.group(1)
    reply_to_id = await reply_id(cod)
    if not text:
        if cod.is_reply and not reply_to_id.media:
            text = reply_to_id.message
        else:
            return await edit_delete(cod, "`What should i search in google.`", 5)
    code = await edit_or_reply(cod, "`Connecting to https://www.google.com/ ...`")
    text = deEmojify(text)
    if ";" in text:
        search, result = text.split(";")
    else:
        await edit_delete(
            cod,
            "__How should i create meme follow the syntax as show__ `.fakegs top text ; bottom text`",
            5,
        )
        return
    codfile = await fakegs(search, result)
    await asyncio.sleep(2)
    await cod.client.send_file(cod.chat_id, codfile, reply_to=reply_to_id)
    await code.delete()
    if os.path.exists(codfile):
        os.remove(codfile)


@codex.cod_cmd(
    pattern="trump(?:\s|$)([\s\S]*)",
    command=("trump", plugin_category),
    info={
        "header": "trump tweet sticker with given custom text",
        "usage": "{tr}trump <text>",
        "examples": "{tr}trump Codexuserbot is One of the Popular userbot",
    },
)
async def nekobot(cod):
    "trump tweet sticker with given custom text_"
    text = cod.pattern_match.group(1)
    text = re.sub("&", "", text)
    reply_to_id = await reply_id(cod)

    reply = await cod.get_reply_message()
    if not text:
        if cod.is_reply and not reply.media:
            text = reply.message
        else:
            return await edit_delete(cod, "**Trump : **`What should I tweet`", 5)
    code = await edit_or_reply(cod, "`Requesting trump to tweet...`")
    text = deEmojify(text)
    await asyncio.sleep(2)
    codfile = await trumptweet(text)
    await cod.client.send_file(cod.chat_id, codfile, reply_to=reply_to_id)
    await code.delete()
    if os.path.exists(codfile):
        os.remove(codfile)


@codex.cod_cmd(
    pattern="modi(?:\s|$)([\s\S]*)",
    command=("modi", plugin_category),
    info={
        "header": "modi tweet sticker with given custom text",
        "usage": "{tr}modi <text>",
        "examples": "{tr}modi Codexuserbot is One of the Popular userbot",
    },
)
async def nekobot(cod):
    "modi tweet sticker with given custom text"
    text = cod.pattern_match.group(1)
    text = re.sub("&", "", text)
    reply_to_id = await reply_id(cod)

    reply = await cod.get_reply_message()
    if not text:
        if cod.is_reply and not reply.media:
            text = reply.message
        else:
            return await edit_delete(cod, "**Modi : **`What should I tweet`", 5)
    code = await edit_or_reply(cod, "Requesting modi to tweet...")
    text = deEmojify(text)
    await asyncio.sleep(2)
    codfile = await moditweet(text)
    await cod.client.send_file(cod.chat_id, codfile, reply_to=reply_to_id)
    await code.delete()
    if os.path.exists(codfile):
        os.remove(codfile)


@codex.cod_cmd(
    pattern="cmm(?:\s|$)([\s\S]*)",
    command=("cmm", plugin_category),
    info={
        "header": "Change my mind banner with given custom text",
        "usage": "{tr}cmm <text>",
        "examples": "{tr}cmm Codexuserbot is One of the Popular userbot",
    },
)
async def nekobot(cod):
    text = cod.pattern_match.group(1)
    text = re.sub("&", "", text)
    reply_to_id = await reply_id(cod)

    reply = await cod.get_reply_message()
    if not text:
        if cod.is_reply and not reply.media:
            text = reply.message
        else:
            return await edit_delete(cod, "`Give text to write on banner, man`", 5)
    code = await edit_or_reply(cod, "`Your banner is under creation wait a sec...`")
    text = deEmojify(text)
    await asyncio.sleep(2)
    codfile = await changemymind(text)
    await cod.client.send_file(cod.chat_id, codfile, reply_to=reply_to_id)
    await code.delete()
    if os.path.exists(codfile):
        os.remove(codfile)


@codex.cod_cmd(
    pattern="kanna(?:\s|$)([\s\S]*)",
    command=("kanna", plugin_category),
    info={
        "header": "kanna chan sticker with given custom text",
        "usage": "{tr}kanna text",
        "examples": "{tr}kanna Codexuserbot is One of the Popular userbot",
    },
)
async def nekobot(cod):
    "kanna chan sticker with given custom text"
    text = cod.pattern_match.group(1)
    text = re.sub("&", "", text)
    reply_to_id = await reply_id(cod)

    reply = await cod.get_reply_message()
    if not text:
        if cod.is_reply and not reply.media:
            text = reply.message
        else:
            return await edit_delete(cod, "**Kanna : **`What should i show you`", 5)
    code = await edit_or_reply(cod, "`Kanna is writing your text...`")
    text = deEmojify(text)
    await asyncio.sleep(2)
    codfile = await kannagen(text)
    await cod.client.send_file(cod.chat_id, codfile, reply_to=reply_to_id)
    await code.delete()
    if os.path.exists(codfile):
        os.remove(codfile)


@codex.cod_cmd(
    pattern="tweet(?:\s|$)([\s\S]*)",
    command=("tweet", plugin_category),
    info={
        "header": "The desired person tweet sticker with given custom text",
        "usage": "{tr}tweet <username> ; <text>",
        "examples": "{tr}tweet iamsrk ; Codexuserbot is One of the Popular userbot",
    },
)
async def nekobot(cod):
    "The desired person tweet sticker with given custom text"
    text = cod.pattern_match.group(1)
    text = re.sub("&", "", text)
    reply_to_id = await reply_id(cod)

    reply = await cod.get_reply_message()
    if not text:
        if cod.is_reply and not reply.media:
            text = reply.message
        else:
            return await edit_delete(
                cod,
                "what should I tweet? Give some text and format must be like `.tweet username ; your text` ",
                5,
            )
    if ";" in text:
        username, text = text.split(";")
    else:
        await edit_delete(
            cod,
            "__what should I tweet? Give some text and format must be like__ `.tweet username ; your text`",
            5,
        )
        return
    code = await edit_or_reply(cod, f"`Requesting {username} to tweet...`")
    text = deEmojify(text)
    await asyncio.sleep(2)
    codfile = await tweets(text, username)
    await cod.client.send_file(cod.chat_id, codfile, reply_to=reply_to_id)
    await code.delete()
    if os.path.exists(codfile):
        os.remove(codfile)
