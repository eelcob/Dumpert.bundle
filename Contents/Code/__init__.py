import re

####################################################################################################

PLUGIN_TITLE = "Dumpert"
PLUGIN_VIDEO_PREFIX = "/video/dumpert"
PLUGIN_PHOTO_PREFIX = "/photos/dumpert"

# URLS
URL_ROOT_URI     = "http://www.dumpert.nl/"
URL_TOPPERS      = URL_ROOT_URI + "toppers/"
URL_FILMPJES     = URL_ROOT_URI + "filmpjes/"
URL_PLAATJES     = URL_ROOT_URI + "plaatjes/"
URL_AUDIO        = URL_ROOT_URI + "audio/"
URL_VIDEO_ZOEKEN = URL_ROOT_URI + "search/MV/"
URL_PHOTO_ZOEKEN = URL_ROOT_URI + "search/F/"

# REGULAR EXPRESSIONS
REGEX_PAGE_ITEM = r"""<a class="item" href="http://www.dumpert.nl/mediabase/([0-9]+)/([0-9a-f]+)/([^<]+).html">\s+<img src="([^<]+)" alt="[^<]+" title="[^<]+" width="100" height="100" />\s+<div class="info">\s+<h3>([^<]+)</h3>\s+<div class="date">[^<]+</div>\s+<p>([^<]+)</p>"""
REGEX_STREAM = r"""autoStart=true&amp;streamer=lighttpd&amp;file=([^<]+)&amp;recommendations"""
REGEX_AUDIO = r"""file=([^<]+)&config"""
REGEX_IMAGE = r"""<img src="([^<]+)" onclick="window.open"""
REGEX_IMAGE2 = r"""<img src="([^<]+)" class="picca" """
REGEX_OUDER = r"""<span>Ouder</span>"""
REGEX_COMMENTS = r"""comments.push\('<p>([^<]+)</p>'\);\s+comments.push\('<p class="footer">([^<]+) ([0-9]+)-([0-9]+)-([0-9]+) @"""

# Default artwork and icon(s)
PLUGIN_ARTWORK = "art-default.jpg"
PLUGIN_ICON_DEFAULT = "icon-default.png"
PLUGIN_ICON_TOPPERS = "icon-toppers.png"
PLUGIN_ICON_FILMPJES = "icon-filmpjes.png"
PLUGIN_ICON_PLAATJES = "icon-plaatjes.png"
PLUGIN_ICON_AUDIO = "icon-audio.png"
PLUGIN_ICON_ZOEKEN = "icon-zoeken.png"
PLUGIN_ICON_SETTINGS = "icon-settings.png"
PLUGIN_ICON_HELP = "icon-help.png"
PLUGIN_ICON_NEXT = "icon-next.png"

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_VIDEO_PREFIX, MainMenuVideo, PLUGIN_TITLE, PLUGIN_ICON_DEFAULT, PLUGIN_ARTWORK)
  Plugin.AddPrefixHandler(PLUGIN_PHOTO_PREFIX, MainMenuPhoto, PLUGIN_TITLE, PLUGIN_ICON_DEFAULT, PLUGIN_ARTWORK)

  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  Plugin.AddViewGroup("Photos", viewMode="Pictures", mediaType="photos")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")

  # Set the default MediaContainer attributes
  MediaContainer.title1 = PLUGIN_TITLE
  MediaContainer.viewGroup = 'List'
  MediaContainer.art = R(PLUGIN_ARTWORK)

  # Set the default cache time
  HTTP.CacheTime = CACHE_1HOUR

####################################################################################################

def MainMenuVideo():
  dir = MediaContainer(noCache=True) 
  dir.Append(Function(DirectoryItem(DumpertPage, title="Toppers", thumb=R(PLUGIN_ICON_TOPPERS)), pageUrl = URL_TOPPERS, pageIndex = 0, viewGroup='Details'))
  dir.Append(Function(DirectoryItem(DumpertPage, title="Filmpjes", thumb=R(PLUGIN_ICON_FILMPJES)), pageUrl = URL_FILMPJES, pageIndex = 0, viewGroup='Details'))
  dir.Append(Function(DirectoryItem(DumpertPage, title="Audio", thumb=R(PLUGIN_ICON_AUDIO)), pageUrl = URL_AUDIO, pageIndex = 0, viewGroup='Details'))
  dir.Append(Function(InputDirectoryItem(SearchPage, title="Zoeken", thumb=R(PLUGIN_ICON_ZOEKEN), prompt="Zoeken"), pageUrl = URL_VIDEO_ZOEKEN, pageIndex = 0, viewGroup='Details'))
  dir.Append(PrefsItem(title="Instellingen", thumb=R(PLUGIN_ICON_SETTINGS)))
  dir.Append(Function(DirectoryItem(AboutVideoPage, title="Help", thumb=R(PLUGIN_ICON_HELP))))

  return dir

####################################################################################################

def MainMenuPhoto():
  dir = MediaContainer(noCache=True) 
  dir.Append(Function(DirectoryItem(DumpertPage, title="Plaatjes", thumb=R(PLUGIN_ICON_PLAATJES)), pageUrl = URL_PLAATJES, pageIndex = 0, viewGroup='Photos'))
  dir.Append(Function(InputDirectoryItem(SearchPage, title="Zoeken", thumb=R(PLUGIN_ICON_ZOEKEN), prompt="Zoeken"), pageUrl = URL_PHOTO_ZOEKEN, pageIndex = 0, viewGroup='Photos'))
  dir.Append(PrefsItem(title="Instellingen", thumb=R(PLUGIN_ICON_SETTINGS)))
  dir.Append(Function(DirectoryItem(AboutPhotoPage, title="Help", thumb=R(PLUGIN_ICON_HELP))))

  return dir

####################################################################################################

def AboutVideoPage(sender):
  return MessageContainer("Help", "Als je in de sectie 'Toppers' de melding 'Could not read from input\nstream' krijgt, dan komt dit doordat de video-plugin een afbeelding\nprobeert te open. Gebruik hiervoor de afbeeldingen-plugin.")

####################################################################################################

def AboutPhotoPage(sender):
  return MessageContainer("Help", "Als het commentaar uit staat, dan kan je alleen de eerste foto van elk\nitem bekijken. Je kan dan echter wel direct naar het volgende item.")

####################################################################################################

def DumpertPage(sender, pageUrl, pageIndex, viewGroup, title=None):
  if not title:
    title = sender.itemTitle

  dir = MediaContainer(title2=title+" (" + str(pageIndex+1) + ")", noCache=True)
  dir.viewGroup = viewGroup
  dir = ParsePage(dir, pageUrl, pageIndex, title, REGEX_PAGE_ITEM, viewGroup)
  return dir

####################################################################################################

def SearchPage(sender, pageUrl, pageIndex, viewGroup, query, title=None):
  if not title:
    title = sender.itemTitle

  keywords = query.replace(" ", "%20")
  pageUrl = pageUrl + keywords + "/"

  dir = MediaContainer(title2=title+" (" + str(pageIndex+1) + ")", noCache=True)
  dir.viewGroup = viewGroup
  dir = ParsePage(dir, pageUrl, pageIndex, title, REGEX_PAGE_ITEM, viewGroup)

  return dir

####################################################################################################

def ParsePage(dir, url, index, title, regex, viewGroup):
  urlItems = url + str(index) + "/"
  data = HTTP.Request(urlItems).content.decode('latin-1')

  results = re.compile(regex, re.DOTALL + re.IGNORECASE + re.M).findall(data)
  for result in results:
    if Prefs['comments'] == "aan":
      if viewGroup == "Photos":
	    dir.Append(Function(DirectoryItem(OpenPhotoItem, title=result[4], summary=result[5], thumb=Function(GetThumb, url=result[3])), title=result[4], summary=result[5], thumb=result[3], idPartOne = result[0], idPartTwo = result[1]))
      else:
        dir.Append(Function(DirectoryItem(OpenVideoItem, title=result[4], summary=result[5], thumb=Function(GetThumb, url=result[3])), title=result[4], summary=result[5], thumb=result[3], idPartOne = result[0], idPartTwo = result[1]))
    else:
      if viewGroup == "Photos":
        dir.Append(Function(PhotoItem(PlayPhoto, title=result[4], summary=result[4]+"\n"+result[5], thumb=Function(GetThumb, url=result[3])), idPartOne = result[0], idPartTwo = result[1]))
      else:
        dir.Append(Function(VideoItem(PlayVideo, title=result[4], summary=result[5], thumb=Function(GetThumb, url=result[3])), idPartOne = result[0], idPartTwo = result[1]))

  results_ouder = re.compile(REGEX_OUDER, re.DOTALL + re.IGNORECASE + re.M).findall(data)
  if len(results_ouder) > 0:
    dir.Append(Function(DirectoryItem(DumpertPage, title="[OUDER]", summary="Oudere items (pagina " + str(index+2) + ")", thumb=R(PLUGIN_ICON_NEXT)), pageUrl = url, pageIndex = index+1, viewGroup=viewGroup, title = title))

  if len(results) == 0: return MessageContainer("Zoekresultaat", "Er zijn geen items gevonden.")
  else: return dir

####################################################################################################

def OpenVideoItem(sender, title, summary, thumb, idPartOne, idPartTwo):
  dir = MediaContainer(title2=title, noCache=True)
  dir.viewGroup = 'Details'

  #play button
  dir.Append(Function(VideoItem(PlayVideo, title="Play", summary=title+"\n\n"+summary, thumb=Function(GetThumb, url=thumb)), idPartOne=idPartOne, idPartTwo=idPartTwo)) 

  #append comments
  commentsUrl = "http://dumpcomments.geenstijl.nl/"+idPartOne+"_"+idPartTwo+".js"
  dir = ParseComments(dir, commentsUrl, REGEX_COMMENTS, thumb, idPartOne, idPartTwo, mediaType='video')

  return dir

####################################################################################################

def OpenPhotoItem(sender, title, summary, thumb, idPartOne, idPartTwo):
  dir = MediaContainer(title2=title, noCache=True)
  dir.viewGroup = 'Details'

  #play button
  urls = ImageUrls(idPartOne, idPartTwo)
  i=1
  for img in urls:
    dir.Append(PhotoItem(img, title=title + " (" +str(i)+")", summary=title+"\n"+summary, thumb=Function(GetThumb, url=img))) 
    i = i + 1

  #append comments
  commentsUrl = "http://dumpcomments.geenstijl.nl/"+idPartOne+"_"+idPartTwo+".js"
  dir = ParseComments(dir, commentsUrl, REGEX_COMMENTS, img, idPartOne, idPartTwo, mediaType='photo')

  return dir

####################################################################################################

def ParseComments(dir, url, regex, thumb, idPartOne, idPartTwo, mediaType):
  data = HTTP.Request(url).content.decode('latin-1')
  results = re.compile(regex, re.DOTALL + re.IGNORECASE + re.M).findall(data)

  if mediaType == 'video':
    dir.Append(Function(VideoItem(PlayVideo, title="", thumb=thumb), idPartOne=idPartOne, idPartTwo=idPartTwo))
    dir.Append(Function(VideoItem(PlayVideo, title="Comments ("+str(len(results))+")", thumb=thumb), idPartOne=idPartOne, idPartTwo=idPartTwo))
  elif mediaType == 'photo':
    dir.Append(Function(PhotoItem(PlayPhoto, title="", thumb=thumb), idPartOne=idPartOne, idPartTwo=idPartTwo))
    dir.Append(Function(PhotoItem(PlayPhoto, title="Comments ("+str(len(results))+")", thumb=thumb), idPartOne=idPartOne, idPartTwo=idPartTwo))

  for result in results:
    name = result[1]+": "+result[0]
    name = name.replace(".", "")
    name = name.replace("?", "")
    name = name.replace("\\", "")
    name = "   - "+name[:30]
    if len(name) > 30: name = name+"..."

    if mediaType == 'video':
      dir.Append(Function(VideoItem(PlayVideo, title=name, subtitle=result[1], thumb=Function(GetThumb, url=thumb), summary=result[0]), idPartOne=idPartOne, idPartTwo=idPartTwo))
    elif mediaType == 'photo':
      dir.Append(Function(PhotoItem(PlayPhoto, title=name, subtitle=result[1], thumb=Function(GetThumb, url=thumb), summary=result[0]), idPartOne=idPartOne, idPartTwo=idPartTwo))

  return dir

####################################################################################################

def PlayVideo(sender, idPartOne, idPartTwo):
  url = VideoAudioStreamUrl(idPartOne, idPartTwo)

  if url == "":
    return None
  else:
    return Redirect(url)

####################################################################################################

def PlayPhoto(sender, idPartOne, idPartTwo):
  url = ImageUrls(idPartOne, idPartTwo)

  if len(url) == 0:
    return None
  else:
    return Redirect(url[0])

####################################################################################################

def VideoAudioStreamUrl(path1, path2):
  stream = ""
  path = URL_ROOT_URI+ "mediabase/"+path1+"/"+path2+"/index.html"
  data = HTTP.Request(path).content.decode('latin-1')

  results_video = re.compile(REGEX_STREAM, re.DOTALL + re.IGNORECASE + re.M).findall(data)
  for result_video in results_video:
    stream = result_video

  if stream == "":
    results_audio = re.compile(REGEX_AUDIO, re.DOTALL + re.IGNORECASE + re.M).findall(data)
    for result_audio in results_audio:
      stream = result_audio

  # if stream == "":
  #   results_image = re.compile(REGEX_IMAGE, re.DOTALL + re.IGNORECASE + re.M).findall(data)
  #   for result_image in results_image:
  #     stream = result_image

  return stream

####################################################################################################

def ImageUrls(path1, path2):
  stream = ""
  path = URL_ROOT_URI+ "mediabase/"+path1+"/"+path2+"/index.html"
  data = HTTP.Request(path).content.decode('latin-1')

  stream = re.compile(REGEX_IMAGE, re.DOTALL + re.IGNORECASE + re.M).findall(data)

  if len(stream) == 0:
    stream = re.compile(REGEX_IMAGE2, re.DOTALL + re.IGNORECASE + re.M).findall(data)

  return stream

####################################################################################################

def GetThumb(url):
  try:
    image = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
    return DataObject(image, 'image/jpeg')
  except:
    return Redirect(R(PLUGIN_ICON_DEFAULT))
