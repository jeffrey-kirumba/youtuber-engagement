
import datetime
import os
from dao.youtubedao import DataAccessObject
from dao.vars import *
from crunch.channelEngagement import YoutubeMetrics
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from pytz import timezone
from dotenv import load_dotenv
load_dotenv()

utc = timezone('UTC')
API_SERVICE_NAME = os.getenv('API_SERVICE_NAME')
API_VERSION = os.getenv('API_VERSION')
CLIENT_SECRETS_FILE = os.getenv('CLIENT_SECRETS_FILE')
DEVELOPER_KEY = os.getenv('DEVELOPER_KEY')

class Youtubers:
    def __init__(self, update) -> None:
        self.channels = []
        self.update = update
        self.tubeDAO = DataAccessObject(tableName="YOUTUBE_CHANNELS")

    def get_authenticated_service(self):
        youtuber = build('youtube', 'v3', developerKey=DEVELOPER_KEY)
        return youtuber
  
    def searchVids(self, you, searchTerm, pageToken, pageCount):
            request = you.search().list(part='snippet', q=searchTerm, maxResults=50, pageToken=pageToken)
            response = request.execute()
            for i in range(len(response['items'])):
                searchResult = response['items'][i]
                channelId = searchResult['snippet']['channelId']
                channelName = searchResult['snippet']['channelTitle']
                if channelId not in self.channels:
                    self.getChannel(you=you, channelId=channelId, channelName=channelName, searchTerm=searchTerm)
                if i == len(response['items']) -1 and 'nextPageToken' in response and pageCount < 5:
                    #if last, next page using token, max five result sets
                    pageCount+=1
                    self.searchVids(you=you, searchTerm=searchTerm, pageToken=response['nextPageToken'], pageCount=pageCount)
        
    def getVid(self, you, videoId):
        try:
            request = you.videos().list(part='snippet,contentDetails,statistics', id=videoId)
            response = request.execute()
            if len(response['items']) > 0:
                return response['items'][0]
        except Exception as e:
            print(f"Exception in get vid: {e}")
    
    def getChannel(self, you, channelId, channelName, searchTerm):
        try:
            #query channel here
            if not self.update and len(self.tubeDAO.query({'channel_id': channelId})) > 0:
                return
            request = you.channels().list(part='snippet,contentDetails,statistics',
                id=channelId)
            response = request.execute()
            totalView = int(response['items'][0]['statistics']['viewCount'])
            subs = int(response['items'][0]['statistics']['subscriberCount'])
            self.handleChannel(you=you, channelId=channelId, channelName=channelName, searchTerm=searchTerm, subs=subs, totalView=totalView, pageToken=None)
        except Exception as e:
            print(f"Exception in get channel: {e}")
  
    def handleChannel(self, you, channelId, channelName, searchTerm, subs, totalView, pageToken):
        try:
            videos = []
            request = you.search().list(part='snippet', channelId=channelId, pageToken=pageToken, maxResults=50, type='video',)
            response = request.execute()
            for i in range(len(response['items'])):
                if 'videoId' in response['items'][i]['id']:
                    videoId = response['items'][i]['id']['videoId']
                    video = self.getVid(you=you, videoId=videoId)
                    videos.append(video)
                    if i == len(response['items']) -1 and 'nextPageToken' in response:
                        #use page token to get next set
                        self.handleChannel(you=you, channelId=channelId, channelName=channelName, searchTerm=searchTerm, subs=subs, totalView=totalView, pageToken=response['nextPageToken'])

            ym = YoutubeMetrics(channelName=channelName, channelId=channelId, videos=videos, totalSubs=subs)
            ym.calcEngagmentRate()

            values = {}
            values['channel_id'] = channelId
            values['name'] = channelName
            values['subs'] = subs
            values['total_views'] = totalView
            values['avg_engagement_rate'] = ym.engagementRate
            values['search_term'] = searchTerm
            results = self.tubeDAO.query(values=values)
            rn = datetime.datetime.now().isoformat()
            if not results: 
                #insert
                values['creation_date'] = rn
                values['update_date'] = rn
                self.tubeDAO.insert(values=values)
            elif self.update:
                #update
                values['update_date'] = rn
                self.tubeDAO.update(values=values)
            return response
        except Exception as e:
            print(f"Exception in handle channel: {e}")

    def main(self):
        you = self.get_authenticated_service()
        for searchTerm in searchTerms[0:3]:
            self.searchVids(you=you, searchTerm=searchTerm, pageToken=None, pageCount=0)
        pass
you = Youtubers(False)
you.main()

