"""Game state, loop detection, scoring, rendering, and input."""
from collections import defaultdict
import pygame
from constants import *
from tile import Side
from tiles import TileRack, initialize_tiles

class Button:
    def __init__(self, rect, text):
        self.rect, self.text = pygame.Rect(rect), text

    def draw(self, screen, font, enabled=True):
        mouse = pygame.mouse.get_pos()
        if not enabled: color = gCOLOR_BUTTON_DISABLED
        elif self.rect.collidepoint(mouse): color = gCOLOR_BUTTON_HOVER
        else: color = gCOLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        pygame.draw.rect(screen, gCOLOR_PANEL_BORDER, self.rect, 2, border_radius=6)
        image = font.render(self.text, True, gCOLOR_TEXT)
        screen.blit(image, image.get_rect(center=self.rect.center))

class Game:
    def __init__(self, screen, sprites):
        self.screen, self.sprites = screen, sprites
        self.font = pygame.font.SysFont(None, 26)
        self.small_font = pygame.font.SysFont(None, 21)
        self.large_font = pygame.font.SysFont(None, 38)
        self._create_buttons()
        self.new_game()

    def _create_buttons(self):
        x, width = gPANEL_X+gPANEL_MARGIN, gPANEL_WIDTH-2*gPANEL_MARGIN
        half = (width-gBUTTON_GAP)//2
        y = 385
        self.rotate_left_button = Button((x,y,half,gBUTTON_HEIGHT), "ROTATE L")
        self.rotate_right_button = Button((x+half+gBUTTON_GAP,y,half,gBUTTON_HEIGHT), "ROTATE R")
        y += gBUTTON_HEIGHT+gBUTTON_GAP
        self.place_button = Button((x,y,width,gBUTTON_HEIGHT), "PLACE")
        y += gBUTTON_HEIGHT+gBUTTON_GAP
        self.quit_button = Button((x,y,width,gBUTTON_HEIGHT), "QUIT")
        y = 440
        self.play_again_button = Button((x,y,width,gBUTTON_HEIGHT), "PLAY AGAIN")
        self.game_quit_button = Button((x,y+gBUTTON_HEIGHT+gBUTTON_GAP,width,gBUTTON_HEIGHT), "QUIT")

    def new_game(self):
        self.board = [[None for _ in range(gBOARD_SIZE)] for _ in range(gBOARD_SIZE)]
        self.rack = TileRack(initialize_tiles())
        self.score = self.placement_count = self.last_score = 0
        self.selected_slot = None
        self.hover_cell = None
        self.game_over = False
        self.quad_loop_counts = defaultdict(int)
        self.scored_loop_signatures = set()

    def board_cell_at(self, position):
        x,y = position
        col,row = (x-gBOARD_X)//gTILE_SIZE, (y-gBOARD_Y)//gTILE_SIZE
        return (row,col) if 0 <= row < gBOARD_SIZE and 0 <= col < gBOARD_SIZE else None

    def rack_rect(self, slot):
        x, width, gap = gPANEL_X+gPANEL_MARGIN, gPANEL_WIDTH-2*gPANEL_MARGIN, 8
        tile_width = (width-gap*(gEXPOSED_TILE_COUNT-1))//gEXPOSED_TILE_COUNT
        return pygame.Rect(x+slot*(tile_width+gap),225,tile_width,tile_width)

    def select_slot(self, slot):
        if not self.game_over and self.rack.exposed[slot] is not None:
            self.selected_slot = slot

    def rotate_selected(self, clockwise=True):
        if self.game_over or self.selected_slot is None: return
        tile = self.rack.exposed[self.selected_slot]
        if tile:
            tile.rotate_clockwise() if clockwise else tile.rotate_counterclockwise()

    def place_selected(self, row, col):
        if self.game_over or self.selected_slot is None or self.board[row][col] is not None:
            return False
        tile = self.rack.take_tile(self.selected_slot)
        if tile is None: return False
        self.board[row][col] = tile
        self.placement_count += 1
        self.last_score = self._score_new_loops()
        slot = self.selected_slot
        self.rack.draw_replacement(slot)
        self.selected_slot = self.hover_cell = None
        if self.placement_count == gBOARD_SIZE*gBOARD_SIZE:
            self.game_over = True
        return True

    # ----- loop graph -----
    def _build_path_graph(self):
        graph = defaultdict(set)
        for row in range(gBOARD_SIZE):
            for col in range(gBOARD_SIZE):
                tile = self.board[row][col]
                if tile is None: continue
                for a_side,b_side in tile.segments():
                    a,b = (row,col,int(a_side)),(row,col,int(b_side))
                    graph[a].add(b); graph[b].add(a)
                if col+1 < gBOARD_SIZE:
                    n = self.board[row][col+1]
                    if n and Side.RIGHT in tile.connections() and Side.LEFT in n.connections():
                        a,b=(row,col,int(Side.RIGHT)),(row,col+1,int(Side.LEFT))
                        graph[a].add(b); graph[b].add(a)
                if row+1 < gBOARD_SIZE:
                    n = self.board[row+1][col]
                    if n and Side.BOTTOM in tile.connections() and Side.TOP in n.connections():
                        a,b=(row,col,int(Side.BOTTOM)),(row+1,col,int(Side.TOP))
                        graph[a].add(b); graph[b].add(a)
        return graph

    @staticmethod
    def _components(graph):
        result, visited = [], set()
        for start in graph:
            if start in visited: continue
            stack, component = [start], set()
            while stack:
                node = stack.pop()
                if node in visited: continue
                visited.add(node); component.add(node)
                stack.extend(n for n in graph[node] if n not in visited)
            result.append(component)
        return result

    def _find_closed_loops(self):
        graph, loops = self._build_path_graph(), []
        for component in self._components(graph):
            if all(len(graph[node]) == 2 for node in component):
                signature = frozenset(component)
                if signature not in self.scored_loop_signatures:
                    loops.append((signature,component))
        return loops

    def _score_new_loops(self):
        total = 0
        for signature, component in self._find_closed_loops():
            positions = {(r,c) for r,c,_ in component}
            quads = {p for p in positions if self.board[p[0]][p[1]].is_quad()}
            points = len(positions) + len(quads)  # Quad counted twice.
            for p in quads:
                if self.quad_loop_counts[p] >= 1:
                    points += 5
            for p in quads:
                self.quad_loop_counts[p] += 1
            self.scored_loop_signatures.add(signature)
            total += points
        self.score += total
        return total

    # ----- rendering -----
    def _draw_tile_image(self, tile, rect, ghost=False):
        image = self.sprites[tile.tile_type]
        if tile.rotation:
            image = pygame.transform.rotate(image, -90*tile.rotation)
        image = pygame.transform.smoothscale(image, rect.size)
        if ghost:
            image = image.copy(); image.set_alpha(150)
        self.screen.blit(image, rect)

    def _draw_board(self):
        board = pygame.Rect(gBOARD_X,gBOARD_Y,gBOARD_PIXEL_SIZE,gBOARD_PIXEL_SIZE)
        pygame.draw.rect(self.screen,gCOLOR_BOARD,board)
        for row in range(gBOARD_SIZE):
            for col in range(gBOARD_SIZE):
                cell=pygame.Rect(gBOARD_X+col*gTILE_SIZE,gBOARD_Y+row*gTILE_SIZE,gTILE_SIZE,gTILE_SIZE)
                pygame.draw.rect(self.screen,gCOLOR_BOARD_GRID,cell,1)
                tile=self.board[row][col]
                if tile: self._draw_tile_image(tile,cell.inflate(-2,-2))
        if not self.game_over and self.selected_slot is not None and self.hover_cell:
            row,col=self.hover_cell; tile=self.rack.exposed[self.selected_slot]
            if tile:
                cell=pygame.Rect(gBOARD_X+col*gTILE_SIZE,gBOARD_Y+row*gTILE_SIZE,gTILE_SIZE,gTILE_SIZE)
                if self.board[row][col] is None:
                    self._draw_tile_image(tile,cell.inflate(-2,-2),True)
                    pygame.draw.rect(self.screen,gCOLOR_GOOD,cell,3)
                else:
                    pygame.draw.rect(self.screen,gCOLOR_BAD,cell,3)

    def _text(self,text,x,y,font=None,color=None):
        image=(font or self.font).render(text,True,color or gCOLOR_TEXT)
        self.screen.blit(image,(x,y))

    def _draw_panel(self):
        panel=pygame.Rect(gPANEL_X,20,gPANEL_WIDTH,gSCREEN_HEIGHT-40)
        pygame.draw.rect(self.screen,gCOLOR_PANEL,panel,border_radius=8)
        pygame.draw.rect(self.screen,gCOLOR_PANEL_BORDER,panel,2,border_radius=8)
        x=gPANEL_X+gPANEL_MARGIN
        self._text("SCORE",x,35,self.large_font)
        self._text(str(self.score),x,78,self.large_font,gCOLOR_GOOD)
        self._text(f"PLACED: {self.placement_count}/64",x,120,self.small_font)
        if self.last_score:
            self._text(f"LAST LOOP: +{self.last_score}",x,148,self.small_font,gCOLOR_GOOD)
        self._text("EXPOSED TILES",x,190,self.font)
        for slot in range(gEXPOSED_TILE_COUNT):
            rect=self.rack_rect(slot); tile=self.rack.exposed[slot]
            if tile is None:
                pygame.draw.rect(self.screen,gCOLOR_BUTTON_DISABLED,rect,border_radius=6)
                continue
            if slot==self.selected_slot:
                pygame.draw.rect(self.screen,gCOLOR_SELECTED,rect.inflate(8,8),4,border_radius=6)
            self._draw_tile_image(tile,rect)

        if self.game_over:
            self._text("GAME OVER",x,335,self.large_font)
            self._text("Board complete.",x,375,self.small_font)
            self.play_again_button.draw(self.screen,self.font)
            self.game_quit_button.draw(self.screen,self.font)
        else:
            enabled=self.selected_slot is not None
            self.rotate_left_button.draw(self.screen,self.font,enabled)
            self.rotate_right_button.draw(self.screen,self.font,enabled)
            can_place=enabled and self.hover_cell is not None
            if can_place:
                r,c=self.hover_cell; can_place=self.board[r][c] is None
            self.place_button.draw(self.screen,self.font,can_place)
            self.quit_button.draw(self.screen,self.font)
            self._text("Click tile to select.",x,555,self.small_font)
            self._text("Move over board; R/L rotate.",x,580,self.small_font)
            self._text("Click board or PLACE to commit.",x,605,self.small_font)
            self._text("ESC quits.",x,630,self.small_font)

    def draw(self):
        self.screen.fill(gCOLOR_BACKGROUND)
        self._draw_board(); self._draw_panel()
        pygame.display.flip()

    # ----- events -----
    def handle_mouse_motion(self, position):
        self.hover_cell=self.board_cell_at(position)

    def handle_mouse_button(self, position):
        if self.game_over:
            if self.play_again_button.rect.collidepoint(position): self.new_game()
            elif self.game_quit_button.rect.collidepoint(position): return "quit"
            return
        for slot in range(gEXPOSED_TILE_COUNT):
            if self.rack_rect(slot).collidepoint(position):
                self.select_slot(slot); return
        if self.rotate_left_button.rect.collidepoint(position):
            self.rotate_selected(False); return
        if self.rotate_right_button.rect.collidepoint(position):
            self.rotate_selected(True); return
        if self.quit_button.rect.collidepoint(position): return "quit"
        if self.place_button.rect.collidepoint(position):
            if self.hover_cell: self.place_selected(*self.hover_cell)
            return
        cell=self.board_cell_at(position)
        if cell: self.place_selected(*cell)

    def handle_key(self,key):
        if key==pygame.K_ESCAPE: return "quit"
        if self.game_over:
            if key==pygame.K_y: self.new_game()
            elif key==pygame.K_n: return "quit"
            return
        if key==pygame.K_r: self.rotate_selected(True)
        elif key==pygame.K_l: self.rotate_selected(False)
