from settings import *
import numpy as np
import random

green_symbols = np.empty(shape=KATAKANA_ALPHABET_SIZE, dtype=np.int32)
light_green_symbols = np.empty(shape=KATAKANA_ALPHABET_SIZE, dtype=np.int32)
dark_green_symbols = np.empty(shape=KATAKANA_ALPHABET_SIZE, dtype=np.int32)
very_light_green_symbols = np.empty(shape=KATAKANA_ALPHABET_SIZE, dtype=np.int32)


def random_age(n):
    return np.random.randint(0, SYMBOL_AGE_MAX, n)


def random_symbol(n):
    return np.random.randint(0, KATAKANA_ALPHABET_SIZE, n)


class SymbolStream:
    def __init__(self, pos_x, max_size):
        self.n_symbols = random.randint(1, max_size+1)  # Stream size is random
        self.symbols = random_symbol(self.n_symbols)
        self.symbol_ages = random_age(self.n_symbols)
        self.symbol_ages[-1] = SYMBOL_AGE_IMMORTAL
        self.pos_x = pos_x  # Horizontal position is fixed for each stream
        self.pos_y = -FONT_SIZE*self.n_symbols  # Vertical initial position is at the top of the screen

    def draw(self, surface):
        y = self.pos_y
        for i in range(self.n_symbols - 1):
            age = self.symbol_ages[i]

            if age >= SYMBOL_AGE_YONG:
                smb = light_green_symbols[self.symbols[i]]
            elif age >= SYMBOL_AGE_MATURE:
                smb = green_symbols[self.symbols[i]]
            else:
                smb = dark_green_symbols[self.symbols[i]]

            surface.blit(smb, (self.pos_x, y))
            y += FONT_SIZE

        # Symbol at the very bottom always remains very light green
        smb = very_light_green_symbols[self.symbols[self.n_symbols-1]]
        surface.blit(smb, (self.pos_x, y))

    def update(self):
        # Age every symbol until it is old
        self.symbol_ages = np.where(self.symbol_ages > SYMBOL_AGE_OLD, self.symbol_ages-1, SYMBOL_AGE_OLD)

        # Renew symbol if it is old
        self.symbols = np.where(self.symbol_ages == SYMBOL_AGE_OLD, random_symbol(self.n_symbols), self.symbols)
        self.symbol_ages = np.where(self.symbol_ages == SYMBOL_AGE_OLD, random_age(self.n_symbols), self.symbol_ages)


class SymbolStreams:
    def __init__(self):
        self.age = 0
        self.streams = []
        self.speeds = np.random.randint(MIN_STREAM_SPEED, MAX_STREAM_SPEED, N_STREAMS)
        for i in range(N_STREAMS):
            self.streams.append([])

    def can_spawn(self, idx):
        can = True
        for stream in self.streams[idx]:
            if stream.pos_y < FONT_SIZE:
                can = False

        return can

    def remove_fallen(self):
        for i in range(N_STREAMS):
            for stream in self.streams[i]:
                if stream.pos_y > DISPLAY_H:
                    self.streams[i].remove(stream)

    def get_max_stream_size(self):
        if self.age <= STREAM_AGE_GROWTH:
            return int(self.age/10+1)
        else:
             return int(STREAM_AGE_GROWTH/10)

    def get_spawn_probability(self):
        if self.age <= STREAM_AGE_DECAY:
            return SPAWN_PROBABILITY_YOUNG
        else:
            return 1.0/(self.age-STREAM_AGE_DECAY)

    def spawn_streams(self):
        pr = self.get_spawn_probability()
        max_size = self.get_max_stream_size()

        x = 0
        for i in range(N_STREAMS):
            if self.can_spawn(i):
                if random.random() <= pr:
                    self.streams[i].append(SymbolStream(x, max_size))
            x += STREAM_WIDTH

    def draw(self, surface):
        x = 0
        for i in range(N_STREAMS):
            for stream in self.streams[i]:
                stream.draw(surface)
            x += STREAM_WIDTH

    def update_streams(self):
        for i in range(N_STREAMS):
            for stream in self.streams[i]:
                stream.pos_y += self.speeds[i]
                stream.update()

    def update(self):
        self.age += 1
        self.remove_fallen()
        self.update_streams()
        self.spawn_streams()


def main():
    global green_symbols, light_green_symbols, dark_green_symbols, very_light_green_symbols

    ds, clk, green_symbols, light_green_symbols, dark_green_symbols, very_light_green_symbols = initialize()
    transparent = pg.Surface(DISPLAY_RES)
    transparent.set_alpha(ALPHA_CHANNEL)

    streams = SymbolStreams()

    do_game = True
    while do_game:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                do_game = False

        # Draw objects
        transparent.fill(pg.Color('black'))
        streams.draw(transparent)

        ds.blit(transparent, (0, 0))

        # Perform updates
        streams.update()

        # Prepare for next frame
        pg.display.flip()
        clk.tick(FPS)


if __name__ == "__main__":
    main()
