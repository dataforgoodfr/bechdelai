def separate_voice_and_music(path_to_mixed_audio: str) -> None:
    """Splits an audio file into its individual parts using spleeter

    Does not work above 700 seconds or about 11 minutes.

    Stores the results in separate folders, upstream of the project root.

    Parameters:
        path_to_mixed_audio (str): Path to an audio file (.wav)

    Returns:
        None
    """
    os.system('spleeter separate -d 700.0 -o ../../../ -f "{instrument}/{filename}.{codec}" ' + path_to_mixed_audio)
