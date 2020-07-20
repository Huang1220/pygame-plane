import pygame
import random

from game_date import *

SET_GAME_NAME = 'pygame飞机大战'

SCREEN_RECT = pygame.Rect(0, 0, 480, 700)
FRAME_INTERVAL = 10

HERO_BOMB_COUNT = BOMB_COUNT
HERO_DEFAULT_MID_BOTTOM = (SCREEN_RECT.centerx, SCREEN_RECT.bottom - 90)

HERO_DEAD_EVENT = pygame.USEREVENT
HERO_POWER_OFF_EVENT = pygame.USEREVENT + 1
HERO_FIRE_EVENT = pygame.USEREVENT + 2
THROW_SUPPLY_EVENT = pygame.USEREVENT + 3
BULLET_ENHANCED_OFF_EVENT = pygame.USEREVENT + 4

class GameSprite(pygame.sprite.Sprite):

    res_path = './res/images/'


    def __init__(self, image_name, speed, *group):

        super(GameSprite, self).__init__(*group)

        self.image = pygame.image.load(self.res_path + image_name)

        self.rect = self.image.get_rect()

        self.speed = speed

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args):

        self.rect.y += self.speed


class Background(GameSprite):

    def __init__(self, is_alt, *group):
        
        super(Background, self).__init__('background.png', 1, *group)

        if is_alt:
            self.rect.y = - self.rect.h

    def update(self, *args):

        super(Background, self).update(*args)

        if self.rect.y > self.rect.h:
            self.rect.y = -self.rect.h

class StatusButton(GameSprite):

    def __init__(self, image_names, *groups):

        super(StatusButton, self).__init__(image_names[0], 0, *groups)

        self.images = [pygame.image.load(self.res_path + name) for name in image_names]

    def swich_status(self, is_pause):

        self.image = self.images[1 if is_pause else 0]


class Label(pygame.sprite.Sprite):

    font_path = './res/font/MarkerFelt.ttc'

    def __init__(self, text, size, color, *groups):

        super(Label, self).__init__(*groups)

        self.font = pygame.font.Font(self.font_path, size)

        self.color = color

        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect()

    def set_text(self, text):

        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect()

class Plane(GameSprite):

    def __init__(self, normal_names, speed, hp, value, wav_name, hurt_name, destroy_names, *groups):

        super(Plane, self).__init__(normal_names[0], speed, *groups)

        self.hp = hp
        self.max_hp = hp
        self.value = value
        self.wav_name = wav_name

        self.normal_images = [pygame.image.load(self.res_path + name) for name in normal_names]
        self.normal_index = 0
        self.hurt_image = pygame.image.load(self.res_path + hurt_name)
        self.destroy_images = [pygame.image.load(self.res_path + name) for name in destroy_names]
        self.destroy_index = 0

    def reset_plane(self):

        self.hp = self.max_hp

        self.normal_index = 0
        self.destroy_index = 0

        self.image = self.normal_images[0]


    def update(self, *args):

        if not args[0]:
            return

        if self.hp == self.max_hp:

            self.image = self.normal_images[self.normal_index]

            count = len(self.normal_images)
            self.normal_index = (self.normal_index + 1) % count
        
        elif self.hp > 0:

            self.image = self.hurt_image

        else:

            if self.destroy_index < len(self.destroy_images):
                self.image = self.destroy_images[self.destroy_index]

                self.destroy_index += 1

            else:
                self.reset_plane()

class Enemy(Plane):

    def __init__(self, kind, max_speed, *groups):

        self.kind = kind
        self.max_speed = max_speed

        if kind == 0:
                
            super(Enemy, self).__init__(
                ['enemy1.png'], 1, 1, 1000, 'enemy1_down.wav', 'enemy1.png',
                ['enemy1_down%d.png' %i for i in range(1,5)], *groups)

        elif kind == 1:

            super(Enemy, self).__init__(
                ['enemy2.png'], 1, 6, 6000, 'enemy2_down.wav', 'enemy2_hit.png',
                ['enemy2_down%d.png' %i for i in range(1,5)], *groups)

        elif kind == 2:

            super(Enemy, self).__init__(
                ['enemy3_n1.png', 'enemy3_n2.png'], 1, 15, 15000, 'enemy3_down.wav', 'enemy3_hit.png',
                ['enemy3_down%d.png' %i for i in range(1,7)], *groups)

        self.reset_plane()

    def reset_plane(self):

        super(Enemy, self).reset_plane()

        x = random.randint(0, SCREEN_RECT.w - self.rect.w)
        y = random.randint(0, SCREEN_RECT.h - self.rect.h) - SCREEN_RECT.h

        self.rect.topleft = (x, y)

        self.speed = random.randint(1, self.max_speed)

    def update(self, *args):

        super(Enemy, self).update(*args)

        if self.hp > 0:
            self.rect.y += self.speed

        if self.rect.y >= SCREEN_RECT.h:
            self.reset_plane()

class Hero(Plane):

    def __init__(self, *groups):
        self.is_power = False
        self.bomb_count = HERO_BOMB_COUNT
        self.bullets_kind = 0
        self.bullets_group = pygame.sprite.Group()

        super(Hero, self).__init__(('me1.png', 'me2.png'), 5, 1, 0,'me_down.wav', 'me1.png', 
                                   ['me_destroy_%d.png'%x for x in range(1,5)], *groups)

        self.rect.midbottom = HERO_DEFAULT_MID_BOTTOM

        pygame.time.set_timer(HERO_FIRE_EVENT, 200)
    
    def update(self, *args):

        super(Hero, self).update(*args)

        if len(args) != 3 or self.hp <= 0:
            return

        self.rect.x += args[1] * self.speed

        self.rect.x =  0 if self.rect.x < 0 else self.rect.x
        self.rect.right = SCREEN_RECT.right if self.rect.right > SCREEN_RECT.right else self.rect.right

        self.rect.y += args[2] * self.speed
        self.rect.y =  0 if self.rect.y < 0 else self.rect.y
        self.rect.bottom = SCREEN_RECT.bottom if self.rect.bottom > SCREEN_RECT.bottom else self.rect.bottom

    def blowup(self, enemies_group):

        if self.bomb_count <= 0 or self.hp <= 0:
            return 0

        self.bomb_count -= 1
        score = 0
        count = 0

        for enemy in enemies_group.sprites():

            if enemy.rect.bottom > 0:

                score += enemy.value
                enemy.hp = 0
                count += 1

        return score

    def reset_plane(self):

        super(Hero, self).reset_plane()

        self.is_power = True
        self.bomb_count = HERO_BOMB_COUNT
        self.bullets_kind = 0

        pygame.event.post(pygame.event.Event(HERO_DEAD_EVENT))

        pygame.time.set_timer(HERO_POWER_OFF_EVENT, 3000)

    def fire(self, display_group):

        groups = (display_group, self.bullets_group)

        for i in range(3):

            bullet1 = Bullet(self.bullets_kind, *groups)
            y = self.rect.y - i * 15

            if self.bullets_kind == 0:

                bullet1.rect.midbottom = (self.rect.centerx, y)

            else:

                bullet1.rect.midbottom = (self.rect.centerx - 15, y)

                bullet2 = Bullet(self.bullets_kind, *groups)

                bullet2.rect.midbottom = (self.rect.centerx, y)

                bullet3 = Bullet(self.bullets_kind, *groups)

                bullet3.rect.midbottom = (self.rect.centerx + 15, y)


class Bullet(GameSprite):

    def __init__(self, kind, *group):

        image_name = 'bullet1.png' if kind == 0 else 'bullet2.png'

        super(Bullet, self).__init__(image_name, -12, *group)

        self.damage = 1
    
    def update(self, *args):

        super(Bullet, self).update(*args)

        if self.rect.bottom < 0:

            self.kill()

class Supply(GameSprite):

    def __init__(self, kind, *group):

        image_name = 'bomb_supply.png' if kind == 0 else 'bullet_supply.png'
        super(Supply, self).__init__(image_name, 5, *group)

        self.kind = kind
        self.wav_name = 'get_bomb.wav' if kind == 0 else 'get_bullet.wav'

        self.rect.bottom = SCREEN_RECT.h
    
    def update(self, *args):

        if self.rect.y > SCREEN_RECT.h:
            return

        super(Supply, self).update(*args)

    def throw_supply(self):

        self.rect.bottom = 0
        self.rect.x = random.randint(0, SCREEN_RECT.w - self.rect.w)





