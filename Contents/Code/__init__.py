import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

####################################################################################################

PLUGIN_TITLE   = "Dumpert"
PLUGIN_VIDEO_PREFIX  = "/video/dumpert"
PLUGIN_IMAGE_PREFIX  = "/photos/dumpert"

# URLS
URL_ROOT_URI       = "http://www.dumpert.nl/"
URL_TOPPERS        = URL_ROOT_URI + "toppers/"
URL_FILMPJES       = URL_ROOT_URI + "filmpjes/"
URL_PLAATJES       = URL_ROOT_URI + "plaatjes/"
URL_AUDIO          = URL_ROOT_URI + "audio/"
URL_VIDEO_ZOEKEN   = URL_ROOT_URI + "search/MV/"
URL_PHOTO_ZOEKEN   = URL_ROOT_URI + "search/F/"

# OTHER VARS
DEFAULT_PAGE = 0
NEXT_PAGE = 0
CURRENT_PAGE = ""
CACHE_INTERVAL = 3600

# REGULAR EXPRESSIONS
REGEX_PAGE_ITEM = r"""<a class="item" href="http://www.dumpert.nl/mediabase/([0-9]+)/([0-9a-f]+)/([^<]+).html">\s+<img src="([^<]+)" alt="[^<]+" title="[^<]+" width="100" height="100" />\s+<div class="info">\s+<h3>([^<]+)</h3>\s+<div class="date">[^<]+</div>\s+<p>([^<]+)</p>"""
REGEX_STREAM = r"""autoStart=true&file=([^<]+)&recommendations"""
REGEX_AUDIO = r"""file=([^<]+)&config"""
REGEX_IMAGE = r"""<img src="([^<]+)" onclick="window.open"""
REGEX_IMAGE2 = r"""<img src="([^<]+)" class="picca" """
REGEX_OUDER = r"""<span>Ouder</span>"""
REGEX_COMMENTS = r"""comments.push\('<p>([^<]+)</p>'\);\s+comments.push\('<p class="footer">([^<]+) ([0-9]+)-([0-9]+)-([0-9]+) @"""

# Default artwork and icon(s)
PLUGIN_ARTWORK = "art-default.png"
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
  Plugin.AddPrefixHandler(PLUGIN_IMAGE_PREFIX, MainMenuAudio, PLUGIN_TITLE, PLUGIN_ICON_DEFAULT, PLUGIN_ARTWORK)

  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  Plugin.AddViewGroup("Photos", viewMode="Pictures", mediaType="photos")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")

  # Set the default MediaContainer attributes
  MediaContainer.title1 = PLUGIN_TITLE
  MediaContainer.viewGroup = 'List'
  MediaContainer.art = R('art-default.jpg')

  # Set the default cache time
  HTTP.SetCacheTime(CACHE_INTERVAL)

####################################################################################################

def MainMenuVideo():
    dir = MediaContainer(noCache=True) 
    dir.Append(Function(DirectoryItem(DumpertPage, title="Toppers", thumb=R(PLUGIN_ICON_TOPPERS), art=R(PLUGIN_ARTWORK)), pageUrl = URL_TOPPERS, pageIndex = DEFAULT_PAGE, viewGroup='Details'))
    dir.Append(Function(DirectoryItem(DumpertPage, title="Filmpjes", thumb=R(PLUGIN_ICON_FILMPJES), art=R(PLUGIN_ARTWORK)), pageUrl = URL_FILMPJES, pageIndex = DEFAULT_PAGE, viewGroup='Details'))
    dir.Append(Function(DirectoryItem(DumpertPage, title="Audio", thumb=R(PLUGIN_ICON_AUDIO), art=R(PLUGIN_ARTWORK)), pageUrl = URL_AUDIO, pageIndex = DEFAULT_PAGE, viewGroup='Details'))
    dir.Append(Function(InputDirectoryItem(SearchPage, title="Zoeken", thumb=R(PLUGIN_ICON_ZOEKEN), art=R(PLUGIN_ARTWORK), prompt="Zoeken"), pageUrl = URL_VIDEO_ZOEKEN, pageIndex = DEFAULT_PAGE, viewGroup='Details'))
    dir.Append(PrefsItem(title="Instellingen", thumb=R(PLUGIN_ICON_SETTINGS), art=R(PLUGIN_ARTWORK)))
    dir.Append(Function(DirectoryItem(AboutVideoPage, title="Help", thumb=R(PLUGIN_ICON_HELP), art=R(PLUGIN_ARTWORK))))

    return dir

####################################################################################################

def MainMenuAudio():
    dir = MediaContainer(noCache=True) 
    dir.Append(Function(DirectoryItem(DumpertPage, title="Plaatjes", thumb=R(PLUGIN_ICON_PLAATJES), art=R(PLUGIN_ARTWORK)), pageUrl = URL_PLAATJES, pageIndex = DEFAULT_PAGE, viewGroup='Photos'))
    dir.Append(Function(InputDirectoryItem(SearchPage, title="Zoeken", thumb=R(PLUGIN_ICON_ZOEKEN), art=R(PLUGIN_ARTWORK), prompt="Zoeken"), pageUrl = URL_PHOTO_ZOEKEN, pageIndex = DEFAULT_PAGE, viewGroup='Photos'))
    dir.Append(PrefsItem(title="Instellingen", thumb=R(PLUGIN_ICON_SETTINGS), art=R(PLUGIN_ARTWORK)))
    dir.Append(Function(DirectoryItem(AboutAudioPage, title="Help", thumb=R(PLUGIN_ICON_HELP), art=R(PLUGIN_ARTWORK))))

    return dir

####################################################################################################

def AboutVideoPage(sender):
  return MessageContainer("Help", "Als je in de sectie 'Toppers' de melding 'Could not read from input\nstream' krijgt, dan komt dit doordat de video-plugin een afbeelding\nprobeert te open. Gebruik hiervoor de afbeeldingen-plugin.")

####################################################################################################
def AboutAudioPage(sender):
  return MessageContainer("Help", "Als het commentaar uit staat, dan kan je alleen de eerste foto van elk\nitem bekijken. Je kan dan echter wel direct naar het volgende item.")

####################################################################################################

def DumpertPage(sender, pageUrl, pageIndex, viewGroup):
  global NEXT_PAGE, CURRENT_PAGE

  title = sender.itemTitle
  if title == "[OUDER]": 
      title = CURRENT_PAGE
  CURRENT_PAGE = title
  NEXT_PAGE = pageIndex + 1

  dir = MediaContainer(title2=title+" (" + str(pageIndex+1) + ")", noCache=True, art=R(PLUGIN_ARTWORK))
  dir.viewGroup = viewGroup
  dir = ParsePage(dir, pageUrl, REGEX_PAGE_ITEM, viewGroup)
  return dir

####################################################################################################

def SearchPage(sender, pageUrl, pageIndex, viewGroup, query):
  global NEXT_PAGE, CURRENT_PAGE

  keywords = query.replace(" ", "%20")
  pageUrl = pageUrl + keywords + "/" 
  
  title = query
  CURRENT_PAGE = title
  NEXT_PAGE = pageIndex + 1

  dir = MediaContainer(title2=title+" (" + str(pageIndex+1) + ")", noCache=True, art=R(PLUGIN_ARTWORK))
  dir.viewGroup = viewGroup
  dir = ParsePage(dir, pageUrl, REGEX_PAGE_ITEM, viewGroup)

  return dir

####################################################################################################

def ParsePage(dir, url, regex, viewGroup):
  global NEXT_PAGE
    
  urlItems = url + "/" + str(NEXT_PAGE-1)+ "/"
  data = HTTP.Request(urlItems).decode('latin-1')

  results = re.compile(regex, re.DOTALL + re.IGNORECASE + re.M).findall(data)
  for result in results:
    if Prefs.Get('comments') == "aan":
      if viewGroup == "Photos":
	    dir.Append(Function(DirectoryItem(OpenPhotoItem, title=result[4], summary=result[5], thumb=result[3]), title=result[4], summary=result[5], thumb=result[3], idPartOne = result[0], idPartTwo = result[1]))
      else:
        dir.Append(Function(DirectoryItem(OpenVideoItem, title=result[4], summary=result[5], thumb=result[3]), title=result[4], summary=result[5], thumb=result[3], idPartOne = result[0], idPartTwo = result[1]))
    else:
      if viewGroup == "Photos":
        dir.Append(Function(PhotoItem(PlayPhoto, title=result[4], summary=result[4]+"\n"+result[5], thumb=result[3]), idPartOne = result[0], idPartTwo = result[1]))
      else:
        dir.Append(Function(VideoItem(PlayVideo, title=result[4], summary=result[5], thumb=result[3]), idPartOne = result[0], idPartTwo = result[1]))
 
  results_ouder = re.compile(REGEX_OUDER, re.DOTALL + re.IGNORECASE + re.M).findall(data)
  if len(results_ouder) > 0:
    dir.Append(Function(DirectoryItem(DumpertPage, title="[OUDER]", summary="Oudere items (pagina " + str(NEXT_PAGE+1) + ")", thumb=R(PLUGIN_ICON_NEXT)), pageUrl = url, pageIndex = NEXT_PAGE, viewGroup='Details'))

  if len(results) == 0: return MessageContainer("Zoekresultaat", "Er zijn geen items gevonden.")
  else: return dir


####################################################################################################

def OpenVideoItem(sender, title, summary, thumb, idPartOne, idPartTwo):
  dir = MediaContainer(title2=title, noCache=True, art=R(PLUGIN_ARTWORK))
  dir.viewGroup = 'Details'

  #play button
  dir.Append(Function(VideoItem(PlayVideo, title="Play", summary=title+"\n\n"+summary, thumb=thumb), idPartOne=idPartOne, idPartTwo=idPartTwo)) 

  #append comments
  commentsUrl = "http://dumpcomments.geenstijl.nl/"+idPartOne+"_"+idPartTwo+".js"
  dir = ParseComments(dir, commentsUrl, REGEX_COMMENTS, thumb)
  
  return dir

####################################################################################################

def OpenPhotoItem(sender, title, summary, thumb, idPartOne, idPartTwo):
  dir = MediaContainer(title2=title, noCache=True, art=R(PLUGIN_ARTWORK))
  dir.viewGroup = 'List'

  #play button
  urls = ImageUrls(idPartOne, idPartTwo)
  i=1
  for img in urls:
    dir.Append(PhotoItem(img, title=title + " (" +str(i)+")", summary=title+"\n"+summary, thumb=img)) 
    i = i + 1

  #append comments
  commentsUrl = "http://dumpcomments.geenstijl.nl/"+idPartOne+"_"+idPartTwo+".js"
  dir = ParseComments(dir, commentsUrl, REGEX_COMMENTS, img)

  return dir

####################################################################################################

def ParseComments(dir, url, regex, thumb):
	
  data = HTTP.Request(url).decode('latin-1')
  results = re.compile(regex, re.DOTALL + re.IGNORECASE + re.M).findall(data)

  dir.Append(DirectoryItem("none", title="", thumb=thumb))
  dir.Append(DirectoryItem("none", title="Comments ("+str(len(results))+")", thumb=thumb))

  for result in results:
    name = result[1]+": "+result[0]
    name = name.replace(".", "")
    name = name.replace("?", "")
    name = name.replace("\\", "")
    name = "   - "+name[:30]
    if len(name) > 30: name = name+"..."
    dir.Append(DirectoryItem("none", title=name, subtitle=result[1], thumb=thumb, summary=result[0]))

  return dir

####################################################################################################

def PlayVideo(sender, idPartOne, idPartTwo):
	
  url = VideoAudioStreamUrl(idPartOne, idPartTwo)

  if url=="":
    return None
  else:
	return Redirect(url)

####################################################################################################


def PlayPhoto(sender, idPartOne, idPartTwo):

  url = ImageUrls(idPartOne, idPartTwo)

  if len(url)==0:
    return None
  else:
	return Redirect(url[0])


####################################################################################################

def VideoAudioStreamUrl(path1, path2):
  stream = ""
  path = URL_ROOT_URI+ "mediabase/"+path1+"/"+path2+"/index.html"
  data = HTTP.Request(path).decode('latin-1')

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
  data = HTTP.Request(path).decode('latin-1')

  stream = re.compile(REGEX_IMAGE, re.DOTALL + re.IGNORECASE + re.M).findall(data)

  if len(stream) == 0:
    stream = re.compile(REGEX_IMAGE2, re.DOTALL + re.IGNORECASE + re.M).findall(data)


  return stream
