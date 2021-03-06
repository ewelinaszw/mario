# -*- coding: utf-8 -*-

from psychopy import visual, event, core
import multiprocessing as mp
import pygame as pg
import pandas as pd
import filterlib as flt
import blink as blk
from pyOpenBCI import OpenBCIGanglion


def blinks_detector(quit_program, blink_det, blinks_num, blink,):
	def detect_blinks(sample):
		if SYMULACJA_SYGNALU:
			smp_flted = sample
		else:
			smp = sample.channels_data[0]
			smp_flted = frt.filterIIR(smp, 0)
		#print(smp_flted)

		brt.blink_detect(smp_flted, -38000)
		if brt.new_blink:
			if brt.blinks_num == 1:
				#connected.set()
				print('CONNECTED. Speller starts detecting blinks.')
			else:
				blink_det.put(brt.blinks_num)
				blinks_num.value = brt.blinks_num
				blink.value = 1

		if quit_program.is_set():
			if not SYMULACJA_SYGNALU:
				print('Disconnect signal sent...')
				board.stop_stream()


####################################################
	SYMULACJA_SYGNALU = False
####################################################
	mac_adress = 'f0:a6:74:94:b3:4d'
####################################################

	clock = pg.time.Clock()
	frt = flt.FltRealTime()
	brt = blk.BlinkRealTime()

	if SYMULACJA_SYGNALU:
		df = pd.read_csv('dane_do_symulacji/data.csv')
		for sample in df['signal']:
			if quit_program.is_set():
				break
			detect_blinks(sample)
			clock.tick(200)
		print('KONIEC SYGNAŁU')
		quit_program.set()
	else:
		board = OpenBCIGanglion(mac=mac_adress)
		board.start_stream(detect_blinks)

if __name__ == "__main__":


	blink_det = mp.Queue()
	blink = mp.Value('i', 0)
	blinks_num = mp.Value('i', 0)
	#connected = mp.Event()
	quit_program = mp.Event()

	proc_blink_det = mp.Process(
		name='proc_',
		target=blinks_detector,
		args=(quit_program, blink_det, blinks_num, blink,)
		)

	# rozpoczęcie podprocesu
	proc_blink_det.start()
	print('subprocess started')

	############################################
	# Poniżej należy dodać rozwinięcie programu
	############################################

	pg.init()
	WINDOW_WIDTH = 1200
	WINDOW_HEIGHT = 600
	FPS = 20
	BLACK = (0, 0, 0)
	GREEN = (0, 255, 0)
	ADD_NEW_FLAME_RATE = 25
	cactus_img = pg.image.load('cactus_bricks.png')
	cactus_img_rect = cactus_img.get_rect()
	cactus_img_rect.left = 0
	fire_img = pg.image.load('fire_bricks.png')
	fire_img_rect = fire_img.get_rect()
	fire_img_rect.left = 0
	CLOCK = pg.time.Clock()
	font = pg.font.SysFont('forte', 20)

	canvas = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
	pg.display.set_caption('Mario')


	class Topscore:
		def __init__(self):
			self.high_score = 0
		def top_score(self, score):
			if score > self.high_score:
				self.high_score = score
			return self.high_score

	topscore = Topscore()


	class Dragon:
		dragon_velocity = 10

		def __init__(self):
			self.dragon_img = pg.image.load('dragon.png')
			self.dragon_img_rect = self.dragon_img.get_rect()
			self.dragon_img_rect.width -= 10
			self.dragon_img_rect.height -= 10
			self.dragon_img_rect.top = WINDOW_HEIGHT/2
			self.dragon_img_rect.right = WINDOW_WIDTH
			self.up = True
			self.down = False

		def update(self):
			canvas.blit(self.dragon_img, self.dragon_img_rect)
			if self.dragon_img_rect.top <= cactus_img_rect.bottom:
				self.up = False
				self.down = True
			elif self.dragon_img_rect.bottom >= fire_img_rect.top:
				self.up = True
				self.down = False

			if self.up:
				self.dragon_img_rect.top -= self.dragon_velocity
			elif self.down:
				self.dragon_img_rect.top += self.dragon_velocity


	class Flames:
		flames_velocity = 20

		def __init__(self):
			self.flames = pg.image.load('fireball.png')
			self.flames_img = pg.transform.scale(self.flames, (20, 20))
			self.flames_img_rect = self.flames_img.get_rect()
			self.flames_img_rect.right = dragon.dragon_img_rect.left
			self.flames_img_rect.top = dragon.dragon_img_rect.top + 30


		def update(self):
			canvas.blit(self.flames_img, self.flames_img_rect)

			if self.flames_img_rect.left > 0:
				self.flames_img_rect.left -= self.flames_velocity


	class Mario:
		velocity = 10

		def __init__(self):
			self.mario_img = pg.image.load('maryo.png')
			self.mario_img_rect = self.mario_img.get_rect()
			self.mario_img_rect.left = 20
			self.mario_img_rect.top = WINDOW_HEIGHT/2 - 100
			self.down = True
			self.up = False

		def update(self):
			canvas.blit(self.mario_img, self.mario_img_rect)
			if self.mario_img_rect.top <= cactus_img_rect.bottom:
				game_over()
				if SCORE > self.mario_score:
					self.mario_score = SCORE
			if self.mario_img_rect.bottom >= fire_img_rect.top:
				game_over()
				if SCORE > self.mario_score:
					self.mario_score = SCORE
			if self.up:
				self.mario_img_rect.top -= 70
			if self.down:
				self.mario_img_rect.bottom += 5


	def game_over():
		pg.mixer.music.stop()
		music = pg.mixer.Sound('mario_dies.wav')
		music.play()
		topscore.top_score(SCORE)
		game_over_img = pg.image.load('end.png')
		game_over_img_rect = game_over_img.get_rect()
		game_over_img_rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
		canvas.blit(game_over_img, game_over_img_rect)
		while True:
			for event in pg.event.get():
				if event.type == pg.QUIT:
					pg.quit()
					sys.exit()
				if event.type == pg.KEYDOWN:
					if event.key == pg.K_ESCAPE:
						pg.quit()
						sys.exit()
					music.stop()
					game_loop()
			pg.display.update()


	def start_game():
		canvas.fill(BLACK)
		start_img = pg.image.load('start.png')
		start_img_rect = start_img.get_rect()
		start_img_rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
		canvas.blit(start_img, start_img_rect)
		while True:
			for event in pg.event.get():
				if event.type == pg.QUIT:
					pg.quit()
					sys.exit()
				if event.type == pg.KEYDOWN:
					if event.key == pg.K_ESCAPE:
						pg.quit()
						sys.exit()
					game_loop()
			pg.display.update()


	def check_level(SCORE):
		global LEVEL
		if SCORE in range(0, 10):
			cactus_img_rect.bottom = 50
			fire_img_rect.top = WINDOW_HEIGHT - 50
			LEVEL = 1
		elif SCORE in range(10, 20):
			cactus_img_rect.bottom = 100
			fire_img_rect.top = WINDOW_HEIGHT - 100
			LEVEL = 2
		elif SCORE in range(20, 30):
			cactus_img_rect.bottom = 150
			fire_img_rect.top = WINDOW_HEIGHT - 150
			LEVEL = 3
		elif SCORE > 30:
			cactus_img_rect.bottom = 200
			fire_img_rect.top = WINDOW_HEIGHT - 200
			LEVEL = 4





	def game_loop():
		while True:
			global dragon
			dragon = Dragon()
			flames = Flames()
			mario = Mario()
			add_new_flame_counter = 0
			global SCORE
			SCORE = 0
			global  HIGH_SCORE
			flames_list = []
			pg.mixer.music.load('mario_theme.wav')
			pg.mixer.music.play(-1, 0.0)
			while True:
				canvas.fill(BLACK)
				check_level(SCORE)
				dragon.update()
				add_new_flame_counter += 1

				if add_new_flame_counter == ADD_NEW_FLAME_RATE:
					add_new_flame_counter = 0
					new_flame = Flames()
					flames_list.append(new_flame)
				for f in flames_list:
					if f.flames_img_rect.left <= 0:
						flames_list.remove(f)
						SCORE += 1
					f.update()

				for event in pg.event.get():
					if event.type == pg.QUIT:
						pg.quit()
						sys.exit()
					if event.type == pg.KEYDOWN:
						if event.key == pg.K_UP:
							mario.up = True
							mario.down = False
						elif event.key == pg.K_DOWN:
							mario.down = True
							mario.up = False
					if event.type == pg.KEYUP:
						if blink.value == 1:
							mario.up = False
							mario.down = True
						elif event.key == pg.K_DOWN:
							mario.down = True
							mario.up = False


				if blink.value==1:
					print('blink')
					mario.up = True
					mario.down = False
					blink.value=0
				else:
					mario.down = True
					mario.up = False

				score_font = font.render('Score:'+str(SCORE), True, GREEN)
				score_font_rect = score_font.get_rect()
				score_font_rect.center = (200, cactus_img_rect.bottom + score_font_rect.height/2)
				canvas.blit(score_font, score_font_rect)

				level_font = font.render('Level:'+str(LEVEL), True, GREEN)
				level_font_rect = level_font.get_rect()
				level_font_rect.center = (500, cactus_img_rect.bottom + score_font_rect.height/2)
				canvas.blit(level_font, level_font_rect)

				top_score_font = font.render('Top Score:'+str(topscore.high_score),True,GREEN)
				top_score_font_rect = top_score_font.get_rect()
				top_score_font_rect.center = (800, cactus_img_rect.bottom + score_font_rect.height/2)
				canvas.blit(top_score_font, top_score_font_rect)

				canvas.blit(cactus_img, cactus_img_rect)
				canvas.blit(fire_img, fire_img_rect)
				mario.update()
				for f in flames_list:
					if f.flames_img_rect.colliderect(mario.mario_img_rect):
						game_over()
						if SCORE > mario.mario_score:
							mario.mario_score = SCORE
				pg.display.update()
				CLOCK.tick(FPS)


	start_game()

# Zakończenie podprocesów
	proc_blink_det.join()
