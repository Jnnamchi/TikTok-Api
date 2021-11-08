from flask import Flask
from flask import request
from TikTokApi import TikTokApi
from datetime import datetime
from flask_cors import CORS

cache = {}

api = TikTokApi.get_instance()
results = 10

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)
app.debug = False
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def extractUserDetails(userPost):
    authorDetails = userPost["author"]
    authorStats = userPost["authorStats"]
    return {
        "id": authorDetails["id"],
        "handle": authorDetails["uniqueId"],
        "nickname": authorDetails["nickname"],
        "profilePhoto": authorDetails["avatarLarger"],
        "followers": authorStats["followerCount"],
        "following": authorStats["followingCount"],
        "likes": authorStats["heartCount"],
        "videos": authorStats["videoCount"]
    }

def extractPosts(userPosts):
    posts = []
    for post in userPosts:
        videoDetails = post["video"]
        videoStats = post["stats"]
        userFollowers = post["authorStats"]["followerCount"]
        totalEngagements = videoStats["diggCount"] + videoStats["commentCount"] + videoStats["shareCount"]
        addPost = {
            "id": videoDetails["id"],
            "playAddr": videoDetails["playAddr"],
            "timestamp": post["createTime"],
            "date": datetime.fromtimestamp(post["createTime"]).strftime("%A %B %d %Y %H:%M:%S"),
            "description": post["desc"],
            "downloadAddr": videoDetails["downloadAddr"],
            "duration": videoDetails["duration"],
            "format": videoDetails["format"],
            "height": videoDetails["height"],
            "width": videoDetails["width"],
            "videoQuality": videoDetails["videoQuality"],
            "stats": {
                "playCount": videoStats["playCount"],
                "diggCount": videoStats["diggCount"],
                "commentCount": videoStats["commentCount"],
                "shareCount": videoStats["shareCount"],
                "engagements": totalEngagements,
                "impressionRate": round(100 * videoStats["playCount"] / userFollowers, 2),
                "likeRate": round(100 * videoStats["diggCount"] / userFollowers, 2),
                "commentRate": round(100 * videoStats["commentCount"] / userFollowers, 2),
                "engagementRate": round(100 * totalEngagements / userFollowers, 2),
                "shareRate": round(100 * videoStats["shareCount"] / userFollowers, 2),
            }
        }
        posts.append(addPost)
    return posts

def extractMetrics(posts, followers):
    videosTotal = len(posts)
    playsTotal, likesTotal, commentsTotal, sharesTotal, durationTotal = 0, 0, 0, 0, 0

    for post in posts:
        stats = post["stats"]
        commentCount, likeCount, shareCount, playCount = \
            stats["commentCount"], stats["diggCount"], stats["shareCount"], stats["playCount"]

        playsTotal += playCount
        likesTotal += likeCount
        commentsTotal += commentCount
        sharesTotal += shareCount
        durationTotal += post["duration"]

        # Engagements and EngagementRate
        stats["engagements"] = commentCount + likeCount + shareCount
        stats["engagementRate"] = round(100 * stats["engagements"] / followers, 2)

        # Other Rates
        stats["impressionRate"] = round(100 * playCount / followers, 2)
        stats["likeRate"] = round(100 * likeCount / followers, 2)
        stats["commentRate"] = round(100 * commentCount / followers, 2)
        stats["shareRate"] = round(100 * shareCount / followers, 2)

    avgEngagements = round((likesTotal + commentsTotal + sharesTotal) / videosTotal)
    avgDuration = round(durationTotal / videosTotal, 1)
    avgPlays = round(playsTotal / videosTotal)
    avgLikes = round(likesTotal / videosTotal)
    avgComments = round(commentsTotal / videosTotal)
    avgShares = round(sharesTotal / videosTotal)
    metrics = {
        "averages": {
            "avgDuration": avgDuration,
            "avgPlays": avgPlays,
            "avgLikes": avgLikes,
            "avgComments": avgComments,
            "avgShares": avgShares,
            "avgEngagements": avgEngagements,
        },
        "rates": {
            "playRate": round((100 * avgPlays) / followers, 2),
            "likeRate": round((100 * avgLikes) / followers, 2),
            "commentRate": round((100 * avgComments) / followers, 2),
            "shareRate": round((100 * avgShares) / followers, 2),
            "engagementRate": round((100 * avgEngagements) / followers, 2)
        }
    }
    return metrics

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/tiktok')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    # Get auth token
    token = request.args.get('token')
    if token == None or token != 'valuencertoken':
        return {
            "Error": 401,
            "Message": "Not authorized"
        }

    # Get username from url
    username = request.args.get('username')
    if username == None:
        return {
            "Error": 500,
            "Message": "No username specified"
        }

    if username in cache:
        return cache[username]

    userData = api.by_username(username, count=100)

    posts = extractPosts(userData)
    userDetails = extractUserDetails(userData[0])
    data = {
        "userDetails": userDetails,
        "posts": posts,
        "metrics": extractMetrics(posts, userDetails["followers"]),
    }
    cache[username] = data
    return data

# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(host='0.0.0.0', threaded=False)
