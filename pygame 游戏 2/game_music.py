import pygame
import os

class MusicPlayer(object):

    res_path = './res/sound/'

    def __init__(self, music_file):
        
        pygame.mixer.music.load(self.res_path + music_file)
        pygame.mixer.music.set_volume(0.2)

        self.sound_dict = {}

        files = os.listdir(self.res_path)

        for file in files:
            if file == music_file:
                continue

            sound = pygame.mixer.Sound(self.res_path + file)
            self.sound_dict[file] = sound

    @staticmethod
    def play_music():

        pygame.mixer.music.play(-1)
    
    @staticmethod
    def pause_music(is_pause):

        if is_pause:

            pygame.mixer.music.pause()

        else:

            pygame.mixer.music.unpause()

    def play_sound(self, wav_name):

        self.sound_dict[wav_name].play()
