import sys, os
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import urllib, urllib2
import json
import base64
from adobepass.adobe import ADOBE


addon_handle = int(sys.argv[1])
ADDON = xbmcaddon.Addon(id='plugin.video.simpsonsworld')
ROOTDIR = ADDON.getAddonInfo('path')
FANART = ROOTDIR+"/resources/media/fanart.jpg"
ICON = ROOTDIR+"/resources/media/icon.png"

#Addon Settings 
RATIO = str(ADDON.getSetting(id="ratio"))
COMMENTARY = str(ADDON.getSetting(id="commentary"))

RESOURCE_ID = "<rss version='2.0'><channel><title>fx</title></channel></rss>"
UA_FX = 'FXNOW/562 CFNetwork/711.4.6 Darwin/14.0.0'

#Add-on specific Adobepass variables
SERVICE_VARS = {'requestor_id':'fx',
                'public_key':'Dy1OhW3HrWk03QJrMMIULAmUdPQqk2Ds',
                'private_key':'B081JNlGKn1ZqpQH',
                'activate_url':'fxnetworks.com/activate'
                'reg_body': '&appVersion=Fire TV&deviceType=firetv'
               }

def listSeasons():   
    for x in range(1, 29):
        title = "Season "+str(x)
        url = str(x)
        #icon = 'http://thetvdb.com/banners/seasons/71663-'+str(x)+'-15.jpg'
        #icon = 'http://thetvdb.com/banners/seasonswide/71663-'+str(x)+'.jpg'        
        icon = 'http://thetvdb.com/banners/seasons/71663-'+str(x)+'.jpg'

        addSeason(title,url,101,icon,FANART)


def listEpisodes(season):    
    url = "http://fapi2.fxnetworks.com/androidtv/videos?filter%5Bfapi_show_id%5D=9aad7da1-093f-40f5-b371-fec4122f0d86&filter%5Bseason%5D="+season+"&limit=500&filter%5Btype%5D=episode"    
    req = urllib2.Request(url)
    req.add_header("Connection", "keep-alive")
    req.add_header("Accept", "*/*")
    req.add_header("Accept-Encoding", "deflate")
    req.add_header("Accept-Language", "en-us")
    req.add_header("Connection", "keep-alive")
    req.add_header("Authentication", "androidtv:a4y4o0e01jh27dsyrrgpvo6d1wvpravc2c4szpp4")
    req.add_header("User-Agent", UA_FX)
    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close() 
    
    for episode in reversed(json_source['videos']):            
        title = episode['name']
        #Default video type
        url = episode['video_urls']['16x9']['en_US']['video_url']         
        try: url = episode['video_urls'][RATIO]['en_US']['video_url']
        except: pass
        if COMMENTARY == 'true':
            try: url = episode['video_urls'][RATIO]['en_US']['video_url_commentary']
            except: pass
        icon = episode['img_url']
        desc = episode['description']
        duration = episode['duration']
        aired = episode['airDate']
        season = str(episode['season']).zfill(2) 
        episode = str(episode['episode']).zfill(2)         

        info = {'plot':desc,'tvshowtitle':'30000', 'season':season, 'episode':episode, 'title':title,'originaltitle':title,'duration':duration,'aired':aired,'genre':'30002'}
        
        addEpisode(title,url,title,icon,FANART,info)



def getStream(url):
    adobe = ADOBE(SERVICE_VARS)            
    mvpd = adobe.authorizeDevice(RESOURCE_ID)        
    media_token = adobe.mediaToken(RESOURCE_ID)          
    
    if media_token != '':
        url = url + "&auth="+urllib.quote(base64.b64decode(media_token))

        req = urllib2.Request(url)
        req.add_header("Accept", "*/*")
        req.add_header("Accept-Encoding", "deflate")
        req.add_header("Accept-Language", "en-us")
        req.add_header("Connection", "keep-alive")        
        req.add_header("User-Agent", UA_FX)
        response = urllib2.urlopen(req)              
        response.close() 

        '''
        print source
        start_str = '<video src="'
        end_str = '"'
        start = source.find(start_str)
        end = source.find(end_str,start+len(start_str))
        
        stream_url = source[start+len(start_str):end]
        '''
        #get the last url forwarded to
        stream_url = response.geturl()
        stream_url = stream_url + '|User-Agent=okhttp/3.4.1'
        
        listitem = xbmcgui.ListItem(path=stream_url)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem)    
    else:
        msg = "Error Signing Stream"
        dialog = xbmcgui.Dialog() 
        ok = dialog.ok('Authentication Failure', msg)



def addEpisode(name,link_url,title,iconimage,fanart,info=None):
    ok=True
    u=sys.argv[0]+"?url="+urllib.quote_plus(link_url)+"&mode="+str(102)
    liz=xbmcgui.ListItem(name)
    liz.setArt({'icon': ICON, 'thumb': iconimage, 'fanart': fanart})    
    liz.setProperty("IsPlayable", "true")
    liz.setInfo( type="Video", infoLabels={ "Title": title } )
    if info != None:
        liz.setInfo( type="Video", infoLabels=info) 
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    xbmcplugin.setContent(addon_handle, 'episodes')    
    return ok


def addSeason(name,url,mode,iconimage,fanart=None,info=None): 
    params = get_params()      
    ok=True    
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(name)
    liz.setArt({'icon': ICON, 'thumb': iconimage, 'fanart': fanart})
    liz.setInfo( type="Video", infoLabels={ "Title": name, 'tvdb_id': '71663' } )
    if info != None:
        liz.setInfo( type="Video", infoLabels=info)     
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)    
    xbmcplugin.setContent(addon_handle, 'tvshows')
    return ok


def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=splitparams[1]
                            
    return param