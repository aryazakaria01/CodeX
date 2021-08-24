import sys

import usercodex
from usercodex import BOTLOG_CHATID, HEROKU_APP, PM_LOGGER_GROUP_ID

from .Config import Config
from .core.logger import logging
from .core.session import codex
from .utils import (
    add_bot_to_logger_group,
    ipchange,
    load_plugins,
    setup_bot,
    startupmessage,
    verifyLoggerGroup,
)

LOGS = logging.getLogger("CodexUserbot")

print(usercodex.__copyright__)
print("Licensed under the terms of the " + usercodex.__license__)

cmdhr = Config.COMMAND_HAND_LER

try:
    LOGS.info("Starting Userbot")
    codex.loop.run_until_complete(setup_bot())
    LOGS.info("Telegram Bot Startup Completed")
except Exception as e:
    LOGS.error(f"{str(e)}")
    sys.exit()


class CodexCheck:
    def __init__(self):
        self.sucess = True


Codexcheck = CodexCheck()


async def startup_process():
    check = await ipchange()
    if check is not None:
        Codexcheck.sucess = False
        return
    await verifyLoggerGroup()
    await load_plugins("plugins")
    await load_plugins("assistant")
    print("========================================")
    print("Okay, Codex is Officially Working.!!!")
    print(
        f"Now type {cmdhr}alive to see message if codex is live\
        \nIf you need assistance."
    )
    print("========================================")
    print(usercodex.__copyright__)
    print("Licensed: " + usercodex.__license__)
    await verifyLoggerGroup()
    await add_bot_to_logger_group(BOTLOG_CHATID)
    if PM_LOGGER_GROUP_ID != -100:
        await add_bot_to_logger_group(PM_LOGGER_GROUP_ID)
    await startupmessage()
    Codexcheck.sucess = True
    return


codex.loop.run_until_complete(startup_process())

if len(sys.argv) not in (1, 3, 4):
    codex.disconnect()
elif not Codexcheck.sucess:
    if HEROKU_APP is not None:
        HEROKU_APP.restart()
else:
    try:
        codex.run_until_disconnected()
    except ConnectionError:
        pass
