"""
@KENZO
For Codex,
Based Plugins from Ultroid.
If u kang and delete int based from, u gay dude.
"""
from telethon.tl.functions.channels import GetFullChannelRequest as getchat
from telethon.tl.functions.phone import CreateGroupCallRequest as startvc
from telethon.tl.functions.phone import DiscardGroupCallRequest as stopvc
from telethon.tl.functions.phone import GetGroupCallRequest as getvcalls
from telethon.tl.functions.phone import InviteToGroupCallRequest as invitetovc
from telethon.tl.types import ChatAdminRights

from usercodex import codex

from ..core.managers import edit_delete, edit_or_reply

plugin_category = "tools"


async def get_call(event):
    xorl = await event.client(getchat(event.chat_id))
    hxfy = await event.client(getvcalls(xorl.full_chat.call))
    return hxfy.call


def user_list(y, g):
    for a in range(0, len(y), g):
        yield y[a : a + g]


@codex.cod_cmd(
    pattern="startvc$",
    command=("startvc", plugin_category),
    info={
        "header": "Start a voice call in your group.",
        "usage": "{tr}startvc",
    },
    groups_only=True,
)
async def startvcalls(event):
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        return await edit_delete(event, "`Stupid, u're not Admin...`")
    new_rights = ChatAdminRights(invite_users=True)
    try:
        await event.client(startvc(event.chat_id))
        await event.edit("`Voice Call Group Started...`")
    except Exception as e:
        await event.edit(f"`{str(e)}`")


@codex.cod_cmd(
    pattern="offvc$",
    command=("offvc", plugin_category),
    info={
        "header": "Turn off voice call in your group.",
        "usage": "{tr}offvc",
    },
    groups_only=True,
)
async def turnoffvcalls(event):
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        return await edit_delete(event, "`Stupid, u're not Admin...`")
    new_rights = ChatAdminRights(invite_users=True)
    try:
        await event.client(stopvc(await get_call(event)))
        await event.edit("`Voice Chat Stopped...`")
    except Exception as e:
        await event.edit(f"`{str(e)}`")


@codex.cod_cmd(
    pattern="invitevc$",
    command=("invitevc", plugin_category),
    info={
        "header": "Invite all members to voice call.",
        "usage": "{tr}invitevc",
    },
    groups_only=True,
)
async def invitevcalls(event):
    xedoc = await edit_or_reply(event, "`Inviting members to voice call...`")
    users = []
    xed = 0
    async for m in event.client.iter_participants(event.chat_id):
        if not m.bot:
            users.append(m.id)
    code = list(user_list(users, 5))
    for p in code:
        try:
            await event.client(invitetovc(call=await get_call(event), users=p))
            xed += 5
        except BaseException:
            pass
    await edit_delete(xedoc, f"`Invited {xed} users.`")
