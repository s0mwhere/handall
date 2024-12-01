import pygame
import math
from sys import exit 
from random import randint, choice
import cv2
import mediapipe as mp
import pygame.gfxdraw
mp_pose = mp.solutions.pose

class hand(pygame.sprite.Sprite):
    def __init__(self,layer):
        super().__init__()
        self.layer = layer                  #assign hitbox type
        self.color = 'white'                #default color
        self.bluecir = [30,255]             #shield loss visual effect stat
        self.greencir = [120,0]             #health gain visual effect stat       
        self.redcir = [30,255]              #health loss visual effect stat

        self.temp_health = 2                # save the previuos instance of char stat for comparison
        self.temp_shield = shield
        
        if layer == 1: hitbox = 15          # the ball have 3 square hibox for "faking" a circle hitbox
        if layer == 2: hitbox = 40
        if layer == 3: hitbox = 55
        self.rect = pygame.Rect(0,0,hitbox,math.sqrt(ballrad*ballrad-hitbox*hitbox/4.0)*2)

    def position(self):
        self.rect.center = right_wrist_coords   #assign position of hand to character (would get overide later)
    
    def sfx(self):
        global health, shield           #up to date health and shield stat duh
        if self.layer == 1:             #only need to do it once
            if shield == 150: self.bluecir = [30,255]                           #reset the effect when shield is full
            if shield >= 0.3: shield -= 0.3                                     #reduce the shield overtime at rate 0.3/frame
            if self.temp_shield - shield > 0.58: shield += 0.3                  #for when there are 2 hand on screen
            if shield < 0.3:                             #execute the effect when shield loss
                if self.bluecir[1] >= 15:      #expand a blue circle while it color fade away
                    self.bluecir[0] += 5
                    self.bluecir[1] -= 15
                    draw_cir_alpha(screen,self.rect.centerx,self.rect.centery,self.bluecir[0],(52, 235, 219,self.bluecir[1]))
                shield = 0
            if health == 1 and self.redcir[1] >= 15:        #execute the effect when health reduce by 1 
                self.redcir[0] += 5             #expand a red circle while it color fade away
                self.redcir[1] -= 15
                draw_cir_alpha(screen,self.rect.centerx,self.rect.centery,self.redcir[0],(255, 0, 0,self.redcir[1]))
            if health == 2 and self.greencir[1] <= 255-20:      #execute the effect when health +1 
                self.greencir[0] -= 5           #implode a green circle while the color deepen
                self.greencir[1] += 15
                draw_cir_alpha(screen,self.rect.centerx,self.rect.centery,self.greencir[0],(0, 255, 0,self.greencir[1]))

            if self.temp_health < health: self.greencir = [120,0]   #reset the health gain effect
            if self.temp_health > health: self.redcir = [30,255]    #reset the health loss effect
            self.temp_health = health       #update the temp stat for comparison
            self.temp_shield = shield
            
    def display(self):          #display the ball (and it stat ring only while gameplay)
        global health, shield
        pygame.draw.circle(screen,'orange',self.rect.center,ballrad-5)      #background of shield ring
        pygame.draw.arc(screen,'#34ebdb',(self.rect.centerx-25,self.rect.centery-25,50,50),0,(shield/150)*2*math.pi,10) #shield ring
        pygame.draw.circle(screen,'grey',self.rect.center,ballrad-10)        #backgound of health ring
        pygame.draw.circle(screen,'green',self.rect.center,ballrad-10,0,-1+health,-1+health,1,1)     #health ring
        pygame.draw.circle(screen, self.color, self.rect.center,ballrad,5)      #the ball color for left right indication
        if game_state <= 0 :pygame.draw.circle(screen, self.color,self.rect.center,ballrad)

    def update(self):
        self.position()
        self.sfx()
        self.display()

class righthand(hand):    # position and color of right hand
    def __init__(self,layer):
        super().__init__(layer)
        self.color = 'blue'
    def position(self):
        self.rect.center = right_wrist_coords
        
class leftthand(hand):    #position and color of left hand
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

        if self.sides == 1:            #size and exact spawn position
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
        if self.sides == 1: self.rect.x += 30   #slide right
        if self.sides == 2: self.rect.y += 30   #slide down
        if self.sides == 3: self.rect.x -= 30   #slide left
        if self.sides == 4: self.rect.y -= 30   #slide up
        
        if (self.rect.x < -300 or self.rect.x > 1580
            or self.rect.y < -300 or self.rect.y > 1020): self.kill()    #delete when out of bound
        pygame.draw.rect(screen,'blue',self.rect)

    def update(self):
        self.prep_time -=30
        if self.prep_time < 1000: self.movement()   #move only when caution block fully show
        
class caution_block(pygame.sprite.Sprite):      #pre warn sign for sliding block
    def __init__(self, posit, width, height, prep_time):
        super().__init__()
        self._layer = 0     #display behind all object
        self.posit = posit  #position duh
        self.prep_time = prep_time
        self.alpha_rate = 0         #start out as invisible objects
        self.caution1 = pygame.transform.scale(caution,(width/3, height/3))     #3 different image cuz diff transparent state
        self.caution2 = pygame.transform.scale(caution,(width/3, height/3))     #so inefficient ahhhhhhhhhh
        self.caution3 = pygame.transform.scale(caution,(width/3, height/3))
        self.rect = (0,0,0,0)

    def appear(self):
        if self.prep_time >1000:    #caution sign appearing
            self.caution1.set_alpha(self.alpha_rate)
            self.caution2.set_alpha(-50+self.alpha_rate)
            self.caution3.set_alpha(-100+self.alpha_rate)
        else:                       #caution sign disappearing
            self.caution1.set_alpha(400 - self.alpha_rate)
            self.caution2.set_alpha(500 - self.alpha_rate)
            self.caution3.set_alpha(580 - self.alpha_rate)
        self.alpha_rate +=8     #transparency changing rate
        self.prep_time -=30     

        screen.blit(self.caution1,(self.posit[0],self.posit[1]))    #render the image
        screen.blit(self.caution2,(self.posit[2],self.posit[3]))
        screen.blit(self.caution3,(self.posit[4],self.posit[5]))
        
        if self.prep_time <= -100: self.kill()     #remove when done

    def update(self):
        self.appear()

class obstacle1(pygame.sprite.Sprite):      #behaviout of poping block
    def __init__(self,spawn_rect):
        super().__init__()
        self._layer = 2                         #display above the sliding block
        self.sprect = pygame.Rect(spawn_rect)   #get the playing field for accurate spawning
        self.engage = 0                         #counter for turning visible
        self.engage2 = 100                      #counter for flashing red
        self.color = pygame.Color(0,255,0,0)    #color red in hex form lol
        self.kill_time = 5                      #countdown till self destruct

        posx = randint(self.sprect.left, self.sprect.width - 50)    #randomly choose spawn location within play area
        posy = randint(self.sprect.top, self.sprect.bottom - 50)
        width = (randint(50, self.sprect.width - posx))//50*50          #randomly choose the size that not out of bound
        height = (randint(50, self.sprect.height - posy)//50)*50
        
        self.rect1 = pygame.Rect(posx, posy, width, height)        #rect for display
        self.rect = pygame.Rect(-100,-100,0,0)                     #rect for hitbox(spawn outside then put in later)
        self.w = self.rect1.width/2

    def collision(self):
        for event in event_list:
            if event.type == obstacle_timer:                       #counting down
                self.kill_time -= 1
            if self.kill_time == 5: self.color = pygame.Color('orange')     #start color
            # if self.kill_time == 4: self.color = pygame.Color('orange')
            if self.kill_time == 2: self.color = pygame.Color('red')        #final color (when hitbox is on)
        
        if self.engage <1500: #slowly make color visible
            self.engage +=50
            self.color.a = int((self.engage/1500)*255)      

        if self.kill_time <= 2: self.rect = self.rect1      #turn on hitbox
        if self.kill_time == 0: self.rect = (0,0,0,0)

    def display(self):
        if self.kill_time <=0:          #split in half when dissapear
            pygame.draw.rect(screen,'red',rect=(self.rect1.x, self.rect1.y, self.w, self.rect1.height))     #left half
            pygame.draw.rect(screen,'red',rect=(self.rect1.right - self.w, self.rect1.y, self.w, self.rect1.height))    #right half
            self.w -= 30    #turn to nothing rate
            if self.w <= 0: self.kill()     #when there are no width, self destruct

        if self.kill_time >0:           #full square when collision is on
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
        self.pos = (randint(rect_state.x,rect_state.x+rect_state.width-300),randint(0, rect_state.bottom-300))  #random spawn location
        self.healpng = pygame.image.load('graphics/heal square.png').convert_alpha()    #import object visual
        
        self.rect = pygame.Rect(-200,-200,300,300)      #bounding square
        self.rect2 = pygame.Rect(-200,-200,200,200)     #inner progress circle
        self.rect.topleft = self.pos                    #put circle in middle of the square 

        self.hold_time = 0          #duration when hand in heal square
        self.base_time = 3          #require duration for heal

    def trigger(self):
        if (pygame.sprite.spritecollide(self,right_hand,False)
        or pygame.sprite.spritecollide(self,left_hand,False)):  #detect collision
            self.hold_time += 0.03
        elif(self.hold_time > 0.03): self.hold_time -= 0.03     #when hand in square increase hold time
        elif(self.hold_time <= 0.03): self.hold_time = 0        #decrease when hand out till it is 0
        
    def animation(self):    #render the countdown number inside circle and the progress circle
        test_font2 = pygame.font.Font('font/Pixeltype.ttf', 70)
        text1_surf = test_font2.render("{:.1f}".format(self.base_time-self.hold_time),False,(64,64,64))
        text1_rect = text1_surf.get_rect(center = self.rect.center)
        screen.blit(text1_surf,text1_rect)
        
        self.rect2.center = self.rect.center
        screen.blit(self.healpng,self.rect)
        pygame.draw.arc(screen, 'green', self.rect2, 0, (self.hold_time/self.base_time)*2*math.pi,15)

    def confirm(self):      #when hold long enough health +1 then self destruct
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
        self.radius = ballrad       #have same size as the character
        self.rect = pygame.rect.Rect(randint(rect_state.left,rect_state.right-ballrad*2),
                                     randint(0,rect_state.bottom-ballrad*2),ballrad*2,ballrad*2)    #random spawn location
        speed = 20      #speed of movement duh
        direction = (randint(0,360)/360)*2*math.pi  #random start location
        self.velocity = [math.sin(direction)*speed,math.cos(direction)*speed]   #velocity vector
        self.disengage = 0          #for spawn effect
        self.engage = 0             #for despawn effect
        self.touch2 = False         #weither the spawn animation done or not
        self.touch = False          #weither the player touch it
        self.alpha = [0,0]          #[radius, transparent stat]

    def position(self):     #bound when hit wall and change position according to velocity vector
        self.rect.centerx += self.velocity[0]
        self.rect.centery += self.velocity[1]
        if self.rect.bottom >= rect_state.bottom or self.rect.top <= rect_state.top: self.velocity[1] = -self.velocity[1]   
        if self.rect.right >= rect_state.right or self.rect.left <= rect_state.left: self.velocity[0] = -self.velocity[0]

        pygame.draw.circle(screen,'#4287f5',self.rect.center,self.radius,10)

    def trigger(self):      #when touch gain shield and start despawn animation
        global shield
        if (pygame.sprite.spritecollide(self,right_hand,False)
        or pygame.sprite.spritecollide(self,left_hand,False)):
            shield = 150
            self.touch = True
    
    def appear(self):       #spawn animation
        self.engage += 2
        if self.engage == 20: self.touch2 = True
        if self.engage < 32: self.alpha = [self.radius+10,200]
        if self.engage < 16: self.alpha = [self.radius+20,100]
        if self.engage < 8: self.alpha = [self.radius+30,50]
        draw_cir_alpha(screen,self.rect.centerx,self.rect.centery,self.alpha[0],(52, 235, 219,self.alpha[1]),10)

    def disapear(self):     #despawn animation and self destruct
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
        self.flip = True    #for changing side from gamestate 3 to 2
        self.posy = 0       #top left corner of the cover(act as spawn anchor for object on the cover)
        self.posx = 0
        self.rect_main = pygame.Rect(-screen_width/3,0,screen_width/3,screen_height)    #cover size and initial position
        self.shield_acti = pygame.image.load('graphics/shield icon.png').convert_alpha()    #various graphic objects
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

    def cover_score(self):      #score and highscore display
        box_text(screen,test_font,self.posx+40,self.posx+200,self.posy+130, 'Score',(255,255,255))
        box_text(screen,test_font,self.posx+45,self.posx+200,self.posy+176, f'{score}',(255,255,255))
        box_text(screen,test_font,self.posx+40,self.posx+200,self.posy+250, 'HighScore',(255,255,255))
        box_text(screen,test_font,self.posx+45,self.posx+200,self.posy+296, f'{highscore}',(255,255,255))

    def display(self):
        screen.blit(self.main_cover,self.rect_main)     #cover background
        #shield indicator
        pygame.draw.rect(screen,'grey',(self.posx+125,self.posy+430,264,28.7))          
        pygame.draw.rect(screen,'#4287f5',(self.posx+125,self.posy+430,(shield/150)*264,28.7))  #shield bar
        screen.blit(self.shield_bar,(self.posx+125,self.posy+430))                              #shield bar frame
        if shield > 0: screen.blit(self.shield_acti,(self.posx+30,self.posy+420))     #blue shield when hav shield
        else: screen.blit(self.shield_deac,(self.posx+30,self.posy+420))              #grey shield when none

        screen.blit(self.heart_acti,(self.posx+30,self.posy+525))           #health indicator
        if health == 2: screen.blit(self.heart_acti,(self.posx+130,self.posy+525))      #same as shield
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
        self.switch = False     #when countdown reach 0
        self.number = 30        #initial number (same as game state interval)
    def moving(self):
        self.left = rect_state.centerx-240  #position middle of play field
        if game_state == 3: self.point = [self.left,rect_state.y+200]       #reset position every new game
        if self.point[0] < self.left: self.point[0] += (self.left-self.point[0])/30       #slide to middle
        if self.point[0] > self.left: self.point[0] -= (self.point[0]-self.left)/30
        
    
    def display(self):
        if self.switch:     #increase number when reach 0 (a fancy way of reseting)
            self.number -= 1
            if self.number == 0: self.switch = False  #switch to normal countdown when reach max number
        else: 
            self.number = play_time()%30    #countdown 
            if self.number == 0:            #when reach 0 start the fancy reset
                self.switch = True
                self.number = 29
        
        text_surf = test_font3.render("{:02d}".format(30-self.number), True, 'grey')
        text_surf.set_alpha(100)        #make the text transparent to lessen the distraction
        screen.blit(text_surf, (self.point[0], self.point[1]))

    def update(self):
        self.moving()
        if game_state > 0: self.display()   #only show while gameplay

class optionbox(pygame.sprite.Sprite):      #do something when hold for 30 frame
    def __init__(self,color, pos, name):
        super().__init__()
        self.color = color  #color of the box
        self.pos = pos      #spawn location
        self.name = name    #title ontop of the square

        self.rect = pygame.Rect(-200,-200,100,100)      #hit box
        self.rect2 = pygame.Rect(-200,-200,100,100)     #filing square (purely visual)
        
        self.hold_time = 0

    def trigger(self):
        self.rect.center = self.pos     #put hitbox in spawn location
        if (pygame.sprite.spritecollide(self,right_hand,False)
        or pygame.sprite.spritecollide(self,left_hand,False)):  #when touch increase timer and vice versa
            self.hold_time += 1
        elif(self.hold_time > 0): self.hold_time -= 1

    def animation(self):
        text1_surf = test_font.render(f'{self.name}',False,(64,64,64))      #render title
        text1_rect = text1_surf.get_rect(center = (self.rect.centerx,self.rect.top-20))
        screen.blit(text1_surf,text1_rect)
        
        self.rect2.height = (self.hold_time/30)*100         #render inner filling
        self.rect2.bottomleft = self.rect.bottomleft
        pygame.draw.rect(screen,self.color,self.rect,2)
        pygame.draw.rect(screen,self.color,self.rect2)

    def confirm(self):
        if self.hold_time == 30:    #turn off the game (get overide later)
            pygame.quit()
            exit()

    def update(self):
        self.trigger() 
        self.animation()
        self.confirm()

class optionbox1(optionbox):     #behaviour of play or continue box
    def __init__(self,color, pos, name):
        super().__init__(color, pos, name)

    def confirm(self):          #change game state to initiate state
        global game_state
        if self.hold_time == 30: game_state = -2
            
class optionbox2(optionbox):     #behaviour of quit box
    def __init__(self,color, pos, name):
        super().__init__(color, pos, name)

    def confirm(self):          #close the game
        if self.hold_time == 30:
            pygame.quit()
            exit()

def collision_sprite():         #DETECT colision of hand and obstacle
    global health, shield
    if (pygame.sprite.groupcollide(left_hand,obstacle_group,False,True) 
        or pygame.sprite.groupcollide(right_hand,obstacle_group,False,True)):
        if shield == 0:                         #dont have shield -> reduce health
            health -= 1
            heal_tile.add(healing_square())     
        shield =0                               #have shield -> shield reduce to 0

    if health == 0: return True                 #no health -> return true(die)
    else: return False

def draw_rect_alpha(surface, color, rect, width):      #draw transparent rectangle
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)        #the default surface cant handle transparency
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect(),width)            #so we have to render it on another surface
    surface.blit(shape_surf, rect)

def draw_cir_alpha(surface,x,y,radius,coulor,width = 0):       #draw transparent circle
    shape_surf = pygame.Surface((radius*2,radius*2), pygame.SRCALPHA)           #same as draw_rec_alpha
    pygame.draw.circle(shape_surf,(coulor[0],coulor[1],coulor[2],coulor[3]),(radius,radius),radius,width) #if not given width, it auto fill
    surface.blit(shape_surf, (x-radius,y-radius))

def box_text(surface, font, x_start, x_end, y_start, text, colour):     #print text on screen 
        x = x_start         #text box bounding
        y = y_start
        words = text.split(' ')     #take individual word seperate by a space
        word_a = font.render('a', True, colour)         #a place holder for spacing between word and line

        for word in words:
            if word == '/n':                        #/n to go down a line
                y += word_a.get_height() * 1.1
                x = x_start
                continue
            if word == '/s':                        #/s to space
                x += word_a.get_width() * 1.1
                continue

            word_t = font.render(word, True, colour)    #if reach the bound of text box move down a line and continue
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

    if (delta_time in (1 , 31 , 61)) and switch == False:   #if there is an existing power up spawn it again (for fairness sake)
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

    # To improve performance, mark the image as not writeable to
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

pygame.init()       #initiate pygame
screen_height =720
screen_width =1280
screen = pygame.display.set_mode((screen_width,screen_height))  #open the interface
pygame.display.set_caption("lmao")                              #name of interface window
clock = pygame.time.Clock()

start_time = 0
test_font = pygame.font.Font('font/Pixeltype.ttf', 50)          #different font sizes
test_font2 = pygame.font.Font('font/Pixeltype.ttf', 150)
test_font3 = pygame.font.Font('font/Pixeltype.ttf', 800)
instruction = 'Instruction: /n /n 1.move your hand to control the ball /n 1.avoid the quare'    #open screen intruction

caution = pygame.image.load('graphics/caution block.png').convert_alpha()
game_icon = pygame.image.load('graphics/title.png').convert_alpha()             #the game logo
game_icon = pygame.transform.scale(game_icon,(430,400))

right_wrist_coords = [0,0]          #initial character position
left_wrist_coords = [0,0]
health = 2                          #initial health
shield = 150                        #initial shield
temp_shield = 150

ballrad = 30                        #character size
game_state = -4 #-4                 #initial game state
score = 0
highscore = 0

obstacle_group = pygame.sprite.LayeredUpdates()
rect_state1 = pygame.Rect(0,0,screen_width,screen_height)                   #different playing field
rect_state2 = pygame.Rect(0,0,screen_width*(2/3),screen_height)
rect_state3 = pygame.Rect(screen_width/3,0,screen_width*(2/3),screen_height)
rect_state = rect_state3
switch = True

#initiate group for object(a pygame feature, help with reducing the pain)
option_box = pygame.sprite.Group()

left_hand = pygame.sprite.Group()

right_hand = pygame.sprite.Group()

info_board = pygame.sprite.LayeredUpdates()
info_board.add(Cover())

background = pygame.sprite.GroupSingle()
background.add(Countdown())

heal_tile = pygame.sprite.GroupSingle()
shield_tile = pygame.sprite.GroupSingle()

obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer,1500)  #spawining interval one time per 1500 frame

cap = cv2.VideoCapture(0)                       #motion capture range and suffixes
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
pose = mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        smooth_landmarks=True) 

while True:
    mocap()                             #update hand position
    screen.fill('white')                #refresh interface every frame
    event_list = pygame.event.get()

    for event in event_list:
        if event.type == pygame.QUIT:   #for quitting by pressing the X button
            pygame.quit()
            cap.release()
            exit()
        if event.type == pygame.KEYDOWN: #use for testing, ignore it
            if event.key == pygame.K_m:
                pass
        if event.type == obstacle_timer and game_state >= 0:
            if randint(0,5) == 0 and not shield_tile: shield_tile.add(shield_drop())    #shield spawn only when shield = 0
            if game_state == 3: rect_state = rect_state3                                #change the playing field
            if game_state == 2: rect_state = rect_state2
            if game_state == 1: rect_state = rect_state1
            if randint(0,1): obstacle_group.add(obstacle1(rect_state))          #spawn the obstacle
            elif randint(0,1): 
                obstacle_group.add(obstacle2(rect_state))
            else: 
                obstacle_group.add(obstacle2(rect_state))
                obstacle_group.add(obstacle2(rect_state))

    if game_state >= 0:     #when is playing

        game_state = gamestate()    #is there a better way to update? yes, will I? No
        background.update()
        obstacle_group.update()
        heal_tile.update()
        shield_tile.update()
        info_board.update()
        score = play_time()
        
        if collision_sprite(): #switch to death screen when die
            game_state = -3
        
    if game_state == -2:    #initiate state when start a new game
        health = 2
        shield = 150
        obstacle_group.empty()
        start_time = int(pygame.time.get_ticks() / 1000)
        option_box.empty()
        game_state = 3

    if game_state == -3 or game_state == -4:
        if score > highscore: highscore = score     #update highscore
        if not right_hand: right_hand.add(righthand(1),righthand(2),righthand(3))
        if not left_hand: left_hand.add(leftthand(1),leftthand(2),leftthand(3))
        heal_tile.empty()
        option_box.update()

        if game_state == -3:    #death screen
            if not option_box: 
                option_box.add(optionbox2('red',(screen_width*1/4,200),'QUIT'))
                option_box.add(optionbox1('green',(screen_width*3/4,200),'CONTINUE'))
            box_text(screen,test_font2,screen_width/2-220,screen_width,screen_height/5+20,'GAMEOVER','red')
            box_text(screen,test_font,screen_width*2/5,screen_width*3/5,screen_height/2,
                 f'Score: {score} /n Highscore: {highscore}',(64,64,64))

        if game_state == -4:    #entry screen
            screen.blit(game_icon,(screen_width/2-215,50))
            if not option_box: 
                option_box.add(optionbox2('red',(screen_width*1/4,200),'QUIT'))
                option_box.add(optionbox1('green',(screen_width*3/4,200),'PLAY'))
            box_text(screen,test_font,screen_width*2/6-50,screen_width*4/5,(screen_height/5)*3,instruction,'gray')

    right_hand.update()
    left_hand.update()

    # box_text(screen,test_font,600,800,50,f'game state: {game_state}','black')
    # box_text(screen,test_font,200,500,100,f'{temp_shield - shield}','black')
    # temp_shield = shield

    pygame.display.update()   
    clock.tick(60)          #limit the fps