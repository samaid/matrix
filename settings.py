import os
import pygame as pg

# The Matrix uses Japanese alphabet which is encoded in the following list
KATAKANA_ALPHABET_SIZE = 96
KATAKANA_ALPHABET_START = int('0x30a0', 16)
KATAKANA_ALPHABET = [chr(KATAKANA_ALPHABET_START + i) for i in range(KATAKANA_ALPHABET_SIZE)]

DISPLAY_RES = DISPLAY_W, DISPLAY_H = 1600, 900
FONT_SIZE = 25
FPS = 60
ALPHA_CHANNEL = 150

SYMBOL_AGE_OLD = 0
SYMBOL_AGE_MATURE = 50
SYMBOL_AGE_YONG = 100
SYMBOL_AGE_MAX = 200
SYMBOL_AGE_IMMORTAL = 2000000

STREAM_WIDTH = 25
N_STREAMS = DISPLAY_W // STREAM_WIDTH
MIN_STREAM_SPEED = 5
MAX_STREAM_SPEED = 10
STREAM_AGE_GROWTH = 500
STREAM_AGE_DECAY = 500
SPAWN_PROBABILITY_YOUNG = 0.05
SPAWN_PROBABILITY_DECAY = 0.1


def set_display():
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    pg.init()
    surface = pg.display.set_mode(DISPLAY_RES)
    clock = pg.time.Clock()

    return surface, clock


def set_font():
    f = pg.font.Font("MSMINCHO.TTF", FONT_SIZE)
    f.bold = True
    green_symbols = [f.render(char, True, pg.Color(50, 128, 50)) for char in KATAKANA_ALPHABET]
    light_green_symbols = [f.render(char, True, pg.Color(60, 196, 60)) for char in KATAKANA_ALPHABET]
    dark_green_symbols = [f.render(char, True, pg.Color(0, 128, 0)) for char in KATAKANA_ALPHABET]
    very_light_green_symbols = [f.render(char, True, pg.Color(150, 255, 150)) for char in KATAKANA_ALPHABET]

    return green_symbols, light_green_symbols, dark_green_symbols, very_light_green_symbols


def initialize():
    surface, clock = set_display()
    green_symbols, light_green_symbols, dark_green_symbols, very_light_green_symbols = set_font()
    return surface, clock, green_symbols, light_green_symbols, dark_green_symbols, very_light_green_symbols
