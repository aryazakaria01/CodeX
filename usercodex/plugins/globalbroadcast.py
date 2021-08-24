# © Copyright 2021 Lynx-Userbot LLC Company.
# GPL-3.0 License From Github
# Ported by @TeamSecret_Kz (KENZO)
# WARNING !!
# Credits by @TeamUltroid

from usercodex import codex

from ..core.managers import edit_or_reply

plugin_category = "tools"


@codex.cod_cmd(
    pattern="ggcast(?:\s|$)([\s\S]*)",
    command=("ggcast", plugin_category),
    info={
        "header": "Send messages to all groups you are in.",
        "usage": "{tr}ggcast <Text>",
        "examples": "{tr}ggcast Hello",
    },
)
async def gcast(event):
    """Adds given chat to global group cast."""
    xx = event.pattern_match.group(1)
    if not xx:
        return await edit_or_reply(xx, "`Please Give A Message.`")
    tt = event.text
    msg = tt[8:]
    kk = await edit_or_reply(event, "`Sending Group Messages Globally... 📢`")
    er = 0
    done = 0
    async for x in bot.iter_dialogs():
        if x.is_group and not x.is_user:
            chat = x.id
            try:
                done += 1
                await bot.send_message(chat, msg)
            except BaseException:
                er += 1
    await kk.edit(
        f"**✔️Succesfully** Send Message To : `{done}` Group.\n**❌Fail** Send Message To : `{er}` Group."
    )


@codex.cod_cmd(
    pattern="gucast(?:\s|$)([\s\S]*)",
    command=("gucast", plugin_category),
    info={
        "header": "Send messages to all user groups. <Private Message>",
        "usage": "{tr}gucast <Text>",
        "examples": "{tr}gucast Hello",
    },
)
async def gucast(event):
    """Adds given chat to global user cast."""
    xx = event.pattern_match.group(1)
    if not xx:
        return await edit_or_reply(xx, "`Please Give A Message`")
    tt = event.text
    msg = tt[8:]
    kk = await edit_or_reply(event, "`Sending Pivate Messages Globally... 📢`")
    er = 0
    done = 0
    async for x in bot.iter_dialogs():
        if x.is_user and not x.entity.bot:
            chat = x.id
            try:
                done += 1
                await bot.send_message(chat, msg)
            except BaseException:
                er += 1
    await kk.edit(
        f"**✔️Successfully** Send Message To : `{done}` Users.\n**❌Fail** Send Message To : `{er}` Users."
    )
