import re

TITLE = 'Dumpert'
BASE_URL = 'http://www.dumpert.nl'
TOPPERS = '%s/toppers' % BASE_URL
THEMAS = '%s/themas' % BASE_URL
PAGE = '%s/%d/'

ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_MORE = 'icon-next.png'

####################################################################################################
def Start():
  Plugin.AddPrefixHandler('/video/dumpert', MainMenu, TITLE, ICON, ART)
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

  ObjectContainer.title1 = TITLE
  ObjectContainer.art = R(ART)
  ObjectContainer.view_group = 'InfoList'
  DirectoryObject.thumb = R(ICON)
  VideoClipObject.thumb = R(ICON)

  HTTP.CacheTime = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:8.0) Gecko/20100101 Firefox/8.0'

####################################################################################################
def MainMenu():
  oc = ObjectContainer()

  oc.add(DirectoryObject(key=Callback(Videos, title='Filmpjes', url=BASE_URL), title='Filmpjes'))
  oc.add(DirectoryObject(key=Callback(Videos, title='Toppers', url=TOPPERS), title='Toppers'))
  oc.add(DirectoryObject(key=Callback(Themas, title='Thema\'s'), title='Thema\'s'))

  return oc

####################################################################################################
def Videos(title, url, page=1):
  oc = ObjectContainer(title2=title)
  content = HTML.ElementFromURL(PAGE % (url, page), headers={'Cookie':'filter=video'})

  for video in content.xpath('//section[@id="content"]/a[@class="dumpthumb"]/span[@class="video"]/..'):
    vid_url = video.get('href')
    vid_title = video.xpath('.//h1')[0].text
    summary = video.xpath('.//p[@class="description"]')[0].text
    date = video.xpath('.//date')[0].text
    date = Datetime.ParseDate(date).date()
    thumb = video.xpath('./img')[0].get('src')

    oc.add(VideoClipObject(
      url = vid_url,
      title = vid_title,
      summary = summary,
      originally_available_at = date,
      thumb = Callback(GetThumb, url=thumb)
    ))

  if len(oc) == 0:
    return MessageContainer('Geen video\'s', 'Deze directory bevat geen video\'s')

  else:
    if len(content.xpath('//li[@class="volgende"]')) > 0:
      oc.add(DirectoryObject(key=Callback(Videos, title='Filmpjes', url=url, page=page+1), title='Meer ...', thumb=R(ICON_MORE)))

    return oc

####################################################################################################
def Themas(title):
  oc = ObjectContainer(title2=title)

  for thema in HTML.ElementFromURL(THEMAS).xpath('//section[@id="content"]/a[contains(@class,"themalink")]'):
    title = thema.xpath('.//h1')[0].text
    url = thema.get('href').rstrip('/')
    thumb = thema.xpath('./img')[0].get('src').replace('_kl.jpg', '_gr.jpg')

    oc.add(DirectoryObject(key=Callback(Videos, title=title, url=BASE_URL + url), title=title, thumb=Callback(GetThumb, url=thumb)))

  oc.objects.sort(key = lambda obj: obj.title)
  return oc

####################################################################################################
def GetThumb(url):
  try:
    image = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
    return DataObject(image, 'image/jpeg')
  except:
    return Redirect(R(ICON))
