import sys
import pygame
from pygame.locals import *
import random
import math
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="PIL")

pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 900

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")
pygame.display.set_icon(pygame.image.load("favicon.ico"))

global birdskin
birdskin = "default"

# GAME SOUNDS
death_sound = pygame.mixer.Sound('sounds/death.mp3')
death_sound_played = False
point_sfx = pygame.mixer.Sound('sounds/point.wav')
point_sfx.set_volume(0.3)
flap_sound = pygame.mixer.Sound('sounds/wing.wav')

#define font
font = pygame.font.Font('04B_19__.ttf', 60)

#color
white = (255, 255, 255)
black = (0, 0, 0)

# Fade variables
fade_alpha = 0
fade_speed = 5
fade_direction = 1  # 1 for fading in, -1 for fading out

START_SCREEN = 0
PLAYING = 1
GAME_OVER = 2
PAUSED = 3
SHOP = 4


multiplier_button_cooldown = 500  # Cooldown time in milliseconds (adjust as needed)
last_multiplier_activation_time = pygame.time.get_ticks()
current_multiplier_price = 50  # Initial price


game_paused = False
current_state = START_SCREEN


#click image
click_img = pygame.image.load("img/click.png")  # Load the click image
click_rect = click_img.get_rect(center=(screen_width // 2, screen_height // 2 - 650))
click_x = screen_width // 2 - click_rect.width // 2
click_y = 550
click_speed = 0.75






#game variables
player_coins = 0
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_freq = 1500 #millisec
last_pipe = pygame.time.get_ticks() - pipe_freq
score = 0
pass_pipe = False


#load images
coin_img = pygame.image.load('img/coin.png')
bgnew = pygame.image.load("img/start_screen1.jpg")


pointsound = False




# Load pause button image
pause_button_img = pygame.image.load("img/pause_btn.png")
pause_button_rect = pause_button_img.get_rect()
pause_button_rect.topleft = (screen_width - pause_button_rect.width - 10, 10)

resume_countdown_time = 0  # 3000 milliseconds (3 seconds)
resume_countdown_start_time = 0
resume_countdown_active = False


bg = pygame.image.load("img/bg.png")
ground_img = pygame.image.load("img/ground.png")





#SKINS

selected_skin = "default"

global aqua_skin_enabled

aqua_skin_price = 500




space_key_pressed = False
mouse_button_pressed_prev_frame = False


player_coins = 0
try:
    with open("player_coins.txt", 'r') as file:
        player_coins = int(file.read())
except FileNotFoundError:
    pass

best_score = 0
try:
    with open("best_score.txt", "r") as file:
        best_score = int(file.read())
except FileNotFoundError:
    pass

coins_multiplier = 0.3
try:
    with open("coins_multiplier.txt", "r") as file:
        coins_multiplier = float(file.read())
except FileNotFoundError:
    pass




def update_aqua_skin_bought():
    with open("aqua_skin_bought.txt", "r") as file:
        global aqua_skin_bought
        aqua_skin_bought = file.read()




def draw_text_with_outline(text, font, text_col, outline_col, x, y, outline_thickness):
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                outline = font.render(text, True, outline_col)
                outline_rect = outline.get_rect()
                outline_rect.topleft = (x + dx * outline_thickness, y + dy * outline_thickness)
                screen.blit(outline, outline_rect)

    text_surface = font.render(text, True, text_col)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)


def draw_best_score_with_outline(score_text, font, text_col, outline_col, x, y, outline_thickness):
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                outline = font.render(score_text, True, outline_col)
                outline_rect = outline.get_rect()
                outline_rect.topleft = (x + dx * outline_thickness, y + dy * outline_thickness)
                screen.blit(outline, outline_rect)

    text_surface = font.render(score_text, True, text_col)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score



def update_bird_skin(bird, new_skin):
    bird.images = []  # Clear existing images
    bird.skin = new_skin
    bird.initialize_images()
    bird.image = bird.images[bird.index]



class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, skin):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        self.skin = skin
        self.initialize_images()

        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def initialize_images(self):
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}_{self.skin}.png')
            self.images.append(img)

    def update(self):
        global flying

        if flying or game_over:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if game_over:
            self.image = pygame.transform.rotate(self.images[self.index], -90)
        else:
            if not pause_button_rect.collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                    self.clicked = True
                    flying = True
                    self.vel = -8.7
                    flap_sound.play()
                    global player_coins

                if pygame.mouse.get_pressed()[0] == 0:
                    self.clicked = False

                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE] and not space_key_pressed:
                    space_key_pressed = True
                    flying = True
                    flappy.vel = -8.7
                    flap_sound.play()

                if not keys[pygame.K_SPACE]:
                    space_key_pressed = False

                self.counter += 1
                flap_cooldown = 5

                if self.counter > flap_cooldown:
                    self.counter = 0
                    self.index += 1
                    if self.index >= len(self.images):
                        self.index = 0
                self.image = self.images[self.index]

                self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2.7)


        



#pipe
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipee.png')
        self.rect = self.image.get_rect()
        # position 1 is top, -1 is bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]



    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()






class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        action = False

        #get mouse pos
        pos = pygame.mouse.get_pos()

        #check if mouse if over button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action



class SlideInImage(pygame.sprite.Sprite):
    def __init__(self, image_path, final_position, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height + 100))  # Initial position below the screen
        self.final_position = final_position
        self.speed = speed

    def update(self):
        if self.rect.centery > self.final_position[1]:
            self.rect.centery -= self.speed


class FloatingText(pygame.sprite.Sprite):
    def __init__(self, x, y, text, font, color, outline_color, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        text_surface = font.render(text, True, color)
        outline_surface = font.render(text, True, outline_color)
        self.image = pygame.Surface((text_surface.get_width() + 4, text_surface.get_height() + 4), pygame.SRCALPHA)
        self.image.blit(outline_surface, (2, 2))
        self.image.blit(text_surface, (2, 2))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = speed

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < -20:
            self.kill()

floating_texts = pygame.sprite.Group()



class ConfirmButton():
    def __init__(self, x, y, image, text, font, outline_color, action):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.text = text
        self.font = font
        self.outline_color = outline_color
        self.action = action

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        screen.blit(self.image, (self.rect.x, self.rect.y))
        draw_text_with_outline(self.text, self.font, white, self.outline_color, self.rect.x + 10, self.rect.y + 10, outline_thickness=2)

        return action


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        # Load the coin image and scale it down by a factor (e.g., 0.5 for half the size)
        coin_image = pygame.image.load('img/coin.png')
        scale_factor = 0.8
        self.image = pygame.transform.scale(coin_image, (int(coin_image.get_width() * scale_factor), int(coin_image.get_height() * scale_factor)))
        self.rect = self.image.get_rect()
        
        # Initial position
        self.start_y = y - 15
        self.rect.center = [x, y]
        
        # Parameters for smooth oscillation
        self.amplitude = 10  # Amplitude of the oscillation
        self.frequency = 0.07  # Frequency of the oscillation (adjust as needed)
        self.time = 0

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

        # Smooth oscillation motion
        self.time += 1
        displacement = self.amplitude * math.sin(self.frequency * self.time)
        self.rect.y = self.start_y + displacement

coin_group = pygame.sprite.Group()


bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()


flappy = Bird(100, int(screen_height / 2), birdskin)

bird_group.add(flappy)

#create restart button instance



p_key_pressed = False



run = True
while run:

    clock.tick(fps)
    



   # STARTSCREEN
    if current_state == START_SCREEN:
        flappy.vel = 0
        flying = False
        events = pygame.event.get()
        # Check for mouse click or space key press to transition to PLAYING
        if any(e.type == pygame.MOUSEBUTTONDOWN or
            (e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE) for e in events):
            current_state = 1

        # background
        screen.blit(bg, (0, 0))

        # Draw the bird on the start screen
        bird_group.draw(screen)
        bird_group.update()

        # Draw ground
        screen.blit(ground_img, (ground_scroll, 768))

        # Load and display the "get_ready" image in the center of the screen
        get_ready_img = pygame.image.load("img/get_ready.png")
        get_ready_rect = get_ready_img.get_rect(center=(screen_width // 2, screen_height // 2 - 200))
        screen.blit(get_ready_img, get_ready_rect)

        # Load and display the "start_icons" image
        start_icons_img = pygame.image.load("img/start_icons.png")
        start_icons_rect = start_icons_img.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(start_icons_img, (0, 80))

        


        # Draw the click image with smooth up and down motion
        click_y += click_speed * math.sin(pygame.time.get_ticks() * 0.0046) 
        screen.blit(click_img, (click_x, click_y))

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pygame.display.flip()

        

        
    # PLAYING
    elif current_state == PLAYING:
        #background
        screen.blit(bg, (0,0))
        
        
        pipe_group.draw(screen)
        bird_group.draw(screen)
        bird_group.update()
        

        #draw ground
        screen.blit(ground_img, (ground_scroll, 768))
        

        #check score
        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
                and pass_pipe == False:
                pass_pipe = True  
            if pass_pipe == True:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    score += 1
                    pass_pipe = False



        # Draw static coin image in the top left corner
        
        
        

        # Check for coin collisions
        coin_collisions = pygame.sprite.spritecollide(flappy, coin_group, True)
        if coin_collisions:
            player_coins += len(coin_collisions)
            point_sfx.play()
            
            



        
        draw_text_with_outline(str(score), font, white, black, 285, 20, outline_thickness=4)
        



        #look for collision
        
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True
            
        coin_collisions = pygame.sprite.spritecollide(flappy, coin_group, True)
        if coin_collisions:
            player_coins += len(coin_collisions)
            point_sfx.play()
            
            

        #check if game is over
        if flappy.rect.bottom >= 768:
            game_over = True
            flying = False
            current_state = GAME_OVER
            
            
        
        
        if game_over == True:
            if not death_sound_played:
                death_sound.play()
                death_sound_played = True
            if flappy.rect.bottom < 768:
                flappy.vel += 0.5
                flappy.rect.y += int(flappy.vel)
                

                


        if game_over == False and flying == True and not game_paused:
            # gen new pipes
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_freq:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(screen_width, int(screen_height/2) + pipe_height, -1)
                top_pipe = Pipe(screen_width, int(screen_height/2) + pipe_height, 1)

                # 30% chance to spawn coins
                if random.random() < coins_multiplier:
                    coin_y = int(screen_height / 2) + pipe_height
                    coin = Coin(screen_width + 40, coin_y)
                    coin_group.add(coin)

                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now


            #ground and scrolling the ground
            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0

            pipe_group.update()
            coin_group.update()
            coin_group.draw(screen)

            

        #check for game over and reset
        if game_over == True:
            with open("player_coins.txt", "w") as file:
                file.write(str(player_coins))
            # Check if the current score is greater than the best score
            if score > best_score:
                best_score = score
                # Save the new best score to the file
                with open("best_score.txt", "w") as file:
                    file.write(str(best_score))
            
            #draw_best_score_with_outline(f"Best: {best_score}", font, white, black, 20, 860, outline_thickness=4)



        
        if not game_over:
            screen.blit(pause_button_img, pause_button_rect.topleft)


            # Check if the pause button is clicked
            mouse_pos = pygame.mouse.get_pos()
            mouse_button_pressed = pygame.mouse.get_pressed()[0]

            if pause_button_rect.collidepoint(mouse_pos) and mouse_button_pressed and not mouse_button_pressed_prev_frame:
                current_state = PAUSED
                resume_countdown_active = False  # Reset countdown if paused
                

            # Update the previous frame's mouse button state
            mouse_button_pressed_prev_frame = mouse_button_pressed

            keys = pygame.key.get_pressed()
            if keys[pygame.K_p] and not p_key_pressed:
                current_state = PAUSED
                game_paused = True
                p_key_pressed = True
            elif not keys[pygame.K_p]:
                p_key_pressed = False

    elif current_state == PAUSED:
        game_paused = True
        # Display a pause message


        mouse_pos = pygame.mouse.get_pos()
        mouse_button_pressed = pygame.mouse.get_pressed()[0]

        if pause_button_rect.collidepoint(mouse_pos) and mouse_button_pressed and not mouse_button_pressed_prev_frame:
            if not resume_countdown_active:  # Only start countdown if it's not already active
                resume_countdown_start_time = pygame.time.get_ticks()
                resume_countdown_active = True

        # Update the previous frame's mouse button state
        mouse_button_pressed_prev_frame = mouse_button_pressed

        # Check if 'P' key is pressed again to resume the game
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p] and not p_key_pressed:
            if not resume_countdown_active:  # Only start countdown if it's not already active
                resume_countdown_start_time = pygame.time.get_ticks()
                resume_countdown_active = True
            p_key_pressed = True
        elif not keys[pygame.K_p]:
            p_key_pressed = False

        # Start or continue the countdown if the game is paused and the countdown is active
        if game_paused and resume_countdown_active:
            # Display the countdown on the screen
            


            # Check if the countdown has finished
            if pygame.time.get_ticks() - resume_countdown_start_time >= resume_countdown_time:
                current_state = PLAYING
                
                resume_countdown_active = False  # Reset countdown when resuming
                game_paused = False
                

    elif current_state == GAME_OVER:
        screen.blit(bg, (0,0))
        
        bird_group.draw(screen)
        pipe_group.draw(screen)


        screen.blit(ground_img, (ground_scroll, 768))
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 0:
            ground_scroll = 0

        

        ok_btn = pygame.image.load("img/ok_button.png")
        ok_btn_rect = ok_btn.get_rect(center=(screen_width / 2 - 136, screen_height / 2 + 200))

        shop_button = pygame.image.load("img/shop_button.png")
        shop_button_rect = shop_button.get_rect(center=(screen_width / 2 + 137, screen_height / 2 + 200 ))

        score_message_img = pygame.image.load("img/score_message.png")
        score_message_rect = score_message_img.get_rect(center=(screen_width // 2, screen_height // 2 ))

        game_over_img = pygame.image.load("img/game_over.png")
        game_over_rect = game_over_img.get_rect(center=(screen_width // 2, screen_height // 2 - 210 ))
        
        screen.blit(ok_btn, ok_btn_rect)
        screen.blit(shop_button, shop_button_rect)
        screen.blit(score_message_img, score_message_rect)
        screen.blit(game_over_img, game_over_rect)

        
        
        draw_text_with_outline(str(score), pygame.font.Font('04B_19__.ttf', 50), white, black, 469, 395, outline_thickness=4)
        draw_text_with_outline(str(best_score), pygame.font.Font('04B_19__.ttf', 50), white, black, 469, 482, outline_thickness=4)


        # Check for button clicks
        mouse_pos = pygame.mouse.get_pos()
        mouse_button_pressed = pygame.mouse.get_pressed()[0]

        if ok_btn_rect.collidepoint(mouse_pos) and mouse_button_pressed and not mouse_button_pressed_prev_frame:
            score = reset_game()
            death_sound_played = False
            game_over = False
            current_state = START_SCREEN
            flying = False  # Set flying to False when OK button is clicked

        # Update the previous frame button state
        mouse_button_pressed_prev_frame = mouse_button_pressed
            
        # Check for button clicks
        mouse_pos = pygame.mouse.get_pos()
        mouse_button_pressed = pygame.mouse.get_pressed()[0]

        if shop_button_rect.collidepoint(mouse_pos) and mouse_button_pressed:
            current_state = SHOP

        mouse_button_pressed_prev_frame = mouse_button_pressed



    
        
        # Update the display
        pygame.display.flip()
    
    elif current_state == SHOP:
        screen.blit(bg, (0, 0))
        ground_scroll = 0
        screen.blit(ground_img, (ground_scroll, 768))
        
        # Display the number of coins
        screen.blit(coin_img, (10, 830))
        draw_text_with_outline(f"{player_coins}", font, white, black, 70, 830, outline_thickness=4)

        shop_ui_img = pygame.image.load("img/shop_ui.png")
        
        screen.blit(shop_ui_img, (44,21))
        
        ok_btn = pygame.image.load("img/ok_button.png")
        ok_btn_rect = ok_btn.get_rect(center=(screen_width / 2, screen_height - 175))

        selected_img = pygame.image.load("img/selected.png")

        aqua_skin_img = pygame.image.load("img/bird1_aqua.png")
        aqua_skin_rect = aqua_skin_img.get_rect(topleft=(189, 350))
        
        default_skin_img = pygame.image.load("img/bird1_default.png")
        default_skin_rect = default_skin_img.get_rect(topleft=(89,350))

        multiplier_button_img = pygame.image.load("img/coin.png")
        multiplier_button_rect = multiplier_button_img.get_rect(topleft=(89, 150))

        screen.blit(default_skin_img, (89, 350))
        screen.blit(aqua_skin_img, (189, 350))
        screen.blit(multiplier_button_img, (89, 150))

        screen.blit(ok_btn, ok_btn_rect)

        

        # Check for button clicks
        mouse_pos = pygame.mouse.get_pos()
        mouse_button_pressed = pygame.mouse.get_pressed()[0]

        if ok_btn_rect.collidepoint(mouse_pos) and mouse_button_pressed:
            score = reset_game()
            death_sound_played = False
            game_over = False
            current_state = START_SCREEN
            flying = False  # Set flying to False when OK button is clicked

        # Update the previous frame button state
        mouse_pos = pygame.mouse.get_pos()
        mouse_button_pressed = pygame.mouse.get_pressed()[0]

        if multiplier_button_rect.collidepoint(mouse_pos) and mouse_button_pressed:
            current_time = pygame.time.get_ticks()

            # Check if the button cooldown has elapsed
            if current_time - last_multiplier_activation_time >= multiplier_button_cooldown:
                # Check if the player has enough coins
                if player_coins >= current_multiplier_price:
                    # Deduct coins
                    

                    # Increase the coin spawn rate by 10%
                    if coins_multiplier < 1:
                        player_coins -= current_multiplier_price
                        coins_multiplier += 0.05
                        # Increase the price by 15%
                        current_multiplier_price = int(current_multiplier_price * 1.15)

                        with open("coins_multiplier.txt", "w") as file:
                            file.write(str(coins_multiplier))

                        # Update the last activation time
                        last_multiplier_activation_time = current_time

                        # Print a message indicating the successful purchase
                        print(f"Multiplier activated! Coin spawn rate increased and is now {coins_multiplier}.")
                    else:
                        print("Maximum coin multiplier reached")
                    

                    

                else:
                    # Print a message if the player doesn't have enough coins
                    print("Not enough coins to activate the multiplier!")



        
        if selected_skin == "default":
            screen.blit(selected_img, (89 - 5, 350))
        elif selected_skin == "aqua":
            screen.blit(selected_img, (185, 350))
        
        purchase_button_img = pygame.image.load("img/purchase_button.png")
        purchase_button_rect = purchase_button_img.get_rect(center=(screen_width // 2, screen_height // 2))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_button_pressed = pygame.mouse.get_pressed()[0]

        if aqua_skin_rect.collidepoint(mouse_pos) and mouse_button_pressed:
            update_aqua_skin_bought()

            if aqua_skin_bought == "False":

                if player_coins >= aqua_skin_price:
                    player_coins -= aqua_skin_price
                    aqua_skin_bought = "True"
                    with open("aqua_skin_bought.txt", "w") as file:
                        file.write(str(aqua_skin_bought))
                    draw_text_with_outline("Bought Aqua Skin", font, white, black, screen_width / 2, screen_height / 2, outline_thickness=2)
                    pygame.display.flip()
            else:
                selected_skin = "aqua"
                update_bird_skin(flappy, selected_skin)
                    
                screen.blit(selected_img, (185, 350))
                
        mouse_button_pressed_prev_frame = mouse_button_pressed
        if default_skin_rect.collidepoint(mouse_pos) and mouse_button_pressed:
            current_time = pygame.time.get_ticks()
            if current_time - last_multiplier_activation_time >= multiplier_button_cooldown:
                last_multiplier_activation_time = current_time
                selected_skin = "default"
                update_bird_skin(flappy, selected_skin)
                    
                screen.blit(selected_img, (89 - 5, 350))

        pygame.display.flip()
        
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False



        # Check for mouse click to start the game
        if (event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) and flying == False and game_over == False):
            if current_state == START_SCREEN:
                current_state = PLAYING
                flying = True
    
    


    pygame.display.update()

pygame.quit()


