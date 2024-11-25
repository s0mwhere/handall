from typing import Any
import pygame
import math
from sys import exit 
from random import randint, choice
import cv2
import mediapipe as mp
import pygame.gfxdraw
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

class hand(pygame.sprite.Sprite):
    def __init__(self,layer):
        super().__init__()
        self.layer = layer
        self.color = 'white'
        self.bluecir = [30,255]
        self.greencir = [120,0]
        self.redcir = [30,255]

        self.temp_health = 2
        self.temp_shield = shield
        
        if layer == 1: hitbox = 15
        if layer == 2: hitbox = 40
        if layer == 3: hitbox = 55
            
        self.rect = pygame.Rect(0,0,hitbox,math.sqrt(ballrad*ballrad-hitbox*hitbox/4.0)*2)
    def position(self):
        self.rect.center = right_wrist_coords
    
    def sfx(self):
        global health, shield
        if self.layer == 1: 
            if shield == 150: self.bluecir = [30,255]
            if shield >= 0.3: shield -= 0.3
            if self.temp_shield - shield > 0.58: shield += 0.3
            if shield < 0.3: 
                if self.bluecir[1] >= 15:
                    self.bluecir[0] += 5
                    self.bluecir[1] -= 15
                    draw_cir_alpha(screen,self.rect.centerx,self.rect.centery,self.bluecir[0],(52, 235, 219,self.bluecir[1]))
                shield = 0
            if health == 1 and self.redcir[1] >= 15:
                self.redcir[0] += 5
                self.redcir[1] -= 15
                draw_cir_alpha(screen,self.rect.centerx,self.rect.centery,self.redcir[0],(255, 0, 0,self.redcir[1]))
            if health == 2 and self.greencir[1] <= 255-20:
                self.greencir[0] -= 5
                self.greencir[1] += 15
                draw_cir_alpha(screen,self.rect.centerx,self.rect.centery,self.greencir[0],(0, 255, 0,self.greencir[1]))

            if self.temp_health < health: self.greencir = [120,0]
            if self.temp_health > health: self.redcir = [30,255]
            self.temp_health = health
            self.temp_shield = shield
            
    def display(self):
        global health, shield
        pygame.draw.circle(screen,'orange',self.rect.center,ballrad-5)
        pygame.draw.arc(screen,'#34ebdb',(self.rect.centerx-25,self.rect.centery-25,50,50),0,(shield/150)*2*math.pi,10)
        pygame.draw.circle(screen,'grey',self.rect.center,ballrad-10)
        pygame.draw.circle(screen,'green',self.rect.center,ballrad-10,0,-1+health,-1+health,1,1)
        pygame.draw.circle(screen, self.color, self.rect.center,ballrad,5)
        if game_state <= 0 :pygame.draw.circle(screen, self.color,self.rect.center,ballrad)

    def update(self):
        self.position()
        self.sfx()
        self.display()

class righthand(hand):    # control and display of right hand
    def __init__(self,layer):
        super().__init__(layer)
        self.color = 'blue'
    def position(self):
        self.rect.center = right_wrist_coords
        
class leftthand(hand):    #control and dispaly of left hand
    def __init__(self,layer):
        super().__init__(layer)
        self.color = 'red'
    def position(self):
        self.rect.center = left_wrist_coords

class obstacle2(pygame.sprite.Sprite):     #behaviour of sliding block
    def __init__(self,spawn_rect):
        super().__init__()
        self._layer = 1
        self.sprect = pygame.Rect(spawn_rect)
        self.sides = choice([1,2,3,4])       #side where it spawn 1:left  2:up  3:right  4:down
        self.portion = choice([0,1,2])       # each side cut into 3 portions

        width = self.sprect.width           #reduce the pain ahh code
        height = self.sprect.height
        posx = self.portion*width/3+self.sprect.x

        self.prep_time = 2000          #the visible duration of caution block

        if self.sides == 1:            #size and exact position
            self.rect = pygame.Rect(self.sprect.x-50,self.portion*height/3,50,height/3)
            self.posit = [self.sprect.x, self.portion*height/3, self.sprect.x+width/3, 
                          self.portion*height/3, self.sprect.x+width*2/3, self.portion*height/3]
        if self.sides == 2:
            self.rect = pygame.Rect(posx,-50,width/3,50)
            self.posit = [posx, self.sprect.y, posx,
                          self.sprect.y+height/3, posx, self.sprect.y+height*2/3]
        if self.sides == 3:
            self.rect = pygame.Rect(self.sprect.x+width,self.portion*height/3,50,height/3)
            self.posit = [self.sprect.x+width*2/3, self.portion*height/3, self.sprect.x+width/3, 
                          self.portion*height/3, self.sprect.x, self.portion*height/3]
        if self.sides == 4:
            self.rect = pygame.Rect(width/3*self.portion+self.sprect.x,height,width/3,50)
            self.posit = [posx, self.sprect.y+height*2/3, posx,
                          self.sprect.y+height/3, posx, self.sprect.y]
            
        obstacle_group.add(caution_block(self.posit,width,height,self.prep_time))    #spawning caution block
        
    def movement(self):         #movement duh
        if self.sides == 1: self.rect.x += 30
        if self.sides == 2: self.rect.y += 30
        if self.sides == 3: self.rect.x -= 30
        if self.sides == 4: self.rect.y -= 30
        
        if (self.rect.x < -300 or self.rect.x > 1580
            or self.rect.y < -300 or self.rect.y > 1020): self.kill()    #delete when out of bound
        pygame.draw.rect(screen,'blue',self.rect)

    def update(self):
        self.prep_time -=30
        if self.prep_time < 1000: self.movement()   #move only when caution block fully show
        
class caution_block(pygame.sprite.Sprite):      #pre warn sign for sliding block
    def __init__(self, posit, width, height, prep_time):
        super().__init__()
        self._layer = 0
        self.posit = posit
        self.prep_time = prep_time
        self.alpha_rate = 0
        self.caution1 = pygame.transform.scale(caution,(width/3, height/3))
        self.caution2 = pygame.transform.scale(caution,(width/3, height/3))
        self.caution3 = pygame.transform.scale(caution,(width/3, height/3))
        self.rect = (0,0,0,0)

    def appear(self):
        if self.prep_time >1000:
            self.caution1.set_alpha(self.alpha_rate)
            self.caution2.set_alpha(-50+self.alpha_rate)
            self.caution3.set_alpha(-100+self.alpha_rate)
        else:
            self.caution1.set_alpha(400 - self.alpha_rate)
            self.caution2.set_alpha(500 - self.alpha_rate)
            self.caution3.set_alpha(580 - self.alpha_rate)
        self.alpha_rate +=8
        self.prep_time -=30

        screen.blit(self.caution1,(self.posit[0],self.posit[1]))
        screen.blit(self.caution2,(self.posit[2],self.posit[3]))
        screen.blit(self.caution3,(self.posit[4],self.posit[5]))
        
        if self.prep_time <= -100: self.kill()

    def update(self):
        self.appear()

class obstacle1(pygame.sprite.Sprite):      #behaviout of poping block
    def __init__(self,spawn_rect):
        super().__init__()
        self._layer = 2
        self.sprect = pygame.Rect(spawn_rect)
        self.engage = 0
        self.engage2 = 100
        self.color = pygame.Color(0,255,0,0)
        self.kill_time = 5

        posx = randint(self.sprect.left, self.sprect.width - 50)
        posy = randint(self.sprect.top, self.sprect.bottom - 50)
        width = (randint(50, self.sprect.width - posx))//50*50
        height = (randint(50, self.sprect.height - posy)//50)*50
        
        self.rect1 = pygame.Rect(posx, posy, width, height)
        self.rect = pygame.Rect(-100,-100,0,0)
        self.w = self.rect1.width/2

    def collision(self):
        for event in event_list:
            if event.type == obstacle_timer:
                self.kill_time -= 1
            if self.kill_time == 5: self.color = pygame.Color('orange')
            if self.kill_time == 4: self.color = pygame.Color('orange')
            if self.kill_time == 2: self.color = pygame.Color('red')
        
        if self.engage <1500: #slowly make color visible
            self.engage +=50
            self.color.a = int((self.engage/1500)*255)      

        if self.kill_time <= 2: self.rect = self.rect1      #turn on hitbox
        if self.kill_time == 0: self.rect = (0,0,0,0)

    def display(self):
        if self.kill_time <=0:          #split in half when dissapear
            pygame.draw.rect(screen,'red',rect=(self.rect1.x, self.rect1.y, self.w, self.rect1.height))
            pygame.draw.rect(screen,'red',rect=(self.rect1.right - self.w, self.rect1.y, self.w, self.rect1.height))
            self.w -= 30
            if self.w <= 0: self.kill()

        if self.kill_time >0:           #fill the frame when collision is on
            if self.kill_time > 2: width = 5
            else: width = 0
            draw_rect_alpha(screen,self.color,self.rect1, width)

            if 2< self.kill_time <= 3: #flashing red as warning
                self.engage2 -= 1
                if int(abs(2*math.sin(pow((100-self.engage2)/10,2)))): draw_rect_alpha(screen,'red',self.rect1, width)
            
    def update(self):
        self.collision()
        self.display()
        
class healing_square(pygame.sprite.Sprite):     #behaviour of heal tile
    def __init__(self):
        super().__init__()
        self.color = 'green'
        self.pos = (randint(rect_state.x,rect_state.x+rect_state.width-300),randint(0, rect_state.bottom-300))
        self.healpng = pygame.image.load('graphics/heal square.png').convert_alpha()
        
        self.rect = pygame.Rect(-200,-200,300,300)
        self.rect2 = pygame.Rect(-200,-200,200,200)
        self.rect.topleft = self.pos

        self.hold_time = 0
        self.base_time = 3

    def trigger(self):
        if (pygame.sprite.spritecollide(self,right_hand,False)
        or pygame.sprite.spritecollide(self,left_hand,False)):
            self.hold_time += 0.03
        elif(self.hold_time > 0.03): self.hold_time -= 0.03
        elif(self.hold_time <= 0.03): self.hold_time = 0
        
    def animation(self):
        test_font2 = pygame.font.Font('font/Pixeltype.ttf', 70)
        text1_surf = test_font2.render("{:.1f}".format(self.base_time-self.hold_time),False,(64,64,64))
        text1_rect = text1_surf.get_rect(center = self.rect.center)
        screen.blit(text1_surf,text1_rect)
        
        # self.rect2.height = (self.hold_time/5)*100
        self.rect2.center = self.rect.center
        screen.blit(self.healpng,self.rect)
        # pygame.draw.rect(screen,self.color,self.rect2)
        pygame.draw.arc(screen, 'green', self.rect2, 0, (self.hold_time/self.base_time)*2*math.pi,15)

    def confirm(self):
        global game_state, health
        if self.hold_time >= self.base_time:
            health += 1
            self.kill()

    def update(self):
        self.trigger() 
        self.animation()
        self.confirm()

class shield_drop(pygame.sprite.Sprite):        # shield    
    def __init__(self):
        super().__init__()
        self.radius = ballrad
        self.rect = pygame.rect.Rect(randint(rect_state.left,rect_state.right-ballrad*2),
                                     randint(0,rect_state.bottom-ballrad*2),ballrad*2,ballrad*2)
        speed = 20
        direction = (randint(0,360)/360)*2*math.pi
        self.velocity = [math.sin(direction)*speed,math.cos(direction)*speed]
        self.disengage = 0
        self.engage = 0
        self.touch2 = False
        self.touch = False
        self.alpha = [0,0]

    def position(self):
        self.rect.centerx += self.velocity[0]
        self.rect.centery += self.velocity[1]
        if self.rect.bottom >= rect_state.bottom or self.rect.top <= rect_state.top: self.velocity[1] = -self.velocity[1]
        if self.rect.right >= rect_state.right or self.rect.left <= rect_state.left: self.velocity[0] = -self.velocity[0]

        pygame.draw.circle(screen,'#4287f5',self.rect.center,self.radius,10)

    def trigger(self):
        global shield
        if (pygame.sprite.spritecollide(self,right_hand,False)
        or pygame.sprite.spritecollide(self,left_hand,False)):
            shield = 150
            self.touch = True
    
    def appear(self):
        self.engage += 2
        if self.engage == 20: self.touch2 = True
        if self.engage < 32: self.alpha = [self.radius+10,200]
        if self.engage < 16: self.alpha = [self.radius+20,100]
        if self.engage < 8: self.alpha = [self.radius+30,50]
        draw_cir_alpha(screen,self.rect.centerx,self.rect.centery,self.alpha[0],(52, 235, 219,self.alpha[1]),10)

    def disapear(self):
        self.disengage += 2
        if self.disengage == 20: self.kill()
        if self.disengage < 18: self.alpha = [self.radius+30,10]
        if self.disengage < 12: self.alpha = [self.radius+20,100]
        if self.disengage < 6: self.alpha = [self.radius+10,200]

        draw_cir_alpha(screen,self.rect.centerx,self.rect.centery,self.alpha[0],(52, 235, 219,self.alpha[1]),10)

    def update(self):
        if self.touch:
            self.disapear()
        else:
            if self.touch2:
                self.position()
                self.trigger()
            if not self.touch2: self.appear()

class Cover(pygame.sprite.Sprite):          #behaviour of cover and information in it
    def __init__(self):
        super().__init__()
        self._layer = 1
        self.flip = True
        self.posy = 0
        self.posx = 0
        self.rect_main = pygame.Rect(-screen_width/3,0,screen_width/3,screen_height)
        self.shield_acti = pygame.image.load('graphics/shield icon.png').convert_alpha()
        self.shield_deac = pygame.image.load('graphics/shield icon2.png').convert_alpha()
        self.heart_acti = pygame.image.load('graphics/heart.png').convert_alpha()
        self.heart_deac = pygame.image.load('graphics/heart2.png').convert_alpha()
        self.shield_bar = pygame.image.load('graphics/shield bar.png').convert_alpha()
        self.main_cover = pygame.image.load('graphics/main cover.png').convert_alpha()
        
    def movement(self):
        if self.flip: self.rect_main.left = -self.rect_main.width #teleport to left
        if game_state == 3:
            self.flip = False
            if self.rect_main.left < 0: self.rect_main.left += 20 #move right if in left of screen
            if self.rect_main.left >= 0: self.rect_main.left = 0  #stay put
        if game_state == 2:
            if self.rect_main.width >= self.rect_main.right > 0: self.rect_main.left -= 20  #move left if in left of screen
            if self.rect_main.right <= 0: self.rect_main.left = screen_width                #teleport to the right when out of screen 
            if self.rect_main.right > screen_width: self.rect_main.left -= 20               #move left if in right of screen
            if screen_width-self.rect_main.width < self.rect_main.right < screen_width: self.rect_main.right = screen_width #stay put
        if game_state == 1:
            if self.rect_main.left < screen_width and self.rect_main.left>0: self.rect_main.left += 20 #move right if in right
            if self.rect_main.left >=screen_width: self.flip = True                                    
        self.posy = self.rect_main.top
        self.posx = self.rect_main.left

    def cover_score(self):
        box_text(screen,test_font,self.posx+40,self.posx+200,self.posy+130, 'Score',(255,255,255))
        box_text(screen,test_font,self.posx+45,self.posx+200,self.posy+176, f'{score}',(255,255,255))
        box_text(screen,test_font,self.posx+40,self.posx+200,self.posy+250, 'HighScore',(255,255,255))
        box_text(screen,test_font,self.posx+45,self.posx+200,self.posy+296, f'{highscore}',(255,255,255))

    def display(self):
        screen.blit(self.main_cover,self.rect_main)     #cover background

        pygame.draw.rect(screen,'grey',(self.posx+125,self.posy+430,264,28.7))          #shield indicator
        pygame.draw.rect(screen,'#4287f5',(self.posx+125,self.posy+430,(shield/150)*264,28.7))
        screen.blit(self.shield_bar,(self.posx+125,self.posy+430))
        if shield > 0: screen.blit(self.shield_acti,(self.posx+30,self.posy+420))
        else: screen.blit(self.shield_deac,(self.posx+30,self.posy+420))

        screen.blit(self.heart_acti,(self.posx+30,self.posy+525))           #health indicator
        if health == 2: screen.blit(self.heart_acti,(self.posx+130,self.posy+525))
        else: screen.blit(self.heart_deac,(self.posx+130,self.posy+525))

    def update(self):
        self.movement()
        self.display()
        self.cover_score()

class Countdown(pygame.sprite.Sprite):      #background counter
    def __init__(self):
        super().__init__()
        self.left = rect_state.centerx-240
        self.point = [self.left,rect_state.y+200]
        self.switch = False
        self.number = 30
    def moving(self):
        self.left = rect_state.centerx-240
        if game_state == 3: self.point = [self.left,rect_state.y+200]
        if self.point[0] < self.left: self.point[0] += (self.left-self.point[0])/30
        if self.point[0] > self.left: self.point[0] -= (self.point[0]-self.left)/30
        
    
    def display(self):
        if self.switch: 
            self.number -= 1
            if self.number == 0: self.switch = False
        else: 
            self.number = play_time()%30
            if self.number == 0: 
                self.switch = True
                self.number = 29
        
        # box_text(screen,test_font3,self.point[0],screen_width,self.point[1],"{:02d}".format(30-self.number),'grey')
        text_surf = test_font3.render("{:02d}".format(30-self.number), True, 'grey')
        text_surf.set_alpha(100)
        screen.blit(text_surf, (self.point[0], self.point[1]))

    def update(self):
        self.moving()
        if game_state > 0: self.display()

class optionbox(pygame.sprite.Sprite):
    def __init__(self,color, pos, name):
        super().__init__()
        self.color = color
        self.pos = pos
        self.name = name

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
        text1_surf = test_font.render(f'{self.name}',False,(64,64,64))
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

class optionbox1(optionbox):     #behaviour of play or continue box
    def __init__(self,color, pos, name):
        super().__init__(color, pos, name)

    def confirm(self):
        global game_state
        if self.hold_time == 30: game_state = -2
            
class optionbox2(optionbox):     #behaviour of quit box
    def __init__(self,color, pos, name):
        super().__init__(color, pos, name)

    def confirm(self):
        if self.hold_time == 30:
            pygame.quit()
            exit()

def collision_sprite():         #DETECT colision of hand and obstacle
    global health, shield
    if (pygame.sprite.groupcollide(left_hand,obstacle_group,False,True) 
        or pygame.sprite.groupcollide(right_hand,obstacle_group,False,True)):
        if shield == 0: 
            health -= 1
            heal_tile.add(healing_square())
        shield =0

    if health == 0: return True
    else: return False

def draw_rect_alpha(surface, color, rect, width):      #draw transparent rectangle
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect(),width)
    surface.blit(shape_surf, rect)

def draw_cir_alpha(surface,x,y,radius,coulor,width = 0):       #draw transparent circle
    shape_surf = pygame.Surface((radius*2,radius*2), pygame.SRCALPHA)
    pygame.draw.circle(shape_surf,(coulor[0],coulor[1],coulor[2],coulor[3]),(radius,radius),radius,width)
    surface.blit(shape_surf, (x-radius,y-radius))

def box_text(surface, font, x_start, x_end, y_start, text, colour):     #print text on screen 
        x = x_start
        y = y_start
        words = text.split(' ')
        word_a = font.render('a', True, colour)

        for word in words:
            if word == '/n':                        #/n to go down a line
                y += word_a.get_height() * 1.1
                x = x_start
                continue
            if word == '/s':                        #/s to space
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

def play_time():    #count time since the start of a new game
	current_time = int(pygame.time.get_ticks() / 1000) - start_time
	return current_time

def gamestate():                        #update game state
    global switch
    delta_time =  play_time() % 90            # -4: starting screen -3:losing screen -2:restart element   3:right hand
    if delta_time in (0 , 30 , 60) and switch:         #2:left hand     1:both hand
        obstacle_group.empty()
        switch = False

    if (delta_time in (1 , 31 , 61)) and switch == False: 
        switch = True
        if heal_tile: heal_tile.add(healing_square())
        if shield_tile: shield_tile.add(shield_drop())
        
    if delta_time <30:                 
        if delta_time == 0:
            left_hand.empty()
            if not right_hand: right_hand.add(righthand(1),righthand(2),righthand(3))
        return 3
    if delta_time <60:
        if delta_time == 30:
            right_hand.empty()
            if not left_hand: left_hand.add(leftthand(1),leftthand(2),leftthand(3))
        return 2
    if delta_time <90: 
        if delta_time ==60:
            if not right_hand: right_hand.add(righthand(1),righthand(2),righthand(3))
        return 1
    return 99

def mocap():        #tracking wrist location -> wrist coordinate
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
test_font2 = pygame.font.Font('font/Pixeltype.ttf', 150)
test_font3 = pygame.font.Font('font/Pixeltype.ttf', 800)
instruction = 'Instruction: /n /n 1.move your hand to control the ball /n 1.avoid the quare'

caution = pygame.image.load('graphics/caution block.png').convert_alpha()
game_icon = pygame.image.load('graphics/title.png').convert_alpha()
game_icon = pygame.transform.scale(game_icon,(430,400))

right_wrist_coords = [0,0]
health = 2
shield = 150
temp_shield = 150
left_wrist_coords = [0,0]


ballrad = 30
game_state = -4
score = 0
highscore = 0

obstacle_group = pygame.sprite.LayeredUpdates()
rect_state1 = pygame.Rect(0,0,screen_width,screen_height)
rect_state2 = pygame.Rect(0,0,screen_width*(2/3),screen_height)
rect_state3 = pygame.Rect(screen_width/3,0,screen_width*(2/3),screen_height)
rect_state = rect_state3
switch = True

option_box = pygame.sprite.Group()

left_hand = pygame.sprite.Group()

right_hand = pygame.sprite.Group()

info_board = pygame.sprite.LayeredUpdates()
info_board.add(Cover())

background = pygame.sprite.Group()
background.add(Countdown())

heal_tile = pygame.sprite.GroupSingle()
shield_tile = pygame.sprite.GroupSingle()

obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer,1500)

cap = cv2.VideoCapture(0) #cv2.CAP_DSHOW
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
                shield_tile.add(shield_drop())
        if event.type == obstacle_timer and game_state >= 0:
            if randint(0,5) == 0 and not shield_tile: shield_tile.add(shield_drop())
            if game_state == 3: rect_state = rect_state3
            if game_state == 2: rect_state = rect_state2
            if game_state == 1: rect_state = rect_state1
            if randint(0,1): obstacle_group.add(obstacle1(rect_state))
            elif randint(0,1): 
                obstacle_group.add(obstacle2(rect_state))
            else: 
                obstacle_group.add(obstacle2(rect_state))
                obstacle_group.add(obstacle2(rect_state))
            # obstacle_group.add(choice([obstacle2(rect_state),obstacle1(rect_state)]))

    if game_state >= 0:

        game_state = gamestate()
        background.update()
        obstacle_group.update()
        heal_tile.update()
        shield_tile.update() #test
        info_board.update()

        score = play_time()
        
        if collision_sprite(): 
            
            game_state = -3
        
    if game_state == -2:
        health = 2
        shield = 150
        obstacle_group.empty()
        start_time = int(pygame.time.get_ticks() / 1000)
        option_box.empty()
        game_state = 3

    if game_state == -3 or game_state == -4:
        if score > highscore: highscore = score
        if not right_hand: right_hand.add(righthand(1),righthand(2),righthand(3))
        if not left_hand: left_hand.add(leftthand(1),leftthand(2),leftthand(3))
        heal_tile.empty()
        option_box.update()

        if game_state == -3:
            if not option_box: 
                option_box.add(optionbox2('red',(screen_width*1/4,200),'QUIT'))
                option_box.add(optionbox1('green',(screen_width*3/4,200),'CONTINUE'))
            box_text(screen,test_font2,screen_width/2-220,screen_width,screen_height/5+20,'GAMEOVER','red')
            box_text(screen,test_font,screen_width*2/5,screen_width*3/5,screen_height/2,
                 f'Score: {score} /n Highscore: {highscore}',(64,64,64))

        if game_state == -4:
            screen.blit(game_icon,(screen_width/2-215,50))
            if not option_box: 
                option_box.add(optionbox2('red',(screen_width*1/4,200),'QUIT'))
                option_box.add(optionbox1('green',(screen_width*3/4,200),'PLAY'))
            box_text(screen,test_font,screen_width*2/6-50,screen_width*4/5,(screen_height/5)*3,instruction,'gray')

    right_hand.update()
    left_hand.update()

    # box_text(screen,test_font,200,500,50,f'{clock.get_fps()}','black')
    # box_text(screen,test_font,200,500,100,f'{temp_shield - shield}','black')
    # temp_shield = shield

    pygame.display.update()   
    clock.tick(60)