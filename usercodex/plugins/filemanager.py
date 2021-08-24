import asyncio
import io
import os
import shutil
import time
from pathlib import Path

from usercodex import codex

from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _codutils, _format
from . import humanbytes

plugin_category = "utils"


@codex.cod_cmd(
    pattern="ls(?:\s|$)([\s\S]*)",
    command=("ls", plugin_category),
    info={
        "header": "To list all files and folders.",
        "description": "Will show all files and folders if no path is given or folder path is given else will show file details(if file path os given).",
        "usage": "{tr}ls <path>",
        "examples": "{tr}ls usercodex",
    },
)
async def lst(event):  # sourcery no-metrics
    "To list all files and folders."
    cod = "".join(event.text.split(maxsplit=1)[1:])
    path = cod or os.getcwd()
    if not os.path.exists(path):
        await edit_or_reply(
            event,
            f"there is no such directory or file with the name `{cod}` check again",
        )
        return
    path = Path(cod) if cod else os.getcwd()
    if os.path.isdir(path):
        if cod:
            msg = "Folders and Files in `{}` :\n".format(path)
        else:
            msg = "Folders and Files in Current Directory :\n"
        lists = os.listdir(path)
        files = ""
        folders = ""
        for contents in sorted(lists):
            codpath = os.path.join(path, contents)
            if not os.path.isdir(codpath):
                size = os.stat(codpath).st_size
                if str(contents).endswith((".mp3", ".flac", ".wav", ".m4a")):
                    files += "🎵" + f"`{contents}`\n"
                if str(contents).endswith((".opus")):
                    files += "🎙" + f"`{contents}`\n"
                elif str(contents).endswith(
                    (".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")
                ):
                    files += "🎞" + f"`{contents}`\n"
                elif str(contents).endswith((".zip", ".tar", ".tar.gz", ".rar")):
                    files += "🗜" + f"`{contents}`\n"
                elif str(contents).endswith(
                    (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico")
                ):
                    files += "🖼" + f"`{contents}`\n"
                else:
                    files += "📄" + f"`{contents}`\n"
            else:
                folders += f"📁`{contents}`\n"
        msg = msg + folders + files if files or folders else msg + "__empty path__"
    else:
        size = os.stat(path).st_size
        msg = f"The details of given file :\n"
        if str(path).endswith((".mp3", ".flac", ".wav", ".m4a")):
            mode = "🎵"
        if str(path).endswith((".opus")):
            mode = "🎙"
        elif str(path).endswith((".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")):
            mode = "🎞"
        elif str(path).endswith((".zip", ".tar", ".tar.gz", ".rar")):
            mode = "🗜"
        elif str(path).endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico")):
            mode = "🖼"
        else:
            mode = "📄"
        time.ctime(os.path.getctime(path))
        time2 = time.ctime(os.path.getmtime(path))
        time3 = time.ctime(os.path.getatime(path))
        msg += f"**Location :** `{str(path)}`\n"
        msg += f"**icon :** `{mode}`\n"
        msg += f"**Size :** `{humanbytes(size)}`\n"
        msg += f"**Last Modified Time:** `{time2}`\n"
        msg += f"**Last Accessed Time:** `{time3}`"
    if len(msg) > Config.MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "ls.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption=path,
            )
            await event.delete()
    else:
        await edit_or_reply(event, msg)


@codex.cod_cmd(
    pattern="rem ([\s\S]*)",
    command=("rem", plugin_category),
    info={
        "header": "To delete a file or folder from the server",
        "usage": "{tr}rem <path>",
        "examples": "{tr}rem Dockerfile",
    },
)
async def lst(event):
    "To delete a file or folder."
    cod = event.pattern_match.group(1)
    if cod:
        path = Path(cod)
    else:
        await edit_or_reply(event, "what should i delete")
        return
    if not os.path.exists(path):
        await edit_or_reply(
            event,
            f"there is no such directory or file with the name `{cod}` check again",
        )
        return
    codcmd = f"rm -rf {path}"
    if os.path.isdir(path):
        await _codutils.runcmd(codcmd)
        await edit_or_reply(event, f"Succesfully removed `{path}` directory")
    else:
        await _codutils.runcmd(codcmd)
        await edit_or_reply(event, f"Succesfully removed `{path}` file")


@codex.cod_cmd(
    pattern="mkdir(?:\s|$)([\s\S]*)",
    command=("mkdir", plugin_category),
    info={
        "header": "To create a new directory.",
        "usage": "{tr}mkdir <topic>",
        "examples": "{tr}mkdir cod",
    },
)
async def _(event):
    "To create a new directory."
    pwd = os.getcwd()
    input_str = event.pattern_match.group(1)
    if not input_str:
        return await edit_delete(
            event,
            "What should i create ?",
            parse_mode=_format.parse_pre,
        )
    original = os.path.join(pwd, input_str.strip())
    if os.path.exists(original):
        await edit_delete(
            event,
            f"Already a directory named {original} exists",
        )
        return
    mone = await edit_or_reply(
        event, "creating the directory ...", parse_mode=_format.parse_pre
    )
    await asyncio.sleep(2)
    try:
        await _codutils.runcmd(f"mkdir {original}")
        await mone.edit(f"Successfully created the directory `{original}`")
    except Exception as e:
        await edit_delete(mone, str(e), parse_mode=_format.parse_pre)


@codex.cod_cmd(
    pattern="cpto(?:\s|$)([\s\S]*)",
    command=("cpto", plugin_category),
    info={
        "header": "To copy a file from one directory to other directory",
        "usage": "{tr}cpto from ; to destination",
        "examples": "{tr}cpto sample_config.py ; downloads",
    },
)
async def _(event):
    "To copy a file from one directory to other directory"
    pwd = os.getcwd()
    input_str = event.pattern_match.group(1)
    if not input_str:
        return await edit_delete(
            event,
            "What and where should i move the file/folder.",
            parse_mode=_format.parse_pre,
        )
    loc = input_str.split(";")
    if len(loc) != 2:
        return await edit_delete(
            event,
            "use proper syntax .cpto from ; to destination",
            parse_mode=_format.parse_pre,
        )
    original = os.path.join(pwd, loc[0].strip())
    location = os.path.join(pwd, loc[1].strip())

    if not os.path.exists(original):
        await edit_delete(
            event,
            f"there is no such directory or file with the name `{cod}` check again",
        )
        return
    mone = await edit_or_reply(
        event, "copying the file ...", parse_mode=_format.parse_pre
    )
    await asyncio.sleep(2)
    try:
        await _codutils.runcmd(f"cp -r {original} {location}")
        await mone.edit(f"Successfully copied the `{original}` to `{location}`")
    except Exception as e:
        await edit_delete(mone, str(e), parse_mode=_format.parse_pre)


@codex.cod_cmd(
    pattern="mvto(?:\s|$)([\s\S]*)",
    command=("mvto", plugin_category),
    info={
        "header": "To move a file from one directory to other directory.",
        "usage": "{tr}mvto frompath ; topath",
        "examples": "{tr}mvto stringsession.py ; downloads",
    },
)
async def _(event):
    "To move a file from one directory to other directory"
    pwd = os.getcwd()
    input_str = event.pattern_match.group(1)
    if not input_str:
        return await edit_delete(
            event,
            "What and where should i move the file/folder.",
            parse_mode=_format.parse_pre,
        )
    loc = input_str.split(";")
    if len(loc) != 2:
        return await edit_delete(
            event,
            "use proper syntax .mvto from ; to destination",
            parse_mode=_format.parse_pre,
        )
    original = os.path.join(pwd, loc[0].strip())
    location = os.path.join(pwd, loc[1].strip())

    if not os.path.exists(original):
        return await edit_delete(
            event,
            f"there is no such directory or file with the name `{original}` check again",
        )
    mone = await edit_or_reply(
        event, "Moving the file ...", parse_mode=_format.parse_pre
    )
    await asyncio.sleep(2)
    try:
        shutil.move(original, location)
        await mone.edit(f"Successfully moved the `{original}` to `{location}`")
    except Exception as e:
        await edit_delete(mone, str(e), parse_mode=_format.parse_pre)
