
import aiohttp
import config

from urllib.parse import quote

from telegram import constants
from nandha.helpers.decorator import Command


__help__ = """
*Commands*:
/country, /countries, /regions

```
/country name: information about country by name
/countries: get all countries names.
/regions: get all regions names.
```

*Example*:
`/country india`
"""

__module__ = "Country"


COUNTRIES_TXT = f""" \n🌐 *Country Names*:

```Aruba
Afghanistan
Angola
Anguilla
Åland Islands
Albania
Andorra
United Arab Emirates
Argentina
Armenia
American Samoa
Antarctica
French Southern and Antarctic Lands
Antigua and Barbuda
Australia
Austria
Azerbaijan
Burundi
Belgium
Benin
Burkina Faso
Bangladesh
Bulgaria
Bahrain
Bahamas
Bosnia and Herzegovina
Saint Barthélemy
Saint Helena, Ascension and Tristan da Cunha
Belarus
Belize
Bermuda
Bolivia
Caribbean Netherlands
Brazil
Barbados
Brunei
Bhutan
Bouvet Island
Botswana
Central African Republic
Canada
Cocos (Keeling) Islands
Switzerland
Chile
China
Ivory Coast
Cameroon
DR Congo
Republic of the Congo
Cook Islands
Colombia
Comoros
Cape Verde
Costa Rica
Cuba
Curaçao
Christmas Island
Cayman Islands
Cyprus
Czechia
Germany
Djibouti
Dominica
Denmark
Dominican Republic
Algeria
Ecuador
Egypt
Eritrea
Western Sahara
Spain
Estonia
Ethiopia
Finland
Fiji
Falkland Islands
France
Faroe Islands
Micronesia
Gabon
United Kingdom
Georgia
Guernsey
Ghana
Gibraltar
Guinea
Guadeloupe
Gambia
Guinea-Bissau
Equatorial Guinea
Greece
Grenada
Greenland
Guatemala
French Guiana
Guam
Guyana
Hong Kong
Heard Island and McDonald Islands
Honduras
Croatia
Haiti
Hungary
Indonesia
Isle of Man
India
British Indian Ocean Territory
Ireland
Iran
Iraq
Iceland
Israel
Italy
Jamaica
Jersey
Jordan
Japan
Kazakhstan
Kenya
Kyrgyzstan
Cambodia
Kiribati
Saint Kitts and Nevis
South Korea
Kosovo
Kuwait
Laos
Lebanon
Liberia
Libya
Saint Lucia
Liechtenstein
Sri Lanka
Lesotho
Lithuania
Luxembourg
Latvia
Macau
Saint Martin
Morocco
Monaco
Moldova
Madagascar
Maldives
Mexico
Marshall Islands
North Macedonia
Mali
Malta
Myanmar
Montenegro
Mongolia
Northern Mariana Islands
Mozambique
Mauritania
Montserrat
Martinique
Mauritius
Malawi
Malaysia
Mayotte
Namibia
New Caledonia
Niger
Norfolk Island
Nigeria
Nicaragua
Niue
Netherlands
Norway
Nepal
Nauru
New Zealand
Oman
Pakistan
Panama
Pitcairn Islands
Peru
Philippines
Palau
Papua New Guinea
Poland
Puerto Rico
North Korea
Portugal
Paraguay
Palestine
French Polynesia
Qatar
Réunion
Romania
Russia
Rwanda
Saudi Arabia
Sudan
Senegal
Singapore
South Georgia
Svalbard and Jan Mayen
Solomon Islands
Sierra Leone
El Salvador
San Marino
Somalia
Saint Pierre and Miquelon
Serbia
South Sudan
São Tomé and Príncipe
Suriname
Slovakia
Slovenia
Sweden
Eswatini
Sint Maarten
Seychelles
Syria
Turks and Caicos Islands
Chad
Togo
Thailand
Tajikistan
Tokelau
Turkmenistan
Timor-Leste
Tonga
Trinidad and Tobago
Tunisia
Turkey
Tuvalu
Taiwan
Tanzania
Uganda
Ukraine
United States Minor Outlying Islands
Uruguay
United States
Uzbekistan
Vatican City
Saint Vincent and the Grenadines
Venezuela
British Virgin Islands
United States Virgin Islands
Vietnam
Vanuatu
Wallis and Futuna
Samoa
Yemen
South Africa
Zambia
Zimbabwe```

❤️ *By {config.BOT_USERNAME}*
"""


REGIONS_TXT = f"""\n
*🌎 Country Regions*:

```
Americas
Asia
Africa
Europe
Oceania
Antarctic
```
❤️ *By {config.BOT_USERNAME}*
"""


@Command('regions')
async def regions(update, context):
      m = update.effective_message
      await m.reply_text(REGIONS_TXT, parse_mode=constants.ParseMode.MARKDOWN)
  
@Command('countries')
async def countries(update, context):
      m = update.effective_message
      await m.reply_text(COUNTRIES_TXT, parse_mode=constants.ParseMode.MARKDOWN)
  
async def country_info(name: str):
    url = f"https://countryinfoapi.com/api/countries/name/{name}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Format currency string separately for better readability
                    currencies = [
                        f"{cur} ({details.get('name', 'N/A')}, {details.get('symbol', 'N/A')})"
                        for cur, details in data.get('currencies', {}).items()
                    ]
                    
                    country_info = (
                        f"📛 *Name*: {data.get('name', 'N/A')}\n"
                        f"🌐 *Top-level domain*: {', '.join(data.get('tld', ['N/A']))}\n"
                        f"🏙️ *Capital*: {', '.join(data.get('capital', ['N/A']))}\n"
                        f"®️ *Region*: {data.get('region', 'N/A')}\n"
                        f"®️ *Subregion*: {data.get('subregion', 'N/A')}\n"
                        f"👨‍👩‍👧‍👦 *Population*: {data.get('population', 'N/A'):,}\n"
                        f"🌍 *Area*: {data.get('area', 'N/A'):,} sq. km\n"
                        f"💰 *Currencies*: {', '.join(currencies)}\n"
                        f"🗣️ *Languages*: {', '.join(data.get('languages', {}).values())}\n\n"
                        f"✨ By {config.BOT_USERNAME}"
                    )
                    return country_info
                else:
                    return f"❌ Error: Country '{name}' not found (Status code: {response.status})"
    except aiohttp.ClientError as e:
        return f"❌ Error connecting to the API: {str(e)}"
    except Exception as e:
        return f"❌ An unexpected error occurred: {str(e)}"



@Command('country')
async def countryInfo(update, context):
     m = update.effective_message
     query = quote(m.text.split(maxsplit=1)[1].strip()) if len(m.text.split()) > 1 else False
     if not query:
          return await m.reply_text('❌ *Country name not given (!)*', parse_mode=constants.ParseMode.MARKDOWN)
     text = await country_info(query)
     await m.reply_text(
          text,
          parse_mode=constants.ParseMode.MARKDOWN
     )
     
