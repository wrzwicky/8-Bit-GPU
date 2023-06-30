import pygame, sys, math
from pygame.locals import QUIT

# Can we render a textured polygons using only a big stack
# of linear DDAs?
# https://en.wikipedia.org/wiki/Digital_differential_analyzer_(graphics_algorithm)


class DDA:

    def __init__(self, w, n, d):
        """start number: whole part, numer, denom"""
        self.w = w
        self.n = n
        self.d = d

    def add(self, inc):
        """add inc/denom, return w"""
        self.n += inc
        if self.n >= self.d:
            self.w += 1
            self.n -= self.d
        elif self.n < 0:
            self.w -= 1
            self.n += self.d
        return self.w


class Tracker:

    def __init__(self):
        self.incr = 0
        self.dda = None

    def step(self):
        return self.dda.add(self.incr)

    @classmethod
    def make(cls, ref_start, ref_end, target_start, target_end):
        numer = target_end - target_start
        denom = ref_end - ref_start
        t = Tracker()
        t.incr = numer
        t.dda = DDA(target_start, denom / 2, denom)
        return t

class TrackXY:
    @classmethod
    def make(cls, ref_start, ref_end,
             x_start, x_end, y_start, y_end):
        t = TrackXY()
               
        numer = x_end - x_start
        denom = ref_end - ref_start
        t.xincr = numer
        t.xdda = DDA(x_start, denom / 2, denom)

        numer = y_end - y_start
        denom = ref_end - ref_start
        t.yincr = numer
        t.ydda = DDA(y_start, denom / 2, denom)
               
        return t
               
    def step(self):
        self.xdda.add(self.xincr)
        self.ydda.add(self.yincr)
      
    def coord(self):
      return (self.xdda.w, self.ydda.w)


def draw_source(x, y, w, h):
    c1 = (0, 255, 0)
    c2 = (0, 0, 255)
    for i in range(0, int(min(w / 2, h / 2)), 2):
        pygame.draw.rect(screen, c1,
                         (x + i, y + i, int(w - i * 2), int(h - i * 2)), 1)
        i += 1
        pygame.draw.rect(screen, c2,
                         (x + i, y + i, int(w - i * 2), int(h - i * 2)), 1)


def test_rect():
    # pos of UL corner
    origx = 100
    origy = 10
    # size of rect
    sizex = 100
    sizey = 80
    # deg CW
    angle = 20

    angle = angle * math.pi / 180
    hwidth = int(math.cos(angle) * sizex)
    hheight = int(math.sin(angle) * sizex)
    vwidth = int(math.sin(angle) * sizey)
    vheight = int(math.cos(angle) * sizey)

    # h-skew
    ox = DDA(0, vwidth / 2, vheight)
    oy = origy
    for j in range(vheight):
        # v-skew
        hx = origx - ox.w
        hy = DDA(oy, hwidth / 2, hwidth)
        for i in range(hwidth):
            screen.set_at((hx, hy.w), line_color)
            hx += 1
            hy.add(hheight)
        pygame.display.update()

        ox.add(vwidth)
        oy += 1

    pygame.draw.rect(screen, pygame.Color('green'),
                     (origx, origy, sizex, sizey), 1)
    #pygame.draw.line(screen, pygame.Color('red'), (origx, origy), (origx+hwidth, origy+hheight))

    pygame.display.update()


def test_triangle(phil):
    p1 = (20, 10)
    p2 = (50, 60)
    p3 = (10, 110)
    pygame.draw.line(screen, pygame.Color('red'), p1, p2)
    pygame.draw.line(screen, pygame.Color('red'), p2, p3)
    pygame.draw.line(screen, pygame.Color('red'), p3, p1)
    pygame.display.update()

    #step in y dir
    #left
    dx = p3[0] - p1[0]
    dy = p3[1] - p1[1]
    Ln = dx / 2
    Li = dx
    Ld = dy
    left = DDA(p1[0], Ln, Ld)
    #right
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    Rn = dx / 2
    Ri = dx
    Rd = dy
    right = DDA(p1[0], Rn, Rd)

    for y in range(p1[1], p2[1]):
        pygame.draw.line(screen, phil, (left.w, y), (right.w - 1, y))
        left.add(Li)
        right.add(Ri)
        pygame.display.update()

    #second right
    dx = p3[0] - p2[0]
    dy = p3[1] - p2[1]
    Rn = dx / 2
    Ri = dx
    Rd = dy
    right = DDA(p2[0], Rn, Rd)

    for y in range(p2[1], p3[1]):
        pygame.draw.line(screen, phil, (left.w, y), (right.w - 1, y))
        left.add(Li)
        right.add(Ri)
        pygame.display.update()


def test_triangle2():
    p1 = (20, 10)
    uv1 = (100, 10)
    p2 = (50, 60)
    uv2 = (140, 10)
    p3 = (10, 110)
    uv3 = (100, 70)

    pygame.draw.line(screen, pygame.Color('red'), p1, p2)
    pygame.draw.line(screen, pygame.Color('red'), p2, p3)
    pygame.draw.line(screen, pygame.Color('red'), p3, p1)
    pygame.display.update()

    ## RENDER TOP PART
    dest_left = TrackXY.make(p1[1], p3[1], p1[0], p3[0], p1[1], p3[1])
    dest_right = TrackXY.make(p1[1], p2[1], p1[0], p2[0], p1[1], p2[1])

    #source
    #  left will step once per p1..p3
    src_left = TrackXY.make(p1[1], p3[1],
                            uv1[0], uv3[0], uv1[1], uv3[1])
    #  right once per p1..p2
    src_right = TrackXY.make(p1[1], p2[1],
                            uv1[0], uv2[0], uv1[1], uv2[1])

    for y in range(p1[1], p2[1]):
        src_line = TrackXY.make(
          dest_left.xdda.w, dest_right.xdda.w,
          src_left.xdda.w, src_right.xdda.w,
          src_left.ydda.w, src_right.ydda.w)
        src_left.step()
        src_right.step()
      
        for x in range(dest_left.xdda.w, dest_right.xdda.w):
            c = screen.get_at(src_line.coord())
            #screen.set_at(src_line.coord(), pygame.Color('red'))
            src_line.step()
            screen.set_at((x, y), c)
        dest_left.step()
        dest_right.step()
        pygame.display.update()

    ## RENDER BOTTOM PART
    #second right
    dest_right = TrackXY.make(p2[1], p3[1], p2[0], p3[0], p2[1], p3[1])

    src_right = TrackXY.make(p2[1], p3[1],
                          uv2[0], uv3[0], uv2[1], uv3[1])

    for y in range(p2[1], p3[1]):
        src_line = TrackXY.make(
          dest_left.xdda.w, dest_right.xdda.w,
          src_left.xdda.w, src_right.xdda.w,
          src_left.ydda.w, src_right.ydda.w)
        src_left.step()
        src_right.step()

        for x in range(dest_left.xdda.w, dest_right.xdda.w):
            c = screen.get_at(src_line.coord())
            #screen.set_at(src_line.coord(), pygame.Color('red'))
            src_line.step()
            screen.set_at((x, y), c)
        dest_left.step()
        dest_right.step()
        pygame.display.update()


screen_color = (49, 150, 100)
line_color = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((200, 200), flags=pygame.SCALED)
pygame.display.set_caption('Hello World!')

#test_rect()
#test_triangle(pygame.Color('white'))
draw_source(100, 10, 40, 60)
test_triangle2()

# while True:
#     for event in pygame.event.get():
#         if event.type == QUIT:
#             pygame.quit()
#             sys.exit()
