from .models import Argument
from django.conf import settings
from .services import receive_sound, receive_text_to_speech_token
import os


def add_sounds():
    """
    This function tells every english argument where the corresponding mp3 soundfile is and
    creates new files which are not there yet.
    :return:
    """
    text_to_speech = receive_text_to_speech_token()
    if text_to_speech is not None:
        for arg in Argument.objects.all().filter(lang='en'):
            if os.path.exists(settings.BASE_DIR + settings.MEDIA_URL + str(arg.id) + '.mp3') is False:
                mp3_sound = receive_sound(text=arg.text, text_to_speech=text_to_speech)
                if mp3_sound is not None:
                    with open(settings.BASE_DIR + settings.MEDIA_URL + str(arg.id) + '.mp3', 'wb') as audio_file:
                        audio_file.write(mp3_sound)
            #  we need to make sure that we really want to safe the path, in order to achieve it we need to
            #  be sure that there is a file now.
            if os.path.exists(settings.BASE_DIR + settings.MEDIA_URL + str(arg.id) + '.mp3') is True:
                arg.sound = settings.MEDIA_URL + str(arg.id) + '.mp3'
                arg.save()
    else:
        print('The API Access is denied')
