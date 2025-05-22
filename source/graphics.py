import pygame as pg
import numpy as np
import re
import os

offset = np.array([8,8])

image_pattern = re.compile(r".*assets/images/(.*)\.png")
font_pattern = re.compile(r".*assets/fonts/(.*)\.ttf")

def read_folder(relative_path: str, file_type: str = None) -> list[str]:
    path = os.path.join(os.getcwd(), relative_path)
    if not os.path.exists(path): raise ValueError(f"Functions: read_folder path does not exist {path}")
    path_list = []
    for file in os.listdir(path):
        joined_path = os.path.join(path, file)
        if os.path.isfile(joined_path): 
            if not file_type or file.lower().endswith(file_type.lower()): path_list.append(joined_path)
        else:
            path_list += read_folder(os.path.join(relative_path, file), file_type)
    return path_list

def font_dict_setup():
    pg.font.init()
    fonts_dict: dict[str, pg.font.Font] = {"basic": pg.font.Font(pg.font.get_default_font(), 10)}
    for path in read_folder("assets/fonts", "ttf"):
        key = font_pattern.match(path).group(1)
        fonts_dict[key] = pg.font.Font(path, 10)
    return fonts_dict

def image_dict_setup():
    image_dict: dict[str, pg.surface.Surface] = {}
    for path in read_folder("assets/images", "png"):
        image = pg.image.load(path).convert_alpha()
        key = image_pattern.match(path).group(1)
        image_dict[key] = pg.transform.scale(image, (16, 16))
    return image_dict

class SurfaceSprite(pg.sprite.Sprite):
    def __init__(self, image_dict: dict[str, pg.surface.Surface], path: str, position: np.ndarray):
        super().__init__()
        self.image = image_dict[path]
        self.rect = self.image.get_rect(topleft=position)

class Graphics():
    def __init__(self):
        self.fonts_dict = None
        self.image_dict = None
        self.camera_speed = 0.001
        self.camera = np.array((0,0))
        
    def setup(self):
        self.screen = pg.display.set_mode(pg.display.get_desktop_sizes()[0])
        pg.display.set_caption("NAME")
        pg.display.set_icon(pg.image.load("assets/images/icon.png"))
        self.screen_size = np.array(self.screen.get_size())
        self.screen_center = self.screen_size * 1/2
        self.fonts_dict = font_dict_setup()
        self.image_dict = image_dict_setup()
    
    def update(self, dt: float, mouse_location: np.ndarray, path_position_list: list[tuple[str, np.ndarray]], tick_count: int = None):     
        mouse_location_center = mouse_location - self.screen_center
        difference_from_camera =  mouse_location_center - self.camera
        scalar = self.camera_speed * dt
        delta_cam = difference_from_camera * scalar
        self.camera = self.camera + delta_cam
        
        group = pg.sprite.Group()
        
        for path, position in path_position_list:
            position = position + self.camera + self.screen_center

            if not np.all(position > 0) and np.all(position < self.screen_size): continue
            group.add(SurfaceSprite(self.image_dict, path, position + offset))

        self.screen.fill(color="black")

        try: group.draw(self.screen)
        except Exception as e: raise ValueError(f"Graphics: unable to draw creatures. Error: {e}")

        text_list  = (
            [f"dt: {dt}", f"center: {mouse_location_center}", f"camera: {self.camera.round()}", f"ticks: {tick_count}"]  + 
            [f"{path} {i}: {position.round()}" for i, (path, position) in enumerate(path_position_list) if not path == "food"])
        
        font = self.fonts_dict["basic"]
        for i, text in enumerate(text_list):
            text_surface = font.render(text, True, "white")
            text_rect = text_surface.get_rect(center=(100, 40 + 20 * i))
            self.screen.blit(text_surface, text_rect)

        pg.display.update()