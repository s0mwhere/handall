import pygame
import math
from sys import exit 
from random import randint, choice
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


class righthand(pygame.sprite.Sprite):
    def __init__(self,layer):
        super().__init__()
        self.layer = layer
        if layer == 1:
            hitbox = 15
            self.color = 'cyan'
        if layer == 2:
            hitbox = 40
            self.color = 'red'
        if layer == 3:
            hitbox = 55
            self.color = 'purple'
        self.rect = pygame.Rect(0,0,hitbox,math.sqrt(ballrad*ballrad-hitbox*hitbox/4.0)*2)
        
    def position(self):
        self.rect.center = right_wrist_coords
        # pygame.draw.circle(screen,'blue',self.rect.center,30)
        pygame.draw.rect(screen,self.color,self.rect)
        
    def update(self):
        self.position()
        if self.layer == 1: pygame.draw.circle(screen,'blue',self.rect.center,ballrad)

class leftthand(pygame.sprite.Sprite):
    def __init__(self,layer):
        super().__init__()
        self.layer = layer
        if layer == 1:
            hitbox = 15
            self.color = 'cyan'
        if layer == 2:
            hitbox = 40
            self.color = 'red'
        if layer == 3:
            hitbox = 55
            self.color = 'purple'
        self.rect = pygame.Rect(0,0,hitbox,math.sqrt(ballrad*ballrad-hitbox*hitbox/4.0)*2)
        self.rect.center = [0,0]

    

    def position(self):
        self.rect.center = left_wrist_coords
        # pygame.draw.circle(screen,'blue',self.rect.center,30)
        pygame.draw.rect(screen,self.color,self.rect)
        
    def update(self):
        
        self.position()
        if self.layer == 1: pygame.draw.circle(screen,'blue',self.rect.center,ballrad)

class obstacle2(pygame.sprite.Sprite):
    def __init__(self,spawn_rect):
        super().__init__()
        self.sprect = pygame.Rect(spawn_rect)
        self.sides = choice([1,2,3,4])
        self.width = choice([50,100,150,200])
        self.height = choice([50,100,150,200])

        if self.sides == 1:
            self.posx = self.sprect.left-self.width
            self.posy = randint(self.sprect.top,self.sprect.bottom-self.height)
        if self.sides == 2:
            self.posx = randint(self.sprect.left,self.sprect.right-self.width)
            self.posy = self.sprect.top-self.height
        if self.sides == 3:
            self.posx = self.sprect.right
            self.posy = randint(self.sprect.top,self.sprect.bottom-self.height)
        if self.sides == 4:
            self.posx = randint(self.sprect.left,self.sprect.right-self.width)
            self.posy = self.sprect.bottom
        self.rect = pygame.Rect(self.posx,self.posy,self.width,self.height)
        

    def movement(self):
        if self.sides == 1: self.posx += 10
        if self.sides == 2: self.posy += 10
        if self.sides == 3: self.posx -= 10
        if self.sides == 4: self.posy -= 10
        self.rect = pygame.Rect(self.posx,self.posy,self.width,self.height)
        if (self.posx < -300 or self.posx > 1580
            or self.posy < -300 or self.posy > 1020): self.kill()

        pygame.draw.rect(screen,'blue',self.rect)
    def update(self):
        self.movement()

class obstacle1(pygame.sprite.Sprite):
    def __init__(self,spawn_rect):
        super().__init__()
        self.sprect = pygame.Rect(spawn_rect)
        self.engage = 0
        self.color = pygame.Color(0,255,0,0)
        self.kill_time = 5

        self.posx = randint(self.sprect.left,self.sprect.width-50)
        self.posy = randint(self.sprect.top,self.sprect.bottom-50)
        self.width = (randint(50,self.sprect.width-self.posx))//50*50
        self.height = (randint(50,self.sprect.height-self.posy)//50)*50
        
        self.rect1 = pygame.Rect(self.posx,self.posy,self.width,self.height)
        self.rect = pygame.Rect(-100,-100,0,0)

    def collision(self):
        for event in event_list:
            if event.type == obstacle_timer:
                self.kill_time -= 1
            if self.kill_time == 4: self.color = pygame.Color('green')
            if self.kill_time == 3: self.color = pygame.Color('yellow')
            if self.kill_time == 2: self.color = pygame.Color('red')

        if self.engage <1500: 
            self.engage +=50
            self.color.a = int((self.engage/1500)*255)
            
        if self.kill_time <= 2: self.rect = self.rect1
        if self.kill_time == 0: self.kill()

    def update(self):
        self.collision()
        
        draw_rect_alpha(screen,self.color,self.rect1)

class Cover(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.flip = True
        self.posx = -screen_width/3
        self.posy = 0
        self.rect_main = pygame.Rect(0,0,screen_height,screen_width/3)
        
    def movement(self):
        if self.flip: self.posx = -screen_width/3
        if game_state == 3:
            self.flip = False
            if self.posx < 0: self.posx += 20
            if self.posx >= 0: self.posx = 0
        if game_state == 2:
            if self.posx < screen_width*(2/3): self.posx += 20
            if self.posx >= screen_width*(2/3): self.posx = screen_width*(2/3)
        if game_state == 1:
            if self.posx < screen_width and self.posx>0: self.posx += 20
            if self.posx >=screen_width: self.flip = True
        self.rect_main = pygame.Rect(self.posx, self.posy, screen_width/3, screen_height)

    def cover_score(self):
        box_text(screen,test_font,self.posx+120,self.posx+200,self.posy+100,
                 f'Score: {score} /n Highscore: {highscore}',(64,64,64))

    def update(self):
        self.movement()
        pygame.draw.rect(screen,'gray',self.rect_main)
        self.cover_score()

class optionbox1(pygame.sprite.Sprite):
    def __init__(self,color, pos):
        super().__init__()
        self.color = color
        self.pos = pos
        
        self.rect = pygame.Rect(-200,-200,100,100)
        self.rect2 = pygame.Rect(-200,-200,100,100)
        
        self.hold_time = 0

    def trigger(self):
        self.rect.center = self.pos
        if (pygame.sprite.spritecollide(self,right_hand,False)
        or pygame.sprite.spritecollide(self,left_hand,False)):
            self.hold_time += 1
        elif(self.hold_time > 0): self.hold_time -= 1

    def animation(self):
        global game_state
        if game_state == -4: text1_surf = test_font.render('PLAY',False,(64,64,64))
        else : text1_surf = test_font.render('CONTINUE',False,(64,64,64))
        text1_rect = text1_surf.get_rect(center = (self.rect.centerx,self.rect.top-20))
        screen.blit(text1_surf,text1_rect)

        self.rect2.height = (self.hold_time/30)*100
        self.rect2.bottomleft = self.rect.bottomleft
        pygame.draw.rect(screen,self.color,self.rect,2)
        pygame.draw.rect(screen,self.color,self.rect2)

    def confirm(self):
        global game_state
        if self.hold_time == 30:

            game_state = -2

    def update(self):
        self.trigger()
        self.animation()
        self.confirm()

class optionbox2(pygame.sprite.Sprite):
    def __init__(self,color, pos):
        super().__init__()
        self.color = color
        self.pos = pos
        
        self.rect = pygame.Rect(-200,-200,100,100)
        self.rect2 = pygame.Rect(-200,-200,100,100)
        
        self.hold_time = 0

    def trigger(self):
        self.rect.center = self.pos
        if (pygame.sprite.spritecollide(self,right_hand,False)
        or pygame.sprite.spritecollide(self,left_hand,False)):
            self.hold_time += 1
        elif(self.hold_time > 0): self.hold_time -= 1

    def animation(self):
        text1_surf = test_font.render('QUIT',False,(64,64,64))
        text1_rect = text1_surf.get_rect(center = (self.rect.centerx,self.rect.top-20))
        screen.blit(text1_surf,text1_rect)
        
        self.rect2.height = (self.hold_time/30)*100
        self.rect2.bottomleft = self.rect.bottomleft
        pygame.draw.rect(screen,self.color,self.rect,2)
        pygame.draw.rect(screen,self.color,self.rect2)

    def confirm(self):
        if self.hold_time == 30:
            pygame.quit()
            exit()

    def update(self):
        self.trigger() 
        self.animation()
        self.confirm()

def collision_sprite():
	if (pygame.sprite.groupcollide(left_hand,obstacle_group,False,False) 
        or pygame.sprite.groupcollide(right_hand,obstacle_group,False,False)):
		return True
	else: return False

def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

def box_text(surface, font, x_start, x_end, y_start, text, colour):
        x = x_start
        y = y_start
        words = text.split(' ')
        word_a = font.render('a', True, colour)

        for word in words:
            if word == '/n': 
                y += word_a.get_height() * 1.1
                x = x_start
                continue
            if word == '/s':
                x += word_a.get_width() * 1.1
                continue

            word_t = font.render(word, True, colour)
            if word_t.get_width() + x <= x_end:
                surface.blit(word_t, (x, y))
                x += word_t.get_width() * 1.1
            else:
                y += word_t.get_height() * 1.1
                x = x_start
                surface.blit(word_t, (x, y))
                x += word_t.get_width() * 1.1

def display_score():
	current_time = int(pygame.time.get_ticks() / 1000) - start_time
	return current_time

def gamestate():
    delta_time =  score % 30         # 3:right half  #2 left half   #1 all
    if delta_time <10:
        if delta_time == 0:
            left_hand.empty()
            if not right_hand: right_hand.add(righthand(1),righthand(2),righthand(3))
            obstacle_group.empty()
        return 3
    if delta_time <20:
        if delta_time == 10:
            right_hand.empty()
            if not left_hand: left_hand.add(leftthand(1),leftthand(2),leftthand(3))
            obstacle_group.empty()
        return 2
    if delta_time <30: 
        if delta_time ==20:
            if not right_hand: right_hand.add(righthand(1),righthand(2),righthand(3))
            obstacle_group.empty()
        return 1
    return 99

def mocap():
    global right_wrist_coords, left_wrist_coords
        
    success,image = cap.read()
    image = cv2.flip(image,1)

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    
    if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Right wrist (landmark index 16) and Left wrist (landmark index 15)
            right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
            left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]

            # Extracting x, y coordinates of right and left wrists
            h, w, _ = image.shape
            left_wrist_coords = (int(right_wrist.x * w), int(right_wrist.y * h))
            right_wrist_coords = (int(left_wrist.x * w), int(left_wrist.y * h))

pygame.init()
screen_height =720
screen_width =1280
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("lmao")
clock = pygame.time.Clock()

start_time = 0
test_font = pygame.font.Font('font/Pixeltype.ttf', 50)
instruction = 'Instruction: /n /n 1.move your hand to control the ball /n 1.avoid the quare'

ballrad = 30
game_state = -4
score = 0
highscore = 0

obstacle_group = pygame.sprite.Group()
rect_state1 = pygame.Rect(0,0,screen_width,screen_height)
rect_state2 = pygame.Rect(0,0,screen_width*(2/3),screen_height)
rect_state3 = pygame.Rect(screen_width/3,0,screen_width*(2/3),screen_height)
rect_state = rect_state3

option_box = pygame.sprite.Group()

left_hand = pygame.sprite.Group()

right_hand = pygame.sprite.Group()

info_board = pygame.sprite.Group()
info_board.add(Cover())

obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer,1500)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
pose = mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        smooth_landmarks=True) 

while True:
    mocap()
    screen.fill('white')
    event_list = pygame.event.get()

    for event in event_list:
        if event.type == pygame.QUIT:
            pygame.quit()
            cap.release()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                screen.fill('purple')
        if event.type == obstacle_timer and game_state >= 0:
            if game_state == 3: rect_state = rect_state3
            if game_state == 2: rect_state = rect_state2
            if game_state == 1: rect_state = rect_state1
            obstacle_group.add(choice([obstacle2(rect_state),obstacle1(rect_state)]))

    if game_state >= 0:
        obstacle_group.update()
    
        info_board.update()

        score = display_score()
        game_state = gamestate()
        if collision_sprite(): 
            option_box.add(optionbox1('green',(screen_width*3/4,200)))
            option_box.add(optionbox2('red',(screen_width*1/4,200)))
            game_state = -3
        
    if game_state == -2:
        obstacle_group.empty()
        start_time = int(pygame.time.get_ticks() / 1000)
        option_box.empty()
        game_state = 3

    if game_state == -3 or game_state == -4:
        if score > highscore: highscore = score
        if not option_box:
            option_box.add(optionbox1('green',(screen_width*3/4,200)))
            option_box.add(optionbox2('red',(screen_width*1/4,200)))
        if not right_hand: right_hand.add(righthand(1),righthand(2),righthand(3))
        if not left_hand: left_hand.add(leftthand(1),leftthand(2),leftthand(3))
        option_box.update()

        if game_state == -3:
            box_text(screen,test_font,screen_width*2/5,screen_width*3/5,screen_height/2,
                 f'Score: {score} /n Highscore: {highscore}',(64,64,64))

        if game_state == -4:
            box_text(screen,test_font,screen_width*2/6-50,screen_width*4/5,screen_height/2,instruction,'gray')

    # pygame.draw.rect(screen,'green',rect_state,2)
    right_hand.update()
    left_hand.update()
    
    pygame.display.update()   
    clock.tick(60)