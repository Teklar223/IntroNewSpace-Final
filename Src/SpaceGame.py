import math
import random

from Src.GuidingArrow import get_angle, distance
import pygame
from pygame.locals import *
from random import randint
from Src.Configuration import Configuration
from Src.Spaceship import Spaceship
from Src.Engine import Engine
from .Util.Util import FONT, InputBox,to_pg_coords, to_pg_angle # to pygame (co-ordinates)
from .Util.pygame_functions import *
from Src.game_constants import *
from Src.Constants import *

# wasd Constants
UP = K_w
DOWN = K_s
LEFT = K_a
RIGHT = K_d

def _config_zero():
    kwargs = {
            f"{c_vertical_speed}": 0.0,
            f"{c_horizontal_speed}": 0.0,
            f"{c_angle}": 90.0,
            f"{c_engine_power}": 0.0,
            f"{c_latitude}": 0.0,
            f"{c_altitude}" : 1000
        }
    return kwargs


class SpaceGame:
    '''
    This is the 'Controller' of our simulation
    '''

    def __init__(self, width=1600, height=800):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ship = None
        self.font = pygame.font.SysFont(None, 24)
        self.config_text_surfaces = {}
        self.config = Configuration(**_config_zero())  # Creates a default config
        self.target = (0,0)
        self.bg = Background()
        self.ground_color = (128, 128, 128)  # Define the color of the ground floor

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return False

        return True

    def start(self):
        self.startMenu()

    def startMenu(self):
        input_boxes = []  # List to store the input boxes

        # Create input boxes for each configuration variable
        y_offset = 10
        for key, value in self.config.__dict__.items():
            if key not in ["WEIGHT_EMP", "WEIGHT_FUEL", "WEIGHT_FULL", "MAIN_ENG_F", "SECOND_ENG_F", "MAIN_BURN",
                           "SECOND_BURN", "ALL_BURN", "is_player"]:
                permatxt = f"{key}: "
                x = self.screen.get_width() - 210
                input_box = InputBox(x, y_offset, 200, 30, text=str(value), permatext=permatxt)
                input_boxes.append(input_box)
                y_offset += 40

        start_button_rect = pygame.Rect(300, 200, 200, 100)  # Rect for the start button
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return

                # Handle events for the input boxes
                for input_box in input_boxes:
                    input_box.handle_event(event, self.set_config)

            self.screen.fill((255, 255, 255))

            # Draw the start button
            pygame.draw.rect(self.screen, (0, 255, 0), start_button_rect)
            start_button_text = self.font.render("Start", True, (0, 0, 0))
            start_button_text_rect = start_button_text.get_rect(center=start_button_rect.center)
            self.screen.blit(start_button_text, start_button_text_rect)

            # Render and blit configuration values
            for input_box in input_boxes:
                input_box.update()
                input_box.draw(self.screen)

            pygame.display.flip()

            # Check if the start button is clicked
            if pygame.mouse.get_pressed()[0] and start_button_rect.collidepoint(pygame.mouse.get_pos()):
                # Update the configuration variables
                # for input_box in input_boxes:
                #    setattr(self.config, input_box.permatext, input_box.text)
                input_boxes.clear()
                self.startGame()
                running = False

    def set_config(self, key, value):
        # TODO: maybe more precise validation (per paramater?)
        def is_number(s):
            try:
                float(s)
                return True
            except ValueError:
                return False

        if is_number(value):
            d = self.config.__dict__
            d[key[:-2]] = float(value)

    def render_config(self, config):
        # TODO: display up to 3 numbers after the dot (.000 but not .0000)
        # TODO: display avg of the previous x dt for every param? (say avg speed in the last 5 dt)
        y_offset = 10
        for key, value in config.__dict__.items():
            if key not in ["WEIGHT_EMP", "WEIGHT_FUEL", "WEIGHT_FULL", "MAIN_ENG_F", "SECOND_ENG_F", "MAIN_BURN",
                           "SECOND_BURN", "ALL_BURN", "is_player"]:
                text = f"{key}: {value:.5f}"
                if key not in self.config_text_surfaces or self.config_text_surfaces[key] != text:
                    rendered_text = self.font.render(text, True, (255, 255, 255))
                    self.config_text_surfaces[key] = rendered_text
                text_surface = self.config_text_surfaces[key]
                text_rect = text_surface.get_rect(topright=(self.screen.get_width() - 10, y_offset))
                self.screen.blit(text_surface, text_rect)
                y_offset += 24

    def blit_config_values(self):
        for text_surface in self.config_text_surfaces.values():
            self.screen.blit(text_surface, text_surface.get_rect())

    def render_background(self):
        #if self.ship.config.alt > self.ground_threshold:
            # get the opposite speeds (cause we want the image to go in the other direction the ships is 'going')
            hs = -self.config.hs
            vs = -self.config.vs
            scrollBackground(int(hs), -int(vs), self.bg, self.screen) # y is negative due to pygame
                                    # double negative is left for understanding :)

    def render_arrow(self,arrow):
        moon_coordinates = [0, 0] # static target for easy calculations...
        x_arrow = 60
        y_arrow = 60
        x_space = int(self.config.lat)
        y_space = int(self.config.alt)
        space_coordinates = [x_space, y_space]
        arrow_angle = to_pg_angle(get_angle(space_coordinates, moon_coordinates))
        rotated_arrow = pygame.transform.rotate(arrow, arrow_angle)
        rotated_rectangle = rotated_arrow.get_rect(center=(x_arrow, y_arrow))
        self.screen.blit(rotated_arrow, rotated_rectangle)

    def render_time_factor(self, screen):
        time_factor_text = FONT.render(f"X{self.ship.time_factor}", True, (255, 255, 255))
        screen.blit(time_factor_text, (10, 10))  # Adjust the position as needed

    def render_ground(self,screen):        
        # Check if the ship is below the ground height threshold
        alt = self.ship.config.alt
        screen_height = self.screen.get_height()
        if alt <= 0.5 * screen_height:
            # Render the ground floor
            ground_height = screen_height - self.calc_ground(alt, screen_height)
            #left, top = to_pg_coords(x = 0, y = ground_height, canvas_height = screen_height)
            #width, height = to_pg_coords(x = screen.get_width(), y = ground_height, canvas_height = screen_height)
            ground_rect = pygame.Rect(0, ground_height, screen.get_width(), screen_height)
            pygame.draw.rect(screen, self.ground_color, ground_rect)

    def calc_ground(self,alt, screen_height):
        x1 = 0
        y1 = 0.5 * screen_height
        x2 = 0.5 * screen_height
        y2 = 0
        m = (y2 - y1) / (x2 - x1)
        ground_height = m * alt + 0.5 * screen_height
        return ground_height

    def end_condition(self) -> bool:
        alt = self.ship.config.alt
        if alt > 0:
            return True
        else:
            return False

    def check_victory(self) -> bool:
        vs    = self.ship.config.vs
        hs    = self.ship.config.hs
        angle = self.ship.config.angle
        if -5 <= vs and -5 < hs < 5 and 85 < angle < 95:
            return True
        else:
            return False 
            

    def startGame(self):
        os.chdir("..") # CWD is Src/Util when runtime raches this point (for some reason)
        bg = pygame.image.load('Media/background.jpg').convert()
        arrow = pygame.image.load('Media/arrow.png')

        arrow = pygame.transform.scale(arrow, (60, 100))
        grid_size = 3
        grid = []
        for i in range(grid_size):
            row = [bg_name for i in range(grid_size)]
            grid.append(row)
        event_i = random.randint(0, grid_size - 1)
        event_j = random.randint(0, grid_size - 1)
        grid[event_i][event_j] = death_star
        # self.bg.setTiles(tiles=[bg_name, 'Media/death_star.jpeg', 'Media/knowhere.jpg'], screen=self.screen)
        self.bg.setTiles(tiles=grid, screen=self.screen)
        x, y = to_pg_coords(self.screen.get_width() / 2, 0.9 * self.screen.get_height(), self.screen.get_height())
        self.ship = Spaceship(self.config, init_x=x, init_y=y)
        self.ship.rotate_ship()  # Rotate the ship to the correct angle to begin the simulation
        self.ship.set_first_position(self.screen.get_width(), self.screen.get_height())
        self.engine = Engine(self.config)
        running = True
        while running:
            dt = 1/self.clock.tick(60)
            running = self._handle_events()

            self.ship.update(engine=self.engine,
                             dt = dt,
                             width=self.screen.get_width(),
                             height=self.screen.get_height()
                             )
            running = self.end_condition()
            
            self.render_background()
            self.render_arrow(arrow = arrow)
            self.render_config(self.ship.config)
            self.render_time_factor(screen=self.screen)
            self.render_ground(screen=self.screen)
            self.screen.blit(self.ship.image, self.ship.rect)

            pygame.display.flip()

        self.EndGame()

    def EndGame(self):
        # TODO...
        flag = self.check_victory()
        running = True
        while running:
            # dt = 1/self.clock.tick(60)
            running = self._handle_events()
            self.render_background()
            #self.render_arrow(arrow = arrow)
            self.render_config(self.ship.config)
            #self.render_time_factor(screen=self.screen)
            self.render_ground(screen=self.screen)
            self.screen.blit(self.ship.image, self.ship.rect)
        pygame.quit()