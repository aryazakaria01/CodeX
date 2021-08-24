# Copyright (C) 2020 Frizzy.
# All rights reserved.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#

from telethon.errors.rpcerrorlist import YouBlockedUserError

from usercodex import codex

from . import edit_or_reply

plugin_category = "misc"


@codex.cod_cmd(
    pattern="ttvid ([\s\S]*)",
    command=("ttvid", plugin_category),
    info={
        "header": "To download tiktok video.",
        "description": "Download tiktok videos without watermark.",
        "examples": [
            "{tr}ttvid <link>",
        ],
    },
)
async def _(event):
    if event.fwd_from:
        return
    d_link = event.pattern_match.group(1)
    if "vm." and ".com" not in d_link:
        await edit_pr_reply(
            event,
            "`Sorry, the link is not supported. Please find another link.`\n**Example:** `vm.tiktok.com`",
        )
    else:
        await edit_or_reply(event, "```Processing...```")
    chat = "@ttsavebot"
    async with bot.conversation(chat) as conv:
        try:
            msg_start = await conv.send_message("/start")
            r = await conv.get_response()
            msg = await conv.send_message(d_link)
            details = await conv.get_response()
            video = await conv.get_response()
            """ - don't spam notif - """
            await bot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await edit_or_reply(
                event,
                f"#Failed ❌\n`Please unblock` @ttsavebot `then press /start and try again !`",
            )
            return
        await bot.send_file(event.chat_id, video, video_note=True)
        await event.client.delete_messages(
            conv.chat_id, [msg_start.id, r.id, msg.id, details.id, video.id]
        )
        await event.delete()
