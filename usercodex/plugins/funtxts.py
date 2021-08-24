import nekos

from usercodex import codex

from ..core.managers import edit_or_reply

plugin_category = "fun"


@codex.cod_cmd(
    pattern="tcod$",
    command=("tcod", plugin_category),
    info={
        "header": "Some random cod facial text art",
        "usage": "{tr}tcod",
    },
)
async def hmm(cod):
    "Some random cod facial text art"
    reactcat = nekos.textcod()
    await edit_or_reply(cod, reactcat)


@codex.cod_cmd(
    pattern="why$",
    command=("why", plugin_category),
    info={
        "header": "Sends you some random Funny questions",
        "usage": "{tr}why",
    },
)
async def hmm(cod):
    "Some random Funny questions"
    whycod = nekos.why()
    await edit_or_reply(cod, whycod)


@codex.cod_cmd(
    pattern="fact$",
    command=("fact", plugin_category),
    info={
        "header": "Sends you some random facts",
        "usage": "{tr}fact",
    },
)
async def hmm(cod):
    "Some random facts"
    factcod = nekos.fact()
    await edit_or_reply(cod, factcod)
