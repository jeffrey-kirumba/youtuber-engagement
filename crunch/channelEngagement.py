#using all vids on channel 
#return Avg Engagement Rate, TotalSubs, TotalViews
class YoutubeMetrics:
    def __init__(self, channelName, channelId, videos, totalSubs) -> None:
        self.channelName =  channelName
        self.channelId = channelId
        self.videos = videos
        self.totalSubs = totalSubs
        self.engagementRate = None

    def calcEngagmentRate(self):
        #enagement rate = (Total engagement / Total Subscribers) * 100
        #Total engagement = total per vid, entire channel (Likes, Dislikes, Comments, Shares)
        totalEngagement = 0
        for video in self.videos:
            if 'statistics' in video:
                try:
                    if 'likeCount' in video['statistics']:
                        totalEngagement += int(video['statistics']['likeCount'])
                    if 'dislikeCount' in video['statistics']:
                        totalEngagement += int(video['statistics']["dislikeCount"])
                    if 'commentCount' in video['statistics']:
                        totalEngagement += int(video['statistics']['commentCount'])
                    if 'favoriteCount' in video['statistics']:
                        totalEngagement += int(video['statistics']["favoriteCount"])
                except Exception as e:
                    print(f"Exception in channel engagement rate calc: {e}")
        self.engagementRate = totalEngagement/self.totalSubs
