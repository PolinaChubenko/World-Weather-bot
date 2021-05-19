THUNDERSTORM = u'\U000026C8'
TORNADO = u'\U0001F32A'
FOG = u'\U0001F32B'
DRIZZLE = u'\U0001F327'
RAIN = u'\U00002614'
SNOW = u'\U0001F328'
SNOWMAN = u'\U000026C4'
ATMOSPHERE = u'\U0001F301'
CLEAR_SKY = u'\U00002600'
FEW_CLOUDS = u'\U0001F324'
A_FEW_CLOUDS = u'\U000026C5'
MANY_CLOUDS = u'\U0001F325'
CLOUDS = u'\U00002601'
HOT = u'\U0001F525'
DEF_EMOJI = u'\U0001F300'

THINKING = u'\U0001F914'
SUCCESS = u'\U0001F60E'
WINK = u'\U0001F609'
UPSIDE_DOWN = u'\U0001F643'
PENSIVE = u'\U0001F614'
MONKEY = u'\U0001F648'
POINT_DOWN = u'\U0001F447'
MONOCLE = u'\U0001F9D0'

PLANET1 = u'\U0001F30D'
PLANET2 = u'\U0001F30E'
PLANET3 = u'\U0001F30F'

thunderstormID = [200, 201, 202, 210, 211, 212, 221, 230, 231, 232]
drizzleID = [300, 301, 302, 310, 311, 312, 313, 314, 321]
rainID = [500, 501, 502, 503, 504, 511, 520, 521, 522, 531]
snowID = [600, 601, 602, 611, 612, 613, 615, 616, 620, 621, 622]
atmosphereID = [701, 711, 721, 731, 741, 751, 761, 762, 771]
tornadoID = [781]
clearID = [800]
few_cloudsID = [801]
a_few_cloudsID = [802]
many_cloudsID = [803]
cloudsID = [804]

emojis_codes = [
    (thunderstormID, THUNDERSTORM),
    (drizzleID, DRIZZLE),
    (rainID, RAIN),
    (snowID, SNOW),
    (atmosphereID, ATMOSPHERE),
    (tornadoID, TORNADO),
    (clearID, CLEAR_SKY),
    (few_cloudsID, few_cloudsID),
    (a_few_cloudsID, A_FEW_CLOUDS),
    (many_cloudsID, MANY_CLOUDS),
    (cloudsID, CLOUDS)
]


def get_emoji(weather):
    for code, emoji in emojis_codes:
        if int(weather) in code:
            return emoji
    return None
