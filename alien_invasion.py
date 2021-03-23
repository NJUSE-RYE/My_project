from settings import Settings

from ship import Ship

import game_functions as gf

import pygame

from pygame.sprite import Group

from Alien import Alien

from game_stats import GameStats

from Button import Button

from scoreboard import Scoreboard
def run_game():
	#初始化游戏、设置和屏幕对象
	pygame.init()
	ai_settings = Settings()
	screen = pygame.display.set_mode((ai_settings.screen_width,ai_settings.screen_height))
	pygame.display.set_caption("Alien Invasion")

	play_button = Button(ai_settings,screen,"Play")

	#创建一艘飞船
	ship = Ship(screen,ai_settings)
	#创建用于存储子弹的编组
	bullets  = Group()
	#创建aliens编组
	aliens = Group()
	#创建Ailens群
	gf.create_fleet(ai_settings,screen,aliens,ship)
	#创建Game Stats实例
	stats = GameStats(ai_settings)
	sb = Scoreboard(ai_settings,screen,stats)
	#开始游戏的主循环
	while True:

		#监听键盘和鼠标事件
		gf.check_events(ai_settings,screen,ship,bullets,play_button,stats,aliens,sb)
		if stats.game_active:
			ship.update()
			gf.update_bullet(bullets,aliens,ai_settings,screen,ship, stats, sb)
			gf.update_aliens(aliens,ai_settings,ship,stats,screen,bullets,sb)
		#更新屏幕
		gf.update_screen(ai_settings,screen,ship,bullets,aliens,play_button,stats,sb)


run_game()