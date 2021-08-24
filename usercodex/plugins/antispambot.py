# Copyright (C) 2020  sandeep.n(π.$)
# baning spmmers plugin for catuserbot by @sandy1709
# included both cas(combot antispam service) and spamwatch (need to add more feaututres)

from requests import get
from telethon.errors import ChatAdminRequiredError
from telethon.events import ChatAction
from telethon.tl.types import ChannelParticipantsAdmins

from ..Config import Config
from ..sql_helper.gban_sql_helper import get_gbanuser, is_gbanned
from ..utils import is_admin
from . import BOTLOG, BOTLOG_CHATID, codex, edit_or_reply, logging, spamwatch

LOGS = logging.getLogger(__name__)
plugin_category = "admin"


def mentionuser(name, userid):
    return f"[{name}](tg://user?id={userid})"


if Config.ANTISPAMBOT_BAN:

    @codex.on(ChatAction())
    async def anti_spambot(event):  # sourcery no-metrics
        if not event.user_joined and not event.user_added:
            return
        user = await event.get_user()
        codadmin = await is_admin(event.client, event.chat_id, event.client.uid)
        if not codadmin:
            return
        codbanned = None
        adder = None
        ignore = None
        if event.user_added:
            try:
                adder = event.action_message.sender_id
            except AttributeError:
                return
        async for admin in event.client.iter_participants(
            event.chat_id, filter=ChannelParticipantsAdmins
        ):
            if admin.id == adder:
                ignore = True
                break
        if ignore:
            return
        if is_gbanned(user.id):
            codgban = get_gbanuser(user.id)
            if codgban.reason:
                hmm = await event.reply(
                    f"User: [CLICK HERE](tg://user?id={user.id})\nID: `{user.id}`\nWas GBanned by you for the reason: `{codgban.reason}`"
                )
            else:
                hmm = await event.reply(
                    f"User: [CLICK HERE](tg://user?id={user.id})\nID: `{user.id}`\nWas GBanned by you."
                )
            try:
                await event.client.edit_permissions(
                    event.chat_id, user.id, view_messages=False
                )
                codbanned = True
            except Exception as e:
                LOGS.info(e)
        if spamwatch and not codbanned:
            ban = spamwatch.get_ban(user.id)
            if ban:
                hmm = await event.reply(
                    f"User: [CLICK HERE](tg://user?id={user.id})\nID: `{user.id}`\nWas Banned by Spamwatch for the reason: `{ban.reason}`"
                )
                try:
                    await event.client.edit_permissions(
                        event.chat_id, user.id, view_messages=False
                    )
                    codbanned = True
                except Exception as e:
                    LOGS.info(e)
        if not codbanned:
            try:
                casurl = "https://api.cas.chat/check?user_id={}".format(user.id)
                data = get(casurl).json()
            except Exception as e:
                LOGS.info(e)
                data = None
            if data and data["ok"]:
                reason = (
                    f"[Banned by Combot Anti Spam](https://cas.chat/query?u={user.id})"
                )
                hmm = await event.reply(
                    f"User: [CLICK HERE](tg://user?id={user.id})\nID: `{user.id}`\nWas Banned by Combot Anti-Spam Service(CAS) for the reason check: {reason}"
                )
                try:
                    await event.client.edit_permissions(
                        event.chat_id, user.id, view_messages=False
                    )
                    codbanned = True
                except Exception as e:
                    LOGS.info(e)
        if BOTLOG and codbanned:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#ANTISPAMBOT\n"
                f"**User :** [CLICK HERE](tg://user?id={user.id})\n"
                f"**Chat :** {event.chat.title} (`{event.chat_id}`)\n"
                f"**Reason :** {hmm.text}",
            )


@codex.cod_cmd(
    pattern="cascheck$",
    command=("cascheck", plugin_category),
    info={
        "header": "To check the users who are banned in cas",
        "description": "When you use this cmd it will check every user in the group where you used whether \
        he is banned in cas (combat antispam service) and will show there names if they are flagged in cas",
        "usage": "{tr}cascheck",
    },
    groups_only=True,
)
async def caschecker(event):
    "Searches for cas(combot antispam service) banned users in group and shows you the list"
    codevent = await edit_or_reply(
        event,
        "`Checking any CAS (Combot Antispam Service) Banned users here, this may take several minutes too...`",
    )
    text = ""
    try:
        info = await event.client.get_entity(event.chat_id)
    except (TypeError, ValueError) as err:
        return await event.edit(str(err))
    try:
        cas_count, members_count = (0,) * 2
        banned_users = ""
        async for user in event.client.iter_participants(info.id):
            if banchecker(user.id):
                cas_count += 1
                if not user.deleted:
                    banned_users += (
                        f"👤 [CLICK HERE](tg://user?id={user.id}) - `{user.id}`\n"
                    )
                else:
                    banned_users += f"Deleted Account - `{user.id}`\n"
            members_count += 1
        text = "⚠️ **WARNING** ⚠️\n\nFound `{}` of `{}` Users are CAS Banned:\n".format(
            cas_count, members_count
        )
        text += banned_users
        if not cas_count:
            text = "No CAS Banned Users found!"
    except ChatAdminRequiredError:
        await codevent.edit("`CAS Check Failed: Admin privileges are required`")
        return
    except BaseException:
        await codevent.edit("`CAS Check Failed.`")
        return
    await codevent.edit(text)


@codex.cod_cmd(
    pattern="spamcheck$",
    command=("spamcheck", plugin_category),
    info={
        "header": "To check the users who are banned in spamwatch",
        "description": "When you use this command it will check every user in the group where you used whether \
        he is banned in spamwatch federation and will show there names if they are banned in spamwatch federation",
        "usage": "{tr}spamcheck",
    },
    groups_only=True,
)
async def caschecker(event):
    "Searches for spamwatch federation banned users in group and shows you the list"
    text = ""
    codevent = await edit_or_reply(
        event,
        "`Checking any Spamwatch Banned Users here, this may take several minutes too...`",
    )
    try:
        info = await event.client.get_entity(event.chat_id)
    except (TypeError, ValueError) as err:
        await event.edit(str(err))
        return
    try:
        cas_count, members_count = (0,) * 2
        banned_users = ""
        async for user in event.client.iter_participants(info.id):
            if spamchecker(user.id):
                cas_count += 1
                if not user.deleted:
                    banned_users += (
                        f"👤 [CLICK HERE](tg://user?id={user.id}) - `{user.id}`\n"
                    )
                else:
                    banned_users += f"Deleted Account - `{user.id}`\n"
            members_count += 1
        text = "⚠️ **WARNING** ⚠️\n\nFound `{}` of `{}` Users are Spamwatch Banned:\n".format(
            cas_count, members_count
        )
        text += banned_users
        if not cas_count:
            text = "No spamwatch Banned users found!"
    except ChatAdminRequiredError:
        await codevent.edit("`Spamwatch Check Failed: Admin privileges are required`")
        return
    except BaseException:
        await codevent.edit("`Spamwatch Check Failed.`")
        return
    await codevent.edit(text)


def banchecker(user_id):
    try:
        casurl = "https://api.cas.chat/check?user_id={}".format(user_id)
        data = get(casurl).json()
    except Exception as e:
        LOGS.info(e)
        data = None
    return bool(data and data["ok"])


def spamchecker(user_id):
    ban = None
    if spamwatch:
        ban = spamwatch.get_ban(user_id)
    return bool(ban)
