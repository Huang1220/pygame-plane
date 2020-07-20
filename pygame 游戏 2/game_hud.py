import pygame

from game_items import *

class HUDPanel(object):

    margin = 10
    white = (255, 255, 255)
    gray = (64, 64, 64)

    reward_score = 100000
    level2_score = 10000
    level3_score = 50000

    record_filename = 'record.txt'

    def __init__(self, display_group):

        self.score = 0
        self.lives_count = 3
        self.level = 1
        self.best_score = 0


        self.status_sprite = StatusButton(('pause.png','resume.png'), display_group)
        self.status_sprite.rect.topleft = (self.margin, self.margin)
        
        self.bomb_sprite = GameSprite('bomb.png', 0, display_group)
        self.bomb_sprite.rect.x = self.margin
        self.bomb_sprite.rect.bottom = SCREEN_RECT.bottom - self.margin

        self.score_label = Label('%d'%self.score, 32, self.gray, display_group)
        self.score_label.rect.midleft = (self.status_sprite.rect.right + self.margin,
                                         self.status_sprite.rect.centery)

        self.bomb_label = Label('X 3', 32, self.gray, display_group)
        self.bomb_label.rect.midleft = (self.bomb_sprite.rect.right + self.margin,
                                        self.bomb_sprite.rect.centery)

        self.lives_label = Label('X %d'%self.lives_count, 32, self.gray, display_group)
        self.lives_label.rect.midright = (SCREEN_RECT.right - self.margin,
                                          self.bomb_sprite.rect.centery)
        
        self.lives_sprite = GameSprite('life.png', 0, display_group)
        self.lives_sprite.rect.right = self.lives_label.rect.x - self.margin
        self.lives_sprite.rect.bottom = SCREEN_RECT.bottom - self.margin


        self.best_label = Label('Best:%d'%self.best_score, 36, self.white)
        self.best_label.rect.center = SCREEN_RECT.center

        self.status_label = Label('Game Paused!', 48, self.white)
        self.status_label.rect.midbottom = (self.best_label.rect.centerx,
                                            self.best_label.rect.y - 2 * self.margin)

        self.tip_label = Label('Press spacebar to continue.', 22, self.white)
        self.tip_label.rect.midtop = (self.best_label.rect.centerx,
                                      self.best_label.rect.bottom + 8 * self.margin)

        self.load_best_score()
        print('你的最好得分是：', self.best_score, '，继续加油哦！')


    def show_bomb(self, count):

        self.bomb_label.set_text('X %d'%count)
        self.bomb_label.rect.midleft = (self.bomb_sprite.rect.right + self.margin,
                                        self.bomb_sprite.rect.centery)
        
    def show_lives(self):

        self.lives_label.set_text('X %d'%self.lives_count)

        self.lives_label.rect.midright = (SCREEN_RECT.right - self.margin,
                                          self.bomb_sprite.rect.centery)

        self.lives_sprite.rect.right = self.lives_label.rect.x - self.margin

    def increase_score(self, enemy_score):


        score = self.score + enemy_score

        if score // self.reward_score != self.score // self.reward_score:
            self.lives_count += 1
            self.show_lives()

        self.score = score

        self.best_score = score if score > self.best_score else self.best_score

        if score < self.level2_score:
            level = 1
        elif score < self.level3_score:
            level = 2
        else:
            level = 3

        is_upgrade = level != self.level
        self.level = level

        self.score_label.set_text('%d'%score)
        self.score_label.rect.midleft = (self.status_sprite.rect.right + self.margin,
                                         self.status_sprite.rect.centery)
        
        return is_upgrade

    def save_best_score(self):

        file = open(self.record_filename, 'w')
        file.write('%d'%self.best_score)
        file.close()

    def load_best_score(self):

        try:

            file = open(self.record_filename, 'r')
            content = file.read()
            file.close()

            self.best_score = int(content)

        except (FileNotFoundError, ValueError):
            print('读取最高得分文件时发生了异常(；′⌒`)，请检查文件！')

    def panel_paused(self, is_game_over, display_group):

        if display_group.has(self.best_label, self.status_label, self.tip_label):
            return
        
        status = 'Game Over!' if is_game_over else 'Game Paused!'
        tip = 'Press spacebar to '
        tip += 'play again.' if is_game_over else 'continue.'

        self.best_label.set_text('Best:%d'%self.best_score)
        self.status_label.set_text(status)
        self.tip_label.set_text(tip)

        self.best_label.rect.center = SCREEN_RECT.center

        self.status_label.rect.midbottom = (self.best_label.rect.centerx,
                                            self.best_label.rect.y - 2 * self.margin)

        self.tip_label.rect.midtop = (self.best_label.rect.centerx,
                                      self.best_label.rect.bottom + 8 * self.margin)

        display_group.add(self.best_label, self.status_label, self.tip_label)

        self.status_sprite.swich_status(True)
    
    def panel_resume(self, display_group):

        display_group.remove(self.best_label, self.status_label, self.tip_label)

        self.status_sprite.swich_status(False)

    def reset_panel(self):

        self.score = 0
        self.lives_count = 3

        self.increase_score(0)
        self.show_bomb(3)
        self.show_lives()



