from pytube import YouTube


def download_youtube_video(link: str, filename: str, caption_language: str = "en") -> None:
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

    except Exception as e:
        print("Could not download the video!", e)

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


def download_youtube_audio(link:str,filename:str = "audio.mp3") -> str:
    yt = YouTube(link)
    stream = yt.streams.filter(only_audio=True)[0]
    stream.download(filename=filename)
    return filename