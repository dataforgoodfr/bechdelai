from transformers import pipeline


class SpeechRecognition:
    """Speech recognition model for audio files."""

    def __init__(self, model_name="openai/whisper-small"):
        """Initialize speech recognition model.

        Args:
            language (str): target language
            task (str): transcribe for same language or translate to another language
            model_name (str): Whisper model name. Defaults to "openai/whisper-small".
        """
        self.pipe = pipeline(
            task="automatic-speech-recognition",
            model=model_name,
            chunk_length_s=30,
            stride_length_s=(5, 5),
            return_timestamps=True,
            generate_kwargs={"max_length": 1000},
        )

    def transcribe(self, audio_path, language, task="transcribe"):
        """Transcribe audio file.

        Args:
            audio_path (str): Path to audio file
            language (str): target language
            task (str): transcribe for same language or translate to another language

        Returns:
            Dict: Transcribed text
        """
        self.pipe.model.config.forced_decoder_ids = (
            self.pipe.tokenizer.get_decoder_prompt_ids(language=language, task=task)
        )
        return self.pipe(audio_path)
