import pygame
import random

from game_hud import *
from game_items import *
from game_music import *
from game_date import *

IF_DEAD = HERO_IF_DEAD
BULLET_SUPPLY_TIME = SET_BULLET_SUPPLY_TIME * 1000
SUPPLY_TIME = SET_SUPPLY_TIME * 1000
GAME_NAME = SET_GAME_NAME

class Game(object):


    def __init__(self):

        self.main_window = pygame.display.set_mode(SCREEN_RECT.size)
        pygame.display.set_caption(GAME_NAME)

        self.is_game_over = False
        self.is_game_pause = False

        self.all_group = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()
        self.supplies_group = pygame.sprite.Group()

        self.all_group.add(Background(False),Background(True))

        self.hud_panel = HUDPanel(self.all_group)

        self.hero_sprite = Hero(self.all_group)
        self.hud_panel.show_bomb(self.hero_sprite.bomb_count)

        self.create_enemies()

        self.create_supply()

        self.player = MusicPlayer('game_music.ogg')
        self.player.play_music()

    def reset_game(self):

        self.is_game_over = False
        self.is_game_pause = False

        self.hud_panel.reset_panel()

        self.hero_sprite.rect.midbottom = HERO_DEFAULT_MID_BOTTOM

        for enemy in self.enemies_group:
            enemy.kill()

        for bullet in self.hero_sprite.bullets_group:
            bullet.kill()

        self.create_enemies()

    def start(self):

        clock = pygame.time.Clock()

        frame_count = 0

        while True:
            
            self.is_game_over = self.hud_panel.lives_count == 0

            if self.event_handler():

                self.hud_panel.save_best_score()

                return

            if self.is_game_over:

                self.hud_panel.panel_paused(True, self.all_group)
            
            elif self.is_game_pause:

                self.hud_panel.panel_paused(False, self.all_group)
            
            else:

                self.hud_panel.panel_resume(self.all_group)

                keys = pygame.key.get_pressed()
                move_hor = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
                move_ver = keys[pygame.K_DOWN] - keys[pygame.K_UP]

                self.check_collide()

                frame_count = (frame_count + 1) % FRAME_INTERVAL
                self.all_group.update(frame_count == 0, move_hor, move_ver)
                

            self.all_group.draw(self.main_window)

            
            pygame.display.update()


            clock.tick(60)

    def event_handler(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:

                return True
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:

                return True

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:

                if self.is_game_over:

                    self.reset_game()

                else:

                    self.is_game_pause = not self.is_game_pause
                    self.player.pause_music(self.is_game_pause)
        
            if not self.is_game_over and not self.is_game_pause:

                if event.type == pygame.KEYDOWN and event.key == pygame.K_b: 
                    
                    if self.hero_sprite.hp > 0 and self.hero_sprite.bomb_count > 0:
                        self.player.play_sound('use_bomb.wav')

                    score = self.hero_sprite.blowup(self.enemies_group)
                    self.hud_panel.show_bomb(self.hero_sprite.bomb_count)

                    if self.hud_panel.increase_score(score):

                        print('升级到 %d 级了，继续加油！'% self.hud_panel.level)
                        self.player.play_sound('upgrade.wav')
                        self.create_enemies()

                elif event.type == HERO_DEAD_EVENT:

                    self.hud_panel.lives_count -= 1
                    self.hud_panel.show_lives()
                    self.hud_panel.show_bomb(self.hero_sprite.bomb_count)

                elif event.type == HERO_POWER_OFF_EVENT:

                    self.hero_sprite.is_power = False
                    pygame.time.set_timer(HERO_POWER_OFF_EVENT, 0)

                elif event.type == HERO_FIRE_EVENT:
                    
                    self.player.play_sound('bullet.wav')
                    self.hero_sprite.fire(self.all_group)
                
                elif event.type == THROW_SUPPLY_EVENT:

                    self.player.play_sound('supply.wav')
                    supply = random.choice(self.supplies_group.sprites())
                    supply.throw_supply()

                elif event.type == BULLET_ENHANCED_OFF_EVENT:

                    self.hero_sprite.bullets_group = 0
                    pygame.time.set_timer(BULLET_ENHANCED_OFF_EVENT, 0)

        return False

    def create_enemies(self):

        count = len(self.enemies_group.sprites())
        groups = (self.all_group, self.enemies_group)

        if self.hud_panel.level == 1 and count == 0:

            for i in range(16):

                Enemy(0, 3, *groups)

        elif self.hud_panel.level == 2 and count == 16:

            for enemy in self.enemies_group.sprites():

                enemy.max_speed = 5

            for i in range(8):

                Enemy(0, 5, *groups)

            for i in range(2):

                Enemy(1, 1, *groups)

        elif self.hud_panel.level == 3 and count == 26:

            for enemy in self.enemies_group.sprites():

                enemy.max_speed = 7 if enemy.kind == 0 else 3

            for i in range(8):

                Enemy(0, 7, *groups)

            for i in range(2):

                Enemy(1, 3, *groups)

            for i in range (2):

                Enemy(2, 1, *groups)

    def check_collide(self):

        if not self.hero_sprite.is_power:
            
            collide_enemies = pygame.sprite.spritecollide(self.hero_sprite, self.enemies_group, False, pygame.sprite.collide_mask)

            collide_enemies =  list(filter(lambda  x: x.hp > 0, collide_enemies))

            if collide_enemies:

                self.hero_sprite.hp = IF_DEAD

                if IF_DEAD == 0:
                    self.player.play_sound(self.hero_sprite.wav_name)

            for enemy in collide_enemies:

                enemy.hp = 0

        try:

            hit_enemies = pygame.sprite.groupcollide(self.enemies_group, self.hero_sprite.bullets_group, False, False, pygame.sprite.collide_mask)

            for enemy in hit_enemies:

                if enemy.hp <= 0:
                    continue

                for bullet in hit_enemies[enemy]:

                    bullet.kill()
                    enemy.hp -= bullet.damage

                    if enemy.hp > 0:
                        continue

                    if self.hud_panel.increase_score(enemy.value):

                        print('升级到 %d 级了，继续加油！'% self.hud_panel.level)
                        self.player.play_sound('upgrade.wav')
                        self.create_enemies()

                    self.player.play_sound(enemy.wav_name)
                    break
        
        except (TypeError):

            pass
        
        supplies =  pygame.sprite.spritecollide(self.hero_sprite, self.supplies_group, False, pygame.sprite.collide_mask)

        if supplies:
            supply = supplies[0]
            self.player.play_sound(supply.wav_name)

            if supply.kind == 0:
                self.hero_sprite.bomb_count += 1
                self.hud_panel.show_bomb(self.hero_sprite.bomb_count)

            else:
                self.hero_sprite.bullets_kind = 1
                pygame.time.set_timer(BULLET_ENHANCED_OFF_EVENT, BULLET_SUPPLY_TIME)

            supply.rect.y = SCREEN_RECT.h

    def create_supply(self):

        Supply(0, self.all_group, self.supplies_group)
        Supply(1, self.all_group, self.supplies_group)

        pygame.time.set_timer(THROW_SUPPLY_EVENT, SUPPLY_TIME)


if __name__ == '__main__':

    pygame.init()

    Game().start()

    pygame.quit