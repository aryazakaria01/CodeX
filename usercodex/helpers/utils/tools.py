import os
from typing import Optional

from moviepy.editor import VideoFileClip
from PIL import Image

from ...core.logger import logging
from ...core.managers import edit_or_reply
from ..tools import media_type
from .utils import runcmd

LOGS = logging.getLogger(__name__)


async def media_to_pic(event, reply, noedits=False):
    mediatype = media_type(reply)
    if mediatype not in [
        "Photo",
        "Round Video",
        "Gif",
        "Sticker",
        "Video",
        "Voice",
        "Audio",
        "Document",
    ]:
        return event, None
    if not noedits:
        codevent = await edit_or_reply(
            event, f"`Transfiguration Time! Converting to ....`"
        )
    else:
        codevent = event
    codmedia = None
    codfile = os.path.join("./temp/", "meme.png")
    if os.path.exists(codfile):
        os.remove(codfile)
    if mediatype == "Photo":
        codmedia = await reply.download_media(file="./temp")
        im = Image.open(codmedia)
        im.save(codfile)
    elif mediatype in ["Audio", "Voice"]:
        await event.client.download_media(reply, codfile, thumb=-1)
    elif mediatype == "Sticker":
        codmedia = await reply.download_media(file="./temp")
        if codmedia.endswith(".tgs"):
            codcmd = f"lottie_convert.py --frame 0 -if lottie -of png '{codmedia}' '{codfile}'"
            stdout, stderr = (await runcmd(codcmd))[:2]
            if stderr:
                LOGS.info(stdout + stderr)
        elif codmedia.endswith(".webp"):
            im = Image.open(codmedia)
            im.save(codfile)
    elif mediatype in ["Round Video", "Video", "Gif"]:
        await event.client.download_media(reply, codfile, thumb=-1)
        if not os.path.exists(codfile):
            codmedia = await reply.download_media(file="./temp")
            clip = VideoFileClip(media)
            try:
                clip = clip.save_frame(codfile, 0.1)
            except:
                clip = clip.save_frame(codfile, 0)
    elif mediatype == "Document":
        mimetype = reply.document.mime_type
        mtype = mimetype.split("/")
        if mtype[0].lower() == "image":
            codmedia = await reply.download_media(file="./temp")
            im = Image.open(codmedia)
            im.save(codfile)
    if codmedia and os.path.lexists(codmedia):
        os.remove(codmedia)
    if os.path.lexists(codfile):
        return codevent, codfile, mediatype
    return codevent, None


async def take_screen_shot(
    video_file: str, duration: int, path: str = ""
) -> Optional[str]:
    thumb_image_path = path or os.path.join(
        "./temp/", f"{os.path.basename(video_file)}.jpg"
    )
    command = f"ffmpeg -ss {duration} -i '{video_file}' -vframes 1 '{thumb_image_path}'"
    err = (await runcmd(command))[1]
    if err:
        LOGS.error(err)
    return thumb_image_path if os.path.exists(thumb_image_path) else None
