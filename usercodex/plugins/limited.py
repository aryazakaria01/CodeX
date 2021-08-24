"""
@KENZO
For Codex,
Based Plugins from Ultroid.
If u kang and delete int based from, u gay dude.
"""
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError

from usercodex import codex

from ..core.managers import edit_or_reply

plugin_category = "utils"


@codex.cod_cmd(
    pattern="limited$",
    command=("limited", plugin_category),
    info={
        "header": "To check your telegram account. <Limited or not>",
        "description": "check your account limit via spam bots with these plugins",
        "usage": "{tr}limited",
    },
)
async def acclimited(event):
    chat = "@SpamBot"
    mesg = await edit_or_reply(event, "Checking If You Are Limited...")
    async with event.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=178220800)
            )
            await conv.send_message("/start")
            response = await response
            await event.client.send_read_acknowledge(chat)
        except YouBlockedUserError:
            await mesg.edit("Boss! Please Unblock @SpamBot ")
            return
        await mesg.edit(f"~ {response.message.message}")
