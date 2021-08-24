# corona virus stats for codexuserbot
# Credits @Catuserbot

from covid import Covid

from . import codex, covidindo, edit_delete, edit_or_reply

plugin_category = "extra"


@codex.cod_cmd(
    pattern="covid(?:\s|$)([\s\S]*)",
    command=("covid", plugin_category),
    info={
        "header": "To get latest information about covid-19.",
        "description": "Get information about covid-19 data in the given country.",
        "usage": "{tr}covid <state_name/country_name>",
        "examples": ["{tr}covid japan", "{tr}covid indonesia", "{tr}covid world"],
    },
)
async def corona(event):
    "To get latest information about covid-19."
    input_str = event.pattern_match.group(1)
    country = (input_str).title() if input_str else "World"
    codevent = await edit_or_reply(event, "`Collecting data...`")
    covid = Covid(source="worldometers")
    try:
        country_data = covid.get_status_by_country_name(country)
    except ValueError:
        country_data = ""
    if country_data:
        hmm1 = country_data["confirmed"] + country_data["new_cases"]
        hmm2 = country_data["deaths"] + country_data["new_deaths"]
        data = ""
        data += f"\n⚠️ <code>Confirmed   :</code> <code>{hmm1}</code>"
        data += f"\n😔 <code>Active      :</code> <code>{country_data['active']}</code>"
        data += f"\n⚰️ <code>Deaths      :</code> <code>{hmm2}</code>"
        data += (
            f"\n🤕 <code>Critical    :</code> <code>{country_data['critical']}</code>"
        )
        data += (
            f"\n😊 <code>Recovered   :</code> <code>{country_data['recovered']}</code>"
        )
        data += (
            f"\n💉 <code>Total tests :</code> <code>{country_data['total_tests']}</code>"
        )
        data += (
            f"\n🥺 <code>New Cases   :</code> <code>{country_data['new_cases']}</code>"
        )
        data += (
            f"\n😟 <code>New Deaths  :</code> <code>{country_data['new_deaths']}</code>"
        )
        await codevent.edit(
            "<b>Corona Virus Info of {}:\n{}</b>".format(country, data),
            parse_mode="html",
        )
    else:
        data = await covidindo(country)
        if data:
            axe1 = int(data["positif"])
            axe2 = int(data["sembuh"])
            axe3 = int(data["meninggal"])
            axe4 = int(data["dirawat"])
            result = f"<b>Corona virus info of {data['state_name']}\
                \n\n⚠️ `Positif    :` <code>{axe1}</code>\
                \n⚰️ `Meninggal  :` <code>{axe3}</code>\
                \n🏥 `Dirawat    :` <code>{axe4}</code>\
                \n🤞 `Sembuh     :` <code>{axe2}</code> </b>"
            await codevent.edit(result, parse_mode="html")
        else:
            await edit_delete(
                codevent,
                "`Corona Virus Info of {} is not avaiable or unable to fetch`".format(
                    country
                ),
                5,
            )
