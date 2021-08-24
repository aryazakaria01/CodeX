from __future__ import unicode_literals

import asyncio
import os
import traceback

import pytgcalls
from pyrogram import filters, idle
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.raw.functions.phone import CreateGroupCall
from pyrogram.raw.types import InputPeerChannel
from pyrogram.types import Message

# Initialize db
import db

db.init()

from db import db
from functions import (
    BITRATE,
    CHAT_ID,
    app,
    get_default_service,
    play_song,
    session,
    telegram,
)
from misc import HELP_TEXT, REPO_TEXT

running = False  # Tells if the queue is running or not
CLIENT_TYPE = pytgcalls.GroupCallFactory.MTPROTO_CLIENT_TYPE.PYROGRAM
PLAYOUT_FILE = "input.raw"
PLAY_LOCK = asyncio.Lock()
OUTGOING_AUDIO_BITRATE_KBIT = BITRATE


@app.on_message(filters.command("help") & ~filters.private & filters.chat(CHAT_ID))
async def help(_, message):
    await message.reply_text(HELP_TEXT, quote=False)


@app.on_message(filters.command("repo") & ~filters.private & filters.chat(CHAT_ID))
async def repo(_, message):
    await message.reply_text(REPO_TEXT, quote=False)


@app.on_message(filters.command("joinvc") & ~filters.private & filters.chat(CHAT_ID))
async def joinvc(_, message, manual=False):
    if "call" in db:
        asyncio.sleep(0.7)
        return await message.reply_text("__**I'ma already in the voice chat.**__")
    asyncio.sleep(0.5)
    await message.delete()
    os.popen(f"cp etc/sample_input.raw {PLAYOUT_FILE}")
    vc = pytgcalls.GroupCallFactory(
        app, CLIENT_TYPE, OUTGOING_AUDIO_BITRATE_KBIT
    ).get_file_group_call(PLAYOUT_FILE, "output.raw")
    db["call"] = vc
    try:
        await vc.start(CHAT_ID)
    except Exception:
        peer = await app.resolve_peer(CHAT_ID)
        startVC = CreateGroupCall(
            peer=InputPeerChannel(
                channel_id=peer.channel_id,
                access_hash=peer.access_hash,
            ),
            random_id=app.rnd_id() // 9000000000,
        )
        try:
            await app.send(startVC)
            await vc.start(CHAT_ID)
        except ChatAdminRequired:
            del db["call"]
            return await message.reply_text(
                "Make me admin with message delete and vc manage permission"
            )
    asyncio.sleep(1)
    await message.reply_text(
        "✅ __**Joined The Voice Chat.**__ \n\n📃**Note:** __If you can't hear anything,"
        + " Send /leavevc and then /joinvc again.__"
    )
    asyncio.sleep(0.5)
    await message.delete()


@app.on_message(filters.command("leavevc") & ~filters.private & filters.chat(CHAT_ID))
async def leavevc(_, message):
    if "call" in db:
        await db["call"].leave_current_group_call()
        await db["call"].stop()
        del db["call"]
    asyncio.sleep(0.5)
    await message.reply_text("⏬ __**Left The Voice Chat**__")
    asyncio.sleep(0.5)
    await message.delete()


@app.on_message(filters.command("volume") & ~filters.private & filters.chat(CHAT_ID))
async def volume_bot(_, message):
    usage = "**Usage:**\n/volume [1-200]\n\n**Example:** `/volume 20`"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    if "call" not in db:
        return await message.reply_text("**Voice Call isn't started.**")
    vc = db["call"]
    volume = int(message.text.split(None, 1)[1])
    if (volume < 1) or (volume > 200):
        return await message.reply_text(usage)
    try:
        await vc.set_my_volume(volume=volume)
    except ValueError:
        return await message.reply_text(usage)
    asyncio.sleep(0.5)
    await message.reply_text(
        f"🔊 **Volume set to** `{volume}`\nPress👉 /repeat if you've changed the volume."
    )
    asyncio.sleep(0.5)
    await message.delete()


@app.on_message(filters.command("pause") & ~filters.private & filters.chat(CHAT_ID))
async def pause_song_func(_, message):
    if "call" not in db:
        return await message.reply_text("**Voice Call isn't started.**")
    if "paused" in db:
        if db.get("paused"):
            return await message.reply_text("**Already paused...**")
    db["paused"] = True
    db["call"].pause_playout()
    await message.reply_text("⏸️ **Paused The Music, Send `/resume` To Resume.**")


@app.on_message(filters.command("resume") & ~filters.private & filters.chat(CHAT_ID))
async def resume_song(_, message):
    if "call" not in db:
        return await message.reply_text("**Voice Call isn't started**")
    if "paused" in db:
        if not db.get("paused"):
            return await message.reply_text("**Already playing...**")
    db["paused"] = False
    db["call"].resume_playout()
    await message.reply_text("▶️ **Resumed, Send `/pause` To Pause The Music.**")


@app.on_message(filters.command("skip") & ~filters.private & filters.chat(CHAT_ID))
async def skip_func(_, message):
    if "queue" not in db:
        await message.reply_text("**Voice Call isn't started**")
        return await message.delete()
    queue = db["queue"]
    if queue.empty() and ("playlist" not in db or not db["playlist"]):
        await message.reply_text("🗑️ __**Queue Is Empty Dude, Just Like Your Life.**__")
        asyncio.sleep(0.7)
        return await message.delete()
    db["skipped"] = True
    asyncio.sleep(1)
    await message.reply_text("⏩ __**Skipped !!**__")
    asyncio.sleep(0.7)
    await message.delete()


@app.on_message(filters.command("repeat") & ~filters.private & filters.chat(CHAT_ID))
async def repeeeat(_, message):
    if "call" not in db:
        await message.reply_text("**Voice Call isn't started**")
        return
    if "call" in db:
        await db["call"].reconnect()
        asyncio.sleep(1)
        await message.reply_text("🔁 __**Repeat The Music...**__")
    asyncio.sleep(0.7)
    await message.delete()


@app.on_message(filters.command("play") & ~filters.private & filters.chat(CHAT_ID))
async def queuer(_, message):
    global running
    try:
        usage = """
**USAGE :**
`/play Skinnyfabs Ghost`
`/play youtube it's you`
`/play saavn how deep is your love`
`/play Reply On Audio File (Telegram)`"""

        async with PLAY_LOCK:
            if len(message.command) < 1 and not message.reply_to_message:
                return await message.reply_text(usage)
            await message.delete()
            if "call" not in db:
                return await message.reply_text("**Fkg Stupid, Use /joinvc First!**")
            await message.delete()
            if message.reply_to_message:
                if message.reply_to_message.audio:
                    service = "telegram"
                    song_name = message.reply_to_message.audio.title
                else:
                    return await message.reply_text(
                        "**LOL, Reply to a telegram audio file**"
                    )
                await message.delete()
            else:
                text = message.text.split("\n")[0]
                text = text.split(None, 1)[1:]
                service = text[0].lower()
                services = ["youtube", "saavn"]
                if service in services:
                    song_name = text[1]
                else:
                    service = get_default_service()
                    song_name = " ".join(text)
            requested_by = message.from_user.first_name
            if "queue" not in db:
                db["queue"] = asyncio.Queue()
            if not db["queue"].empty() or db.get("running"):
                asyncio.sleep(1)
                await message.reply_text(
                    f"⏭️ __**Added To Queue.__**\n\n**Song Name:** `{song_name}`\n**Requested By:** {message.from_user.first_name}\n**Platform:** `{service}`"
                )
                asyncio.sleep(0.7)
                await message.delete()
            asyncio.sleep(1)
            await db["queue"].put(
                {
                    "service": service or telegram,
                    "requested_by": requested_by,
                    "query": song_name,
                    "message": message,
                }
            )
        if not db.get("running"):
            db["running"] = True
            await start_queue()
    except Exception as e:
        await message.reply_text(str(e))
        e = traceback.format_exc()
        print(e)


@app.on_message(filters.command("queue") & ~filters.private & filters.chat(CHAT_ID))
async def queue_list(_, message):
    if "queue" not in db:
        db["queue"] = asyncio.Queue()
    queue = db["queue"]
    if queue.empty():
        return await message.reply_text(
            "🗑️__**Queue Is Empty, Just Like Your Life.**__"
        )
    if len(message.text.split()) > 1 and message.text.split()[1].lower() == "plformat":
        pl_format = True
    else:
        pl_format = False
    text = ""
    for count, song in enumerate(queue._queue, 1):
        if not pl_format:
            text += (
                f"**No {count}. {song['service']}** "
                + f"| __{song['query']}__  |  {song['requested_by']}\n"
            )
        else:
            text += song["query"] + "\n"
    if len(text) > 4090:
        return await message.reply_text(
            f"**There are {queue.qsize()} songs in queue.**"
        )
    await message.reply_text(text)


# Queue handler


async def start_queue(message=None):
    while db:
        if "queue_breaker" in db and db.get("queue_breaker") != 0:
            db["queue_breaker"] -= 1
            if db["queue_breaker"] == 0:
                del db["queue_breaker"]
            break
        if db["queue"].empty():
            if "playlist" not in db or not db["playlist"]:
                db["running"] = False
                break
            else:
                await playlist(app, message, redirected=True)
        data = await db["queue"].get()
        service = data["service"]
        if service == "telegram":
            await telegram(data["message"])
        else:
            await play_song(
                data["requested_by"],
                data["query"],
                data["message"],
                service,
            )


@app.on_message(filters.command("delqueue") & ~filters.private & filters.chat(CHAT_ID))
async def clear_queue(_, message):
    global db
    if "call" not in db:
        return await message.reply_text("**Voice Call isn't started**")
    if ("queue" not in db or db["queue"].empty()) and (
        "playlist" not in db or not db["playlist"]
    ):
        return await message.reply_text("**Queue Already is Empty** 🗑️")
    db["playlist"] = False
    db["queue"] = asyncio.Queue()
    await message.reply_text("**Successfully Cleared the Queue** 🗑️")


@app.on_message(filters.command("playlist") & ~filters.private & filters.chat(CHAT_ID))
async def playlist(_, message: Message, redirected=False):
    if message.reply_to_message:
        raw_playlist = message.reply_to_message.text
    elif len(message.text) > 9:
        raw_playlist = message.text[10:]
    else:
        usage = """
**Usage: Same as /play
Example:
    __**/playlist song name 1
    song name 2
    youtube song name 3**__"""

        return await message.reply_text(usage)
    if "call" not in db:
        return await message.reply_text("**Fkg Stupid, Use /joinvc First!**")
    if "playlist" not in db:
        db["playlist"] = False
    if "running" in db and db.get("running"):
        db["queue_breaker"] = 1
    db["playlist"] = True
    db["queue"] = asyncio.Queue()
    for line in raw_playlist.split("\n"):
        services = ["youtube", "saavn"]
        if line.split()[0].lower() in services:
            service = line.split()[0].lower()
            song_name = " ".join(line.split()[1:])
        else:
            service = "youtube"
            song_name = line
        requested_by = message.from_user.first_name
        await db["queue"].put(
            {
                "service": service or telegram,
                "requested_by": requested_by,
                "query": song_name,
                "message": message,
            }
        )
    if not redirected:
        db["running"] = True
        await message.reply_text("**Playlist Started.**")
        await start_queue(message)


async def main():
    await app.start()
    print("Bot started!")
    await idle()
    await session.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
