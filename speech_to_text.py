import os
import speech_recognition as sr


class SpeechToText:
    """
    Recognize speech using Google Cloud Speech
    """

    def __init__(self, creds_file_path='creds.json'):
        self.text = None
        self.creds = creds_file_path
        self.recognizer = sr.Recognizer()

    def recognize(self, audio_file, language="en-US"):
        """
        Recognize speech from audio using Google Cloud Speech
        :param audio_file: audio file
        :param language: languages
        :return: text
        """
        # use the audio file as the audio source
        audio_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), audio_file)
        with sr.AudioFile(audio_path) as source:
            audio = self.recognizer.record(source)
        try:
            text = self.recognizer.recognize_google_cloud(
                audio,
                language=language,
                credentials_json=open(self.creds).read()
            )
        except sr.UnknownValueError:
            print("Google Cloud Speech could not understand audio")
            return
        except sr.RequestError as e:
            return
        return text
