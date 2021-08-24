"""
@KENZO
For Codex,
Based Plugins from Ultroid & GeezUserBot.
Credits : @Abdul & @Vckyouu
If u kang and delete int based from, u gay dude.
"""
import asyncio
import csv
import random

from telethon.errors import (
    ChannelInvalidError,
    ChannelPrivateError,
    ChannelPublicGroupNaError,
)
from telethon.errors.rpcerrorlist import (
    UserAlreadyParticipantError,
    UserNotMutualContactError,
    UserPrivacyRestrictedError,
)
from telethon.tl import functions
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import InputPeerUser

from usercodex import codex

from ..core.managers import edit_delete, edit_or_reply

plugin_category = "utils"


async def get_chat_info(event):
    chat = event.pattern_match.group(1)
    chat_info = None
    if chat:
        try:
            chat = int(chat)
        except ValueError:
            pass
    if not chat:
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg.fwd_from and replied_msg.fwd_from.channel_id is not None:
                chat = replied_msg.fwd_from.channel_id
        else:
            chat = event.chat_id
    try:
        chat_info = await event.client(GetFullChatRequest(chat))
    except BaseException:
        try:
            chat_info = await event.client(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            await edit_or_reply(event, "`Invalid channel/group`")
            return None
        except ChannelPrivateError:
            await edit_or_reply(
                event, "`This is a private channel/group or I am banned from there`"
            )
            return None
        except ChannelPublicGroupNaError:
            await edit_or_reply(event, "`Channel or supergroup doesn't exist`")
            return None
        except (TypeError, ValueError):
            await edit_or_reply(event, "`Invalid channel/group`")
            return None
    return chat_info


@codex.cod_cmd(
    pattern="scrpall ([\s\S]*)",
    command=("scrpall", plugin_category),
    info={
        "header": "Dredge up members from other groups by using the group username",
        "usage": "{tr}scrpall <Username Group>",
        "example": "{tr}scrpall @codexsupportgroup",
    },
    groups_only=True,
)
async def get_users(event):
    sender = await event.get_sender()
    me = await event.client.get_me()
    if not sender.id == me.id:
        cod = await edit_or_reply(event, "`Processing...`")
    else:
        cod = await edit_or_reply(event, "`Processing...`")
    xedoc = await get_chat_info(event)
    chat = await event.get_chat()
    if event.is_private:
        return await edit_delete(
            cod, "`Sorry master, I Can't add users in here, Coz Private.`"
        )
    s = 0
    f = 0
    error = "None"

    await cod.edit("**TerminalStatus**\n\n`Collecting Users.......`")
    async for user in event.client.iter_participants(xedoc.full_chat.id):
        try:
            if error.startswith("Too"):
                return await cod.edit(
                    f"**Terminal Finished With Error**\n(`May Got Limit Error from telethon Please try agin Later`)\n**Error** : \n`{error}`\n\n• Invited `{s}` people \n• Failed to Invite `{f}` people"
                )
            await event.client(
                functions.channels.InviteToChannelRequest(channel=chat, users=[user.id])
            )
            s = s + 1
            await cod.edit(
                f"**Terminal Running...**\n\n• Invited `{s}` people \n• Failed to Invite `{f}` people\n\n**× LastError:** `{error}`"
            )
        except Exception as e:
            error = str(e)
            f = f + 1
    return await cod.edit(
        f"**Terminal Finished** \n\n• Successfully Invited `{s}` people \n• failed to invite `{f}` people"
    )


@codex.cod_cmd(
    pattern="getmember$",
    command=("getmember", plugin_category),
    info={
        "header": "Collect members data from the group.",
        "description": "This plugin is done before using the add member plugin.",
        "usage": "{tr}getmember",
    },
    groups_only=True,
)
async def getmembers(event):
    channel = event.chat_id
    xedoc = await edit_or_reply(event, "`Please wait...`")
    saint = event.client
    members = await saint.get_participants(channel, aggressive=True)

    with open("members.csv", "w", encoding="UTF-8") as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(["user_id", "hash"])
        for member in members:
            writer.writerow([member.id, member.access_hash])
    await edit_or_reply(xedoc, "`Successfully collect data members.`")


@codex.cod_cmd(
    pattern="addmember$",
    command=("addmember", plugin_category),
    info={
        "header": "Add your group members. (there's a limit)",
        "description": "This plugin is done after using the get member plugin.",
        "usage": "{tr}addmember",
    },
    groups_only=True,
)
async def addmembers(event):
    xedoc = await edit_or_reply(
        event, "`The process of adding members, starting from 0`"
    )
    channel = await event.get_chat()
    user_to_add = None
    saint = event.client
    x = []
    with open("members.csv", encoding="UTF-8") as f:
        rows = csv.reader(f, delimiter=",", lineterminator="\n")
        next(rows, None)
        for row in rows:
            i = {"user_id": int(row[0]), "hash": int(row[1])}
            x.append(i)
    y = 0
    for i in x:
        y += 1
        if y % 30 == 0:
            await edit_or_reply(
                event, f"`Has reached 30 members, wait until {200/60} min.`"
            )
            await asyncio.sleep(200)

        if user_to_add is None:
            try:
                user_to_add = InputPeerUser(i["user_id"], i["hash"])
            except BaseException:
                pass

        try:
            await saint(
                functions.channels.InviteToChannelRequest(
                    channel=channel, users=[user_to_add]
                )
            )
            await asyncio.sleep(random.randrange(5, 7))
            await edit_or_reply(event, f"`Prosess of adding {y} Members...`")
        except TypeError:
            y -= 1
            continue
        except UserAlreadyParticipantError:
            y -= 1
            continue
        except UserPrivacyRestrictedError:
            y -= 1
            continue
        except UserNotMutualContactError:
            y -= 1
            continue
