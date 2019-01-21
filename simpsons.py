from resources.lib.globals import *

params = get_params()
url = None
name = None
mode = None

if 'url' in params:
    url = urllib.unquote_plus(params["url"])

if 'name' in params:
    name = urllib.unquote_plus(params["name"])

if 'mode' in params:
    mode = int(params["mode"])

if mode is None or url is None or len(url)<1:
    list_seasons()
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
elif mode == 101:
    list_episode(url)
elif mode == 102:
    get_stream(url)
elif mode == 103:
    random_episode()

    if CONTINUOUS_RANDOM == 'true':
        xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(sys.argv[0] + "?url=0&mode=103")

elif mode == 999:
    deauthorize()

xbmcplugin.endOfDirectory(addon_handle)