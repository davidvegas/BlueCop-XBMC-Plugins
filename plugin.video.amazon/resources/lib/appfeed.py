#!/usr/bin/env python
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import xbmcplugin
import xbmc
import xbmcgui
import os.path
import sys
import urllib
import resources.lib.common as common
import re
import demjson
import listtv
import listmovie

import movies as moviesDB
import tv as tvDB

pluginhandle = common.pluginhandle
confluence_views = [500,501,502,503,504,508]

#Modes
#===============================================================================
# 'catalog/GetCategoryList'
# 'catalog/Browse'
# 'catalog/Search'
# 'catalog/GetSearchSuggestions'
# 'catalog/GetASINDetails'
# 'catalog/GetSimilarities'
# 
# 'catalog/GetStreamingUrls'
# 'catalog/GetStreamingTrailerUrls'
# 'catalog/GetContentUrls'
# 
# 'library/GetLibrary'
# 'library/Purchase'
# 'library/GetRecentPurchases'
# 
# 'link/LinkDevice'
# 'link/UnlinkDevice'
# 'link/RegisterClient'
# 'licensing/Release'
# 
# 'usage/UpdateStream'
# 'usage/ReportLogEvent'
# 'usage/ReportEvent'
# 'usage/GetServerConfig'
#===============================================================================


MAX_VALUES = [25,50,100,150,200,250]
MAX=MAX_VALUES[int(common.addon.getSetting("perpage"))]

common.gen_id()

deviceID = common.addon.getSetting("GenDeviceID")#'000000000000'
deviceTypeID = 'A2W5AJPLW5Q6YM'  #Android Type
#deviceTypeID = 'A13Q6A55DBZB7M' #WEB Type
firmware = 'fmw:15-app:1.1.19'
format = 'json'
PARAMETERS = '?firmware='+firmware+'&deviceTypeID='+deviceTypeID+'&deviceID='+deviceID+'&format='+format

def BUILD_BASE_API(MODE,HOST='https://atv-ext.amazon.com/cdp/'):
    return HOST+MODE+PARAMETERS

def getList(ContentType,start=0,isPrime=True):
    if isPrime:
        BROWSE_PARAMS = '&OfferGroups=B0043YVHMY'
    BROWSE_PARAMS +='&NumberOfResults=250'
    BROWSE_PARAMS +='&StartIndex='+str(start)
    BROWSE_PARAMS +='&ContentType='+ContentType
    BROWSE_PARAMS +='&OrderBy=SalesRank'
    #BROWSE_PARAMS +='&HighDef=F&playbackInformationRequired=false&OrderBy=SalesRank&SuppressBlackedoutEST=T&HideNum=T&Detailed=T&AID=1&IncludeNonWeb=T'
    BROWSE_PARAMS +='&version=2'    
    url = BUILD_BASE_API('catalog/Browse')+BROWSE_PARAMS
    return demjson.decode(common.getATVURL(url))

def ASIN_LOOKUP(ASINLIST):
    results = len(ASINLIST.split(','))-1
    BROWSE_PARAMS = '&asinList='+ASINLIST+'&NumberOfResults='+str(results)+'&IncludeAll=T&NumberOfResults=400&playbackInformationRequired=true&version=2'
    url = BUILD_BASE_API('catalog/GetASINDetails')+BROWSE_PARAMS
    return demjson.decode(common.getATVURL(url))

def URL_LOOKUP(url):
    return demjson.decode(common.getATVURL(url+PARAMETERS.replace('?','&')))

################################ Library listing
def APP_ROOT():
    common.addDir('Prime Movie Categories','appfeed','APP_LEVEL2','2,2')
    common.addDir('Prime TV shows Categories','appfeed','APP_LEVEL2','3,2')
    common.addDir('All Seasons','appfeed','BROWSE_SEASONS','')
    common.addDir('All Shows','appfeed','BROWSE_SERIES','')
    common.addDir('Full Category List','appfeed','APP_LEVEL0','')
    xbmcplugin.endOfDirectory(pluginhandle)
    
def APP_LEVEL0():
    url = BUILD_BASE_API('catalog/GetCategoryList')+'&version=1'
    data = common.getATVURL(url)
    json = demjson.decode(data)
    del data
    categories = json['message']['body']['categories']
    del json
    for item in categories:
        if item.has_key('categories'):
            common.addDir(item['title'],'appfeed','APP_LEVEL1',str(categories.index(item)))
        else:
            common.addDir(item['title'],'appfeed','BROWSE',item['query'])
    xbmcplugin.endOfDirectory(pluginhandle)
    
def APP_LEVEL1():
    url = BUILD_BASE_API('catalog/GetCategoryList')+'&version=1'
    data = common.getATVURL(url)
    json = demjson.decode(data)
    del data
    categories = json['message']['body']['categories'][int(common.args.url)]['categories']
    del json
    for item in categories:
        if item.has_key('categories'):
            common.addDir(item['title'],'appfeed','APP_LEVEL2',common.args.url+','+str(categories.index(item)))
        else:
            common.addDir(item['title'],'appfeed','BROWSE',item['query'])
    xbmcplugin.endOfDirectory(pluginhandle)    

def APP_LEVEL2():
    url = BUILD_BASE_API('catalog/GetCategoryList')+'&version=1'
    data = common.getATVURL(url)
    json = demjson.decode(data)
    del data
    categories = json['message']['body']['categories'][int(common.args.url.split(',')[0])]['categories'][int(common.args.url.split(',')[1])]['categories']
    del json
    for item in categories:
        if item.has_key('categories'):
            common.addDir(item['title'],'appfeed','APP_LEVEL3',common.args.url+','+str(categories.index(item)))
        else:
            common.addDir(item['title'],'appfeed','BROWSE',item['query'])
    xbmcplugin.endOfDirectory(pluginhandle)    

def APP_LEVEL3():
    url = BUILD_BASE_API('catalog/GetCategoryList')+'&version=1'
    data = common.getATVURL(url)
    json = demjson.decode(data)
    del data
    categories = json['message']['body']['categories'][int(common.args.url.split(',')[0])]['categories'][int(common.args.url.split(',')[1])]['categories'][int(common.args.url.split(',')[2])]['categories']
    del json
    for item in categories:
        if item.has_key('categories'):
            common.addDir(item['title'],'appfeed','APP_LEVEL4',common.args.url+','+str(categories.index(item)))
        else:
            common.addDir(item['title'],'appfeed','BROWSE',item['query'])
    xbmcplugin.endOfDirectory(pluginhandle) 

def APP_LEVEL4():
    common.addDir('ADD LEVEL4','appfeed','APP_LEVEL4','')
    
def ADD_MOVIE(addASIN,isPrime=True,inWatchlist=False):
    movies = moviesDB.lookupMoviedb(addASIN,isPrime=True)
    for moviedata in movies:
        listmovie.ADD_MOVIE_ITEM(moviedata,inWatchlist=inWatchlist)

def ADD_SERIES(addASIN,isPrime=True):
    shows = tvDB.lookupShowsdb(addASIN,isPrime)
    for showdata in shows:
        listtv.ADD_SHOW_ITEM(showdata)

def ADD_SEASON(addASIN,mode='appfeed',submode='BROWSE_EPISODES',isPrime=True,seriesTitle=True,inWatchlist=False):
    seasons = tvDB.lookupSeasondb(addASIN,isPrime)
    for seasondata in seasons:
        listtv.ADD_SEASON_ITEM(seasondata,mode=mode,submode=submode,seriesTitle=True,inWatchlist=inWatchlist)

def ADD_EPISODE(addASIN,isPrime=True,seriesTitle=False):
    episodes = tvDB.lookupEpisodedb(addASIN,isPrime)
    for episodedata in episodes:
        listtv.ADD_EPISODE_ITEM(episodedata,seriesTitle=seriesTitle)

def BROWSE_NEXT(results=MAX):
    index = int(common.args.page)*results
    BROWSE(results=results,index=index)

def BROWSE(results=MAX,index=0):
    BROWSE_PARAMS = '&OfferGroups=&HighDef=T&NumberOfResults='+str(results)+'&StartIndex='+str(index)+'&playbackInformationRequired=true&SuppressBlackedoutEST=T&version=2&'
    url = BUILD_BASE_API('catalog/Browse')+BROWSE_PARAMS+common.args.url
    BROWSE_ADDITEMS(url,results,index)

# No way to filter only prime shows. OfferGroup B0043YVHMY doesn't work
def BROWSE_SERIES(results=MAX,index=0):
    BROWSE_PARAMS = '&OfferGroups=&NumberOfResults='+str(results)+'&StartIndex='+str(index)+'&playbackInformationRequired=true&SuppressBlackedoutEST=T&version=2'
    url = BUILD_BASE_API('catalog/Browse')+BROWSE_PARAMS+'&ContentType=TVSeries&Detailed=T&tag=1&Detailed=T&AID=0&IncludeNonWeb=T&IncludeAll=T'
    BROWSE_ADDITEMS(url,results,index)

def BROWSE_SEASONS(results=MAX,index=0):
    BROWSE_PARAMS = '&OfferGroups=&NumberOfResults='+str(results)+'&StartIndex='+str(index)+'&HighDef=T&playbackInformationRequired=true&SuppressBlackedoutEST=T&version=2'
    url = BUILD_BASE_API('catalog/Browse')+BROWSE_PARAMS+'&ContentType=TVSeaon&HideNum=T&Detailed=T&AID=1&IncludeNonWeb=T&OfferGroups=B0043YVHMY&IncludeAll=T'
    BROWSE_ADDITEMS(url,results,index)

def BROWSE_SEASONS4SERIES(results=MAX,index=0):
    BROWSE_PARAMS = '&SeriesASIN='+common.args.url+'&ContentType=TVSeason&version=2&HideNum=F&Detailed=T&AID=1&IncludeNonWeb=T&IncludeAll=T'
    url = BUILD_BASE_API('catalog/Browse')+BROWSE_PARAMS
    BROWSE_ADDITEMS(url,results,index)

def BROWSE_EPISODES(results=MAX,index=0):
    BROWSE_PARAMS = '&SeasonASIN='+common.args.url+'&IncludeAll=T&NumberOfResults=400&playbackInformationRequired=true&version=2'
    url = BUILD_BASE_API('catalog/Browse')+BROWSE_PARAMS
    BROWSE_ADDITEMS(url,results,index)

def SEARCH_PRIME(searchString=False,results=MAX,index=0):
    if not searchString:
        keyboard = xbmc.Keyboard('')
        keyboard.doModal()
        q = keyboard.getText()
        if (keyboard.isConfirmed()):
            searchString=urllib.quote_plus(keyboard.getText())
            common.addDir('[Search Suggestions]','appfeed','SEARCH_SUGGEST_PRIME',searchString)
    BROWSE_PARAMS = '&searchString='+searchString+'&OfferGroups=B0043YVHMY&SuppressBlackedoutEST=T&version=2&NumberOfResults='+str(results)+'&StartIndex='+str(index)
    url = BUILD_BASE_API('catalog/Search')+BROWSE_PARAMS
    BROWSE_ADDITEMS(url,results,index,search=True)

def SEARCH_SUGGEST_PRIME():
    BROWSE_PARAMS = '&query='+common.args.url+'&version=1'
    url = BUILD_BASE_API('catalog/GetSearchSuggestions')+BROWSE_PARAMS
    data = common.getATVURL(url)
    suggestions = demjson.decode(data)['message']['body']['searchSuggestion']
    selected=xbmcgui.Dialog().select('Suggestions', [suggestion for suggestion in suggestions])
    SEARCH_PRIME(searchString=urllib.quote_plus(suggestions[selected]))
    
def BROWSE_ADDITEMS(url,results,index,search=False):
    data = common.getATVURL(url)
    json = demjson.decode(data)
    del data
    titles = json['message']['body']['titles']
    del json
    if len(titles) == results:
        if index == 0:
            page = 1
        else:
            page = index/results
        if not search:
            common.addDir('Next Page (%s-%s)'% (page*results+1,(page+1)*results),'appfeed','BROWSE_NEXT',common.args.url,page=page)
    Movies = False
    Series = False
    Season = False
    Episode = False
    for title in titles:
        if title['contentType'] == 'MOVIE':
            ADD_MOVIE(title['titleId'])
            Movies = True
        elif title['contentType'] == 'SERIES':
            ADD_SERIES(title['titleId'])
            Series = True
        elif title['contentType'] == 'SEASON':
            asin = title['titleId']
            for format in title['formats']:
                if format['videoFormatType'] == 'HD':
                    for offer in format['offers']:
                        if offer['offerType'] == 'SEASON_PURCHASE':
                            asin = offer['asin']
            ADD_SEASON(asin,seriesTitle=True)
            Season = True
        elif title['contentType'] == 'EPISODE':
            asin = title['titleId']
            for format in title['formats']:
                if format['videoFormatType'] == 'HD':
                    for offer in format['offers']:
                        if offer['offerType'] == 'PURCHASE':
                            asin = offer['asin']
            ADD_EPISODE(asin,seriesTitle=search)
            Episode = True
    if Series:
        view='showview'
        xbmcplugin.setContent(pluginhandle, 'tvshows')
    elif Season:
        view = 'seasonview'
        xbmcplugin.setContent(pluginhandle, 'tvshows')
    elif Movies:
        view='movieview'
        xbmcplugin.setContent(pluginhandle, 'Movies')
    elif Episode:
        view='episodeview'
        xbmcplugin.setContent(pluginhandle, 'Episodes')
    else:
        view='showview'
        xbmcplugin.setContent(pluginhandle, 'tvshows')
    xbmcplugin.endOfDirectory(pluginhandle)
    viewenable=common.addon.getSetting("viewenable")
    if viewenable == 'true':
        view=int(common.addon.getSetting(view))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
       