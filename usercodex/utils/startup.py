import glob
import os
import sys
from asyncio.exceptions import CancelledError
from datetime import timedelta
from pathlib import Path
from platform import python_version

import requests
from telethon import Button, functions, types, utils, version

from usercodex import BOTLOG, BOTLOG_CHATID, PM_LOGGER_GROUP_ID

from .. import codversion
from ..Config import Config
from ..core.logger import logging
from ..core.session import codex
from ..helpers.utils import install_pip
from ..sql_helper.global_collection import (
    del_keyword_collectionlist,
    get_item_collectionlist,
)
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from .pluginmanager import load_module
from .tools import create_supergroup

LOGS = logging.getLogger("CodexUserbot")
cmdhr = Config.COMMAND_HAND_LER


async def setup_bot():
    """
    To set up bot for usercodex
    """
    try:
        await codex.connect()
        config = await codex(functions.help.GetConfigRequest())
        for option in config.dc_options:
            if option.ip_address == codex.session.server_address:
                if codex.session.dc_id != option.id:
                    LOGS.warning(
                        f"Fixed DC ID in session from {codex.session.dc_id}"
                        f" to {option.id}"
                    )
                codex.session.set_dc(option.id, option.ip_address, option.port)
                codex.session.save()
                break
        bot_details = await codex.tgbot.get_me()
        Config.TG_BOT_USERNAME = f"@{bot_details.username}"
        # await codex.start(bot_token=Config.TG_BOT_USERNAME)
        codex.me = await codex.get_me()
        codex.uid = codex.tgbot.uid = utils.get_peer_id(codex.me)
        if Config.OWNER_ID == 0:
            Config.OWNER_ID = utils.get_peer_id(codex.me)
    except Exception as e:
        LOGS.error(f"STRING_SESSION - {str(e)}")
        sys.exit()


async def startupmessage():
    """
    Start up message in telegram logger group
    """
    try:
        if BOTLOG:
            Config.CODLOGO = await codex.tgbot.send_file(
                BOTLOG_CHATID,
                "https://telegra.ph/file/c6f5ed625c0fb1c2480f7.jpg",
                caption="**Codex has been started successfully.**",
                buttons=[(Button.url("Support", "https://t.me/CodexSupportGroup"),)],
            )
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        msg_details = list(get_item_collectionlist("restart_update"))
        if msg_details:
            msg_details = msg_details[0]
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        if msg_details:
            await codex.check_testcases()
            message = await codex.get_messages(msg_details[0], ids=msg_details[1])
            text = f"[Codex](t.me/CodexUserbot) **is Back up and Running...**\n\n"
            text += f"`Telethon :` __v{version.__version__}__\n"
            text += f"`Python   :` __v{python_version()}__\n"
            text += f"`Codex    :`  __v{codversion}__\n"
            await codex.edit_message(msg_details[0], msg_details[1], text)
            if gvarstatus("restartupdate") is not None:
                await codex.send_message(
                    msg_details[0],
                    f"{cmdhr}ping",
                    reply_to=msg_details[1],
                    schedule=timedelta(seconds=10),
                )
            del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
        return None


# don't know work or not just a try in future will use sleep
async def ipchange():
    """
    Just to check if ip change or not
    """
    newip = (requests.get("https://httpbin.org/ip").json())["origin"]
    if gvarstatus("ipaddress") is None:
        addgvar("ipaddress", newip)
        return None
    oldip = gvarstatus("ipaddress")
    if oldip != newip:
        delgvar("ipaddress")
        LOGS.info("Ip Change detected")
        try:
            await codex.disconnect()
        except (ConnectionError, CancelledError):
            pass
        return "ip change"


async def add_bot_to_logger_group(chat_id):
    """
    To add bot to logger groups
    """
    bot_details = await codex.tgbot.get_me()
    try:
        await codex(
            functions.messages.AddChatUserRequest(
                chat_id=chat_id,
                user_id=bot_details.username,
                fwd_limit=1000000,
            )
        )
    except BaseException:
        try:
            await codex(
                functions.channels.InviteToChannelRequest(
                    channel=chat_id,
                    users=[bot_details.username],
                )
            )
        except Exception as e:
            LOGS.error(str(e))


async def load_plugins(folder):
    """
    To load plugins from the mentioned folder
    """
    path = f"usercodex/{folder}/*.py"
    files = glob.glob(path)
    files.sort()
    for name in files:
        with open(name) as f:
            path1 = Path(f.name)
            shortname = path1.stem
            try:
                if shortname.replace(".py", "") not in Config.NO_LOAD:
                    flag = True
                    check = 0
                    while flag:
                        try:
                            load_module(
                                shortname.replace(".py", ""),
                                plugin_path=f"usercodex/{folder}",
                            )
                            break
                        except ModuleNotFoundError as e:
                            install_pip(e.name)
                            check += 1
                            if check > 5:
                                break
                else:
                    os.remove(Path(f"usercodex/{folder}/{shortname}.py"))
            except Exception as e:
                os.remove(Path(f"usercodex/{folder}/{shortname}.py"))
                LOGS.info(f"unable to load {shortname} because of error {e}")


async def verifyLoggerGroup():
    """
    Will verify the both loggers group
    """
    flag = False
    if BOTLOG:
        try:
            entity = await codex.get_entity(BOTLOG_CHATID)
            if not isinstance(entity, types.User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info(
                        "Permissions missing to send messages for the specified PRIVATE_GROUP_BOT_API_ID."
                    )
                if entity.default_banned_rights.invite_users:
                    LOGS.info(
                        "Permissions missing to addusers for the specified PRIVATE_GROUP_BOT_API_ID."
                    )
        except ValueError:
            LOGS.error(
                "PRIVATE_GROUP_BOT_API_ID cannot be found. Make sure it's correct."
            )
        except TypeError:
            LOGS.error(
                "PRIVATE_GROUP_BOT_API_ID is unsupported. Make sure it's correct."
            )
        except Exception as e:
            LOGS.error(
                "An Exception occured upon trying to verify the PRIVATE_GROUP_BOT_API_ID.\n"
                + str(e)
            )
    else:
        descript = "Don't delete this group or change to group(If you change group all your previous snips, welcome will be lost.)"
        _, groupid = await create_supergroup(
            "Codex (LOGS Group)", codex, Config.TG_BOT_USERNAME, descript
        )
        addgvar("PRIVATE_GROUP_BOT_API_ID", groupid)
        print(
            "Private Group for PRIVATE_GROUP_BOT_API_ID is created successfully and added to vars."
        )
        flag = True
    if PM_LOGGER_GROUP_ID != -100:
        try:
            entity = await codex.get_entity(PM_LOGGER_GROUP_ID)
            if not isinstance(entity, types.User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info(
                        "Permissions missing to send messages for the specified PM_LOGGER_GROUP_ID."
                    )
                if entity.default_banned_rights.invite_users:
                    LOGS.info(
                        "Permissions missing to addusers for the specified PM_LOGGER_GROUP_ID."
                    )
        except ValueError:
            LOGS.error("PM_LOGGER_GROUP_ID cannot be found. Make sure it's correct.")
        except TypeError:
            LOGS.error("PM_LOGGER_GROUP_ID is unsupported. Make sure it's correct.")
        except Exception as e:
            LOGS.error(
                "An Exception occured upon trying to verify the PM_LOGGER_GROUP_ID.\n"
                + str(e)
            )
    if flag:
        executable = sys.executable.replace(" ", "\\ ")
        args = [executable, "-m", "usercodex"]
        os.execle(executable, *args, os.environ)
        sys.exit(0)
