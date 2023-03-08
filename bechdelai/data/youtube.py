from pytube import YouTube
import urllib.parse as urlparse

try:
    from IPython.display import display,HTML
except:
    print("Jupyter is not installed, you may encounter a few errors")


def download_youtube_video(link: str, filename: str, download_captions:bool = False,caption_language: str = "en") -> None:
    """Download a youtube video with captions given an id

    Parameters
    ----------
    link : str
        Youtube video link
    filename : str
        File name to save the video and the caption
    caption_language : str
        Language caption to download

    Raises
    ------
    TypeError
        url must be a string
    ValueError
        url must start with 'http'
    """
    try:
        yt = YouTube(link)
    except:
        print("Connection Error")
        return

    filename = filename if filename.endswith(".mp4") else filename + ".mp4"

    try:
        (
            yt.streams.filter(progressive=True, file_extension="mp4")
            .order_by("resolution")
            .desc()
            .first()
        ).download(filename=filename)

        print(f"Saved the youtube video at {filename}")

    except Exception as e:
        print("Could not download the video!", e)

    if download_captions:
        try:
            captions = {
                k: v
                for k, v in yt.captions.lang_code_index.items()
                if caption_language in k
            }
            for lang, caption in captions.items():
                caption.download(title=f"caption_{lang}", srt=False)
        except Exception as e:
            print("Could not download the caption!", e)
        print("Task Completed!")


def get_youtube_video_id_from_url(url):
    """
    From https://stackoverflow.com/questions/48072619/how-can-i-import-urlparse-in-python-3
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    query = urlparse.urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = urlparse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None


def show_youtube_in_notebook(url):

    video_id = get_youtube_video_id_from_url(url)

    html = f"""
    <center> 
    <iframe width="500" height="320" src="https://www.youtube.com/embed/{video_id}"></iframe>
    </center>
    """

    display(HTML(html))