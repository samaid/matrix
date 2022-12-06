from settings import *
import numpy as np
import random

green_symbols = np.empty(shape=KATAKANA_ALPHABET_SIZE, dtype=np.int32)
light_green_symbols = np.empty(shape=KATAKANA_ALPHABET_SIZE, dtype=np.int32)
dark_green_symbols = np.empty(shape=KATAKANA_ALPHABET_SIZE, dtype=np.int32)
very_light_green_symbols = np.empty(shape=KATAKANA_ALPHABET_SIZE, dtype=np.int32)
the_matrix_symbols = np.empty(shape=8, dtype=np.int32)


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

    def draw_stream_but_last_symbol(self, surface):
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
        return y

    def draw(self, surface):
        y = self.draw_stream_but_last_symbol(surface)
        # Symbol at the very bottom always remains very light green
        smb = very_light_green_symbols[self.symbols[self.n_symbols-1]]
        surface.blit(smb, (self.pos_x, y))

    def update(self):
        # Age every symbol until it is old
        self.symbol_ages = np.where(self.symbol_ages > SYMBOL_AGE_OLD, self.symbol_ages-1, SYMBOL_AGE_OLD)

        # Renew symbol if it is old
        self.symbols = np.where(self.symbol_ages == SYMBOL_AGE_OLD, random_symbol(self.n_symbols), self.symbols)
        self.symbol_ages = np.where(self.symbol_ages == SYMBOL_AGE_OLD, random_age(self.n_symbols), self.symbol_ages)


class TheMatrixStream(SymbolStream):
    def __init__(self, pos_x, max_size, symbol):
        self.symbol = symbol
        super().__init__(pos_x, max_size)

    def draw_stream_but_last_symbol(self, surface):
        y = self.pos_y
        for i in range(self.n_symbols - 1):
            if y >= (DISPLAY_H-FONT_SIZE)//2:
                break

            age = self.symbol_ages[i]

            if age >= SYMBOL_AGE_YONG:
                smb = light_green_symbols[self.symbols[i]]
            elif age >= SYMBOL_AGE_MATURE:
                smb = green_symbols[self.symbols[i]]
            else:
                smb = dark_green_symbols[self.symbols[i]]

            surface.blit(smb, (self.pos_x, y))
            y += FONT_SIZE

        return y

    def draw(self, surface):
        y = self.draw_stream_but_last_symbol(surface)
        # Symbol at the very bottom always remains very light green
        smb = the_matrix_symbols[self.symbol]

        # The Matrix symbols displayed in the middle
        y = min((DISPLAY_H-FONT_SIZE)//2, y)

        surface.blit(smb, (self.pos_x, y))

    def update(self):
        super().update()
        self.pos_y += 10


class SymbolStreams:
    def __init__(self):
        self.age = 0
        self.streams = []
        self.speeds = np.random.randint(MIN_STREAM_SPEED, MAX_STREAM_SPEED, N_STREAMS)
        for i in range(N_STREAMS):
            self.streams.append([])

    def can_spawn(self, idx):
        can = True

        # For final seconds of intro we do not allow new streams at positions of THE MATRIX symbols
        if self.age >= STREAM_AGE_DECAY*2:
            idx_left = N_STREAMS//2 - 10
            if idx_left <= idx <= idx_left+5 or idx_left+9 <= idx <= idx_left+20:
                can = False
        else:
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
    global green_symbols, light_green_symbols, dark_green_symbols, very_light_green_symbols, the_matrix_symbols

    ds, clk, green_symbols, light_green_symbols, dark_green_symbols, very_light_green_symbols, the_matrix_symbols = initialize()
    transparent = pg.Surface(DISPLAY_RES)

    alpha = ALPHA_CHANNEL
    transparent.set_alpha(alpha)

    streams = SymbolStreams()

    x = DISPLAY_W//2 - 10*STREAM_WIDTH
    t_stream = TheMatrixStream(x, 20, 0)
    x += 2*STREAM_WIDTH
    h_stream = TheMatrixStream(x, 20, 1)
    x += 2*STREAM_WIDTH
    e_stream = TheMatrixStream(x, 20, 2)
    x += 4*STREAM_WIDTH
    m_stream = TheMatrixStream(x, 20, 3)
    x += 2*STREAM_WIDTH
    a_stream = TheMatrixStream(x, 20, 4)
    x += 2*STREAM_WIDTH
    t2_stream = TheMatrixStream(x, 20, 0)
    x += 2*STREAM_WIDTH
    r_stream = TheMatrixStream(x, 20, 5)
    x += 2*STREAM_WIDTH
    i_stream = TheMatrixStream(x, 20, 6)
    x += 2*STREAM_WIDTH
    x_stream = TheMatrixStream(x, 20, 7)

    do_game = True
    while do_game:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                do_game = False

        # Draw objects
        transparent.fill(pg.Color('black'))
        streams.draw(transparent)

        if streams.age >= STREAM_AGE_DECAY*2:
            t_stream.draw(transparent)
            h_stream.draw(transparent)
            e_stream.draw(transparent)
            m_stream.draw(transparent)
            a_stream.draw(transparent)
            t2_stream.draw(transparent)
            r_stream.draw(transparent)
            i_stream.draw(transparent)
            x_stream.draw(transparent)

        ds.blit(transparent, (0, 0))

        # Perform updates
        streams.update()

        if streams.age >= STREAM_AGE_DECAY * 2:
            t_stream.update()

        if streams.age >= STREAM_AGE_DECAY * 2 + 50:
            r_stream.update()

        if streams.age >= STREAM_AGE_DECAY * 2 + 150:
            m_stream.update()

        if streams.age >= STREAM_AGE_DECAY * 2 + 250:
            a_stream.update()

        if streams.age >= STREAM_AGE_DECAY * 2 + 300:
            h_stream.update()

        if streams.age >= STREAM_AGE_DECAY * 2 + 350:
            i_stream.update()

        if streams.age >= STREAM_AGE_DECAY * 2 + 380:
            e_stream.update()

        if streams.age >= STREAM_AGE_DECAY * 2 + 420:
            x_stream.update()

        if streams.age >= STREAM_AGE_DECAY * 2 + 460:
            t2_stream.update()

        if streams.age >= STREAM_AGE_DECAY * 2 + 600:
            alpha -= 1
            alpha = max(0, alpha)
            transparent.set_alpha(alpha)

        # Prepare for next frame
        pg.display.flip()
        clk.tick(FPS)


if __name__ == "__main__":
    main()
