thunderstorm = u'\U000026C8'
tornado = u'\U0001F32A'
fog = u'\U0001F32B'
drizzle = u'\U0001F327'
rain = u'\U00002614'
snow = u'\U0001F328'
snowman = u'\U000026C4'
atmosphere = u'\U0001F301'
clearSky = u'\U00002600'
fewClouds = u'\U0001F324'
aFewClouds = u'\U000026C5'
manyClouds = u'\U0001F325'
clouds = u'\U00002601'
hot = u'\U0001F525'
def_emoji = u'\U0001F300'

thinking = u'\U0001F914'
success = u'\U0001F60E'
wink = u'\U0001F609'
upside_down = u'\U0001F643'
pensive = u'\U0001F614'
monkey = u'\U0001F648'
point_down = u'\U0001F447'

planet1 = u'\U0001F30D'
planet2 = u'\U0001F30E'
planet3 = u'\U0001F30F'

thunderstormID = [200, 201, 202, 210, 211, 212, 221, 230, 231, 232]
drizzleID = [300, 301, 302, 310, 311, 312, 313, 314, 321]
rainID = [500, 501, 502, 503, 504, 511, 520, 521, 522, 531]
snowID = [600, 601, 602, 611, 612, 613, 615, 616, 620, 621, 622]
atmosphereID = [701, 711, 721, 731, 741, 751, 761, 762, 771]
tornadoID = [781]
clearID = [800]
cloudsID = [801, 802, 803, 804]


def get_emoji(weather):
    weather = int(weather)
    if weather in thunderstormID:
        return thunderstorm
    if weather in drizzleID:
        return drizzle
    if weather in rainID:
        return rain
    if weather in snowID:
        return snow
    if weather in atmosphereID:
        return atmosphere
    if weather in tornadoID:
        return tornadoID
    if weather in clearID:
        return clearSky
    if weather == 801:
        return fewClouds
    if weather == 802:
        return aFewClouds
    if weather == 803:
        return manyClouds
    if weather == 804:
        return clouds
    return None
