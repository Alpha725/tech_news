import requests
import feedparser
import boto3
from datetime import datetime
import re
import html

def get_page_contents(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        return response.text
    except requests.RequestException as e:
        return f"An error occurred: {e}"

def parse_rss_feed(rss_content):
    feed = feedparser.parse(rss_content)
    return feed 

def text_to_speech(title, description):
    clean_title = title
    clean_description = html.unescape(re.sub('<[^<]+?>', '', description))
    full_text = f"{clean_title}. {clean_description}"
    date_str = datetime.now().strftime("%Y-%m-%d-%S-%f")
    title_slug = re.sub(r'\W+', '_', clean_title.lower())[:10]
    filename = f"{date_str}_{title_slug}.mp3"
    polly_client = boto3.Session().client('polly')
    try:
        response = polly_client.synthesize_speech(
            Text=full_text,
            OutputFormat='mp3',
            VoiceId='Matthew'
        )
        if "AudioStream" in response:
            with open(filename, 'wb') as file:
                file.write(response['AudioStream'].read())
            print(f"Audio file saved as {filename}")
        else:
            print("Could not generate audio stream")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# url = "https://www.reddit.com/r/linux/top.rss"
url = "https://distrowatch.com/news/dw.xml"
# url = "https://www.reddit.com/r/anime_titties/hot.rss"


RSS = get_page_contents(url)
parsed_feed = parse_rss_feed(RSS)
for story in parsed_feed.entries:
    text_to_speech(str(story.title), str(story.description))
