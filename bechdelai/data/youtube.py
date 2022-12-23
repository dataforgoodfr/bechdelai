from pytube import YouTube


def download_youtube_video(link: str, filename: str, caption_language: str) -> None:
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

    try:
        (
            yt.streams.filter(progressive=True, file_extension="mp4")
            .order_by("resolution")
            .desc()
            .first()
        ).download(filename=f"{filename}.mp4")

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
