import asyncio
import os
import random
from urllib.parse import quote_plus

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from ..Config import Config
from . import codex, deEmojify, edit_or_reply

plugin_category = "utils"

CARBONLANG = "auto"


@codex.cod_cmd(
    pattern="carbon(?:\s|$)([\s\S]*)",
    command=("carbon", plugin_category),
    info={
        "header": "Carbon generators for given text (Fixed style)",
        "usage": [
            "{tr}carbon <text>",
            "{tr}carbon <reply to text>",
        ],
    },
)
async def carbon_api(event):
    """A Wrapper for carbon.now.sh"""
    await event.edit("`Processing..`")
    CARBON = "https://carbon.now.sh/?l={lang}&code={code}"
    textx = await event.get_reply_message()
    pcode = event.text
    if pcode[8:]:
        pcode = str(pcode[8:])
    elif textx:
        pcode = str(textx.message)
    pcode = deEmojify(pcode)
    code = quote_plus(pcode)
    cod = await edit_or_reply(event, "`Carbonizing...\n25%`")
    url = CARBON.format(code=code, lang=CARBONLANG)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = Config.CHROME_BIN
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    prefs = {"download.default_directory": "./"}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(
        executable_path=Config.CHROME_DRIVER, options=chrome_options
    )
    driver.get(url)
    await cod.edit("`Be Patient...\n50%`")
    download_path = "./"
    driver.command_executor._commands["send_command"] = (
        "POST",
        "/session/$sessionId/chromium/send_command",
    )
    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {"behavior": "allow", "downloadPath": download_path},
    }
    driver.execute("send_command", params)
    driver.find_element_by_xpath("//button[contains(text(),'Export')]").click()

    await cod.edit("`Processing..\n75%`")

    await asyncio.sleep(2)
    await cod.edit("`Done Dana Done...\n100%`")
    file = "./carbon.png"
    await cod.edit("`Uploading..`")
    await event.client.send_file(
        event.chat_id,
        file,
        caption="Here's your carbon",
        force_document=True,
        reply_to=event.message.reply_to_msg_id,
    )
    os.remove("./carbon.png")
    driver.quit()

    await cod.delete()


@codex.cod_cmd(
    pattern="krb(?:\s|$)([\s\S]*)",
    command=("krb", plugin_category),
    info={
        "header": "Carbon generators for given text. each time gives  random style. You can also use patcicular style by using semicolon after text and name",
        "usage": [
            "{tr}krb <text>",
            "{tr}krb <reply to text>",
            "{tr}krb <text> ; <style name>",
        ],
    },
)
async def carbon_api(event):
    """A Wrapper for carbon.now.sh"""
    cod = await edit_or_reply(event, "`Processing....`")
    CARBON = "https://carbon.now.sh/?l={lang}&code={code}"
    textx = await event.get_reply_message()
    pcode = event.text
    if pcode[5:]:
        pcodee = str(pcode[5:])
        if ";" in pcodee:
            pcode, skeme = pcodee.split(";")
        else:
            pcode = pcodee
            skeme = None
    elif textx:
        pcode = str(textx.message)
        skeme = None
    pcode = pcode.strip()
    skeme = skeme.strip()
    pcode = deEmojify(pcode)
    code = quote_plus(pcode)
    await cod.edit("`Meking Carbon...`\n`25%`")
    url = CARBON.format(code=code, lang=CARBONLANG)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = Config.CHROME_BIN
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    prefs = {"download.default_directory": "./"}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(
        executable_path=Config.CHROME_DRIVER, options=chrome_options
    )
    driver.get(url)
    await cod.edit("`Be Patient...\n50%`")
    download_path = "./"
    driver.command_executor._commands["send_command"] = (
        "POST",
        "/session/$sessionId/chromium/send_command",
    )
    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {"behavior": "allow", "downloadPath": download_path},
    }
    driver.execute("send_command", params)
    driver.find_element_by_xpath(
        "/html/body/div[1]/main/div[3]/div[2]/div[1]/div[1]/div/span[2]"
    ).click()
    if skeme is not None:
        k_skeme = driver.find_element_by_xpath(
            "/html/body/div[1]/main/div[3]/div[2]/div[1]/div[1]/div/span[2]/input"
        )
        k_skeme.send_keys(skeme)
        k_skeme.send_keys(Keys.DOWN)
        k_skeme.send_keys(Keys.ENTER)
    else:
        color_scheme = str(random.randint(1, 29))
        driver.find_element_by_id(("downshift-0-item-" + color_scheme)).click()
    driver.find_element_by_id("export-menu").click()
    driver.find_element_by_xpath("//button[contains(text(),'4x')]").click()
    driver.find_element_by_xpath("//button[contains(text(),'PNG')]").click()
    await cod.edit("`Processing..\n75%`")

    await asyncio.sleep(2.5)
    color_name = driver.find_element_by_xpath(
        "/html/body/div[1]/main/div[3]/div[2]/div[1]/div[1]/div/span[2]/input"
    ).get_attribute("value")
    await cod.edit("`Done Dana Done...\n100%`")
    file = "./carbon.png"
    await cod.edit("`Uploading..`")
    await event.client.send_file(
        event.chat_id,
        file,
        caption=f"`Here's your carbon!` \n**Colour Scheme: **`{color_name}`",
        force_document=True,
        reply_to=event.message.reply_to_msg_id,
    )
    os.remove("./carbon.png")
    driver.quit()
    await cod.delete()
