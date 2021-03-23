import sys

import pygame

from ship import Ship

from Bullet import Bullet

from Alien import Alien

from time import sleep

from pygame.sprite import Group

from Button import Button

from scoreboard import Scoreboard

from game_stats import GameStats
def check_keyup_event(event,ship):
	if event.key == pygame.K_RIGHT:
		ship.moving_right = False
	elif event.key == pygame.K_LEFT:
		ship.moving_left = False

def check_keydown_event(event,ai_settings,screen,ship,bullets):
	if event.key == pygame.K_RIGHT:
		#向右移动飞船
		ship.moving_right = True
	elif event.key == pygame.K_LEFT:
		#向左移动飞船
		ship.moving_left = True
	elif event.key == pygame.K_SPACE:
		fire_bullet(bullets,ai_settings,screen,ship)
	elif event.key == pygame.K_q:
		sys.exit()

def check_events(ai_settings,screen,ship,bullets,play_button,stats,aliens,sb):
	"""监视键盘和鼠标事件"""
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		elif event.type == pygame.KEYDOWN:
			check_keydown_event(event,ai_settings,screen,ship,bullets)
		elif event.type == pygame.KEYUP:
			check_keyup_event(event,ship)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x,mouse_y = pygame.mouse.get_pos()
			check_play_button(stats,play_button,mouse_x,mouse_y,ai_settings,screen,bullets,aliens,sb,ship)


def check_play_button(stats,play_button,mouse_x,mouse_y,ai_settings,screen,bullets,aliens,sb,ship):
	button_clicked = play_button.rect.collidepoint(mouse_x,mouse_y)

	if button_clicked and not stats.game_active:

		ai_settings.initialize_dynamic_settings()
		pygame.mouse.set_visible(False)
		stats.reset_stats()
		stats.game_active = True
		
		sb.prep_score()
		sb.prep_high_score()
		sb.prep_level()

		aliens.empty()
		bullets.empty()	


		create_fleet(ai_settings, screen, aliens, ship)
		ship.center_ship()
def update_screen(ai_settings,screen,ship,bullets,aliens,play_button,stats,sb):
	#每次循环时都重绘屏幕
	screen.fill(ai_settings.bg_color)
	#在飞船和外星人后面重绘所有子弹
	for bullet in bullets.sprites():
		bullet.draw_bullet()
	ship.blitme()
	aliens.draw(screen)
	sb.show_score()
	if not stats.game_active:
		play_button.draw_button()

	#最近绘制的屏幕可见
	pygame.display.flip()


def check_bullet_alien_collisions(bullets,aliens,ai_settings,screen,ship,stats,sb):

	collisions = pygame.sprite.groupcollide(bullets,aliens,True,True)

	if collisions:
		for aliens in collisions.values():
			stats.score += ai_settings.alien_points*len(aliens)
			sb.prep_score()
		check_high_score(stats, sb)
	if len(aliens) == 0:

		bullets.empty()
		ai_settings.increase_speed()
		stats.level += 1
		sb.prep_level()
		sb.prep_ships()
		create_fleet(ai_settings, screen, aliens, ship)



def update_bullet(bullets,aliens,ai_settings,screen,ship,stats,sb):
	bullets.update()

	for bullet in bullets.copy():
		if bullet.rect.bottom <= 0:
			bullets.remove(bullet)

	check_bullet_alien_collisions(bullets, aliens, ai_settings, screen, ship,stats,sb)


def fire_bullet(bullets,ai_settings,screen,ship):
	if len(bullets) < ai_settings.bullet_allowed:
		#创建一颗子弹，并将其加入到编组bullets中
		new_bullet = Bullet(ai_settings,screen,ship)
		bullets.add(new_bullet)


def get_number_aliens_x(ai_settings,alien_width):
	
	available_space_x = ai_settings.screen_width - 2 * alien_width
	number_aliens_x = int(available_space_x/(2 * alien_width))
	
	return number_aliens_x

def create_alien(ai_settings,screen,aliens,alien_number,row_number):
	alien = Alien(ai_settings, screen)
	alien.x = alien.rect.width + 2 * alien.rect.width * alien_number
	alien.rect.x = alien.x
	alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
	aliens.add(alien)


def get_number_rows(ai_settings,ship_height,alien_height):
	
	available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
	number_rows = int(available_space_y/(2 * alien_height))

	return number_rows



def create_fleet(ai_settings,screen,aliens,ship):
	"""创建aliens群"""
	#创建一个外星人，并计算一行可容纳多少
	#外星人间距为外星人宽度
	alien = Alien(ai_settings, screen)
	alien_width = alien.rect.width
	number_aliens_x = get_number_aliens_x(ai_settings, alien_width)
	number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)

	#创建外星人群
	for row_number in range(number_rows):
		for alien_number in range(number_aliens_x):
			create_alien(ai_settings,screen,aliens,alien_number,row_number)


def check_fleet_edges(ai_settings,aliens):
	"""有外星人达到边缘时采取相应的措施"""
	for alien in aliens.sprites():
		if alien.check_edge():
			change_fleet_direction(ai_settings,aliens)
			break


def change_fleet_direction(ai_settings,aliens):
	"""将整群外星人下移，并改变他们的方向"""
	for alien in aliens.sprites():
		alien.rect.y += ai_settings.fleet_drop_speed
	
	ai_settings.fleet_direction *= -1


def ship_hit(ai_settings,stats,screen,ship,aliens,bullets,sb):
	"""响应被外星人撞到的飞船"""
	if stats.ships_left > 0:
		# 将ship_left减1
		stats.ships_left -= 1

		sb.prep_ships()

		#清空外星人列表和子弹列表
		aliens.empty()
		bullets.empty()

		# 创建一群新的外星人，并将飞船放到屏幕底端中央
		create_fleet(ai_settings, screen, aliens, ship)
		ship.center_ship()

		#暂停
		sleep(0.5)

	else:
		stats.game_active = False
		pygame.mouse.set_visible(True)


def update_aliens(aliens,ai_settings,ship,stats,screen,bullets,sb):
	check_fleet_edges(ai_settings, aliens)
	aliens.update()

	#检测外星人和飞船的碰撞
	if pygame.sprite.spritecollideany(ship,aliens):
		ship_hit(ai_settings,stats,screen,ship,aliens,bullets,sb)

	check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets,sb)


def check_aliens_bottom(ai_settings,stats,screen,ship,aliens,bullets,sb):
	"""检查是否有外星人到达了屏幕底端"""
	screen_rect = screen.get_rect()
	for alien in aliens.sprites():
		if alien.rect.bottom >= screen_rect.bottom:
			#像飞船被撞到一样处理
			ship_hit(ai_settings, stats, screen, ship, aliens, bullets,sb)
			break


def check_high_score(stats,sb):
	if stats.score > stats.high_score:
		stats.high_score = stats.score
		sb.prep_high_score()


