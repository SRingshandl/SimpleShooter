import pygame
import math
import random
from datetime import datetime

def calc_vector(angle):
    vector_x = math.cos(math.radians(angle))
    vector_y = math.sin(math.radians(angle))
    vector_x = vector_x * 1 / max(abs(vector_x), abs(vector_y))
    vector_y = vector_y * 1 / max(abs(vector_x), abs(vector_y))
    return (vector_x, vector_y)

def steps_func(x1, y1, x2, y2):
    x_ges = x2 - x1
    y_ges = y2 - y1
    distance = math.sqrt(x_ges ** 2 + y_ges ** 2)
    steps = distance / shot_length
    vector_x = shot_length * (x_ges * 1 / max(abs(x_ges), abs(y_ges)))
    vector_y = shot_length * (y_ges * 1 / max(abs(x_ges), abs(y_ges)))
    return (math.ceil(steps), vector_x, vector_y)

def hit_detection(line_x,line_y,circle_x, circle_y, circle_radius):
    if((line_x - circle_x)**2 + (line_y - circle_y)**2 < circle_radius**2):
        return(True)

# initialize pygame
pygame.init()

# used colors
RED     = ( 255, 0, 0)
GREEN   = ( 0, 255, 0)
BLACK = ( 0, 0, 0)
WHITE   = ( 255, 255, 255)

# create window
screen_x = 1000
screen_y = 1000
screen = pygame.display.set_mode((screen_x, screen_y))

# Main title of created window
pygame.display.set_caption("Simple Shooter")

#display text
pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 30)

# run while True
gameactive = True

# for setting refresh time later
clock = pygame.time.Clock()

# Start conditions
player_position_x = 500
player_position_y = 500
player_radius = 40
player_velocity = 5

target_position_x = 500
target_position_y = 500
target_radius = 40
target_velocity = 10
target_angle = 45
target_startlife = 50
target_life = target_startlife

run_counter = 0 # for determining timing; timing dependent on clock.tick
random_timer = random.randrange(0,3) # used for random angle change of target

shot_direction_dict = dict()
shot_length = 50
shot_speed = 1/5 #change denominator: higher denominator --> lower speed
shots_performed = 0

# Main Gameloop
while gameactive:
    # Refresh-time (per second)
    clock.tick(60)

    # chaeck wheter user did an action
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameactive = False
            print("Spieler hat Quit-Button angeklickt")
        elif event.type == pygame.KEYDOWN:
            # Taste für Spieler 1
            if event.key == pygame.K_SPACE:
                print("Spieler hat Leertaste gedrückt")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            shots_performed += 1
            mouse_position = pygame.mouse.get_pos()
            dt = datetime.now()
            timestamp =str(dt.minute) + str(dt.second) + str(dt.microsecond)
            shot_direction_dict[dt] = ((player_position_x,player_position_y), mouse_position, steps_func(player_position_x,player_position_y, mouse_position[0], mouse_position[1]), 0)

    #move player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT] and player_position_x < screen_x - player_radius:
        player_position_x += player_velocity
    if keys[pygame.K_LEFT] and player_position_x > player_radius:
        player_position_x -= player_velocity
    if keys[pygame.K_UP] and player_position_y > player_radius:
        player_position_y -= player_velocity
    if keys[pygame.K_DOWN] and player_position_y < screen_y - player_radius :
        player_position_y += player_velocity

    #bounce target off walls
    if(target_position_x > screen_x - target_radius):
        if(target_angle<180):
            target_angle = 180 - target_angle
        else:
            target_angle = 180 + 360 - target_angle
    if(target_position_x < 0 + target_radius):
        if (target_angle < 180):
            target_angle = 180 - target_angle
        else:
            target_angle = 180 + 360 - target_angle
    if(target_position_y < 0 + target_radius):
        target_angle = 360 - target_angle
    if(target_position_y > screen_y - target_radius):
        target_angle = 360 - target_angle

    #move target
    target_position_x += target_velocity * calc_vector(target_angle)[0]
    target_position_y -= target_velocity * calc_vector(target_angle)[1]

    #change target angle randomly
    if(run_counter == random_timer * 60):
        run_counter = 0
        random_timer = random.randrange(0, 3)
        if(target_position_x >target_radius and
                target_position_x < screen_x - target_radius and
                target_position_y > target_radius and
                target_position_y < screen_y -target_radius):
            target_angle = random.randrange(0,360)
    else:
        run_counter += 1

    # delete game screen and create a new white background
    screen.fill(WHITE)

    # draw game characters
    pygame.draw.circle(screen, BLACK, [player_position_x,player_position_y], player_radius)
    pygame.draw.circle(screen, BLACK, [target_position_x, target_position_y], target_radius+5)
    pygame.draw.circle(screen, RED, [target_position_x, target_position_y], target_radius)

    polygon_tuple = [(target_position_x, target_position_y)]
    for n in range(0, round((target_startlife-target_life)/target_startlife*360)):
        polygon_tuple.append((target_position_x + int(target_radius * math.sin((n+180) * math.pi / 180)),
                              target_position_y + int(target_radius * math.cos((n+180) * math.pi / 180))))
    polygon_tuple.append((target_position_x, target_position_y))

    if len(polygon_tuple) > 2:
        pygame.draw.polygon(screen, (0, 0, 0), polygon_tuple)

    textsurface = myfont.render('Shots taken: ' + str(shots_performed), False, (0, 0, 0))
    screen.blit(textsurface,(0,0))

    #Shot draw and Hit detection
    for shot in list(dict.keys(shot_direction_dict)):
        shot_direction_dict[shot] = (shot_direction_dict[shot][0], shot_direction_dict[shot][1], shot_direction_dict[shot][2], shot_direction_dict[shot][3] + 1) #iterate counter
        iterator = shot_direction_dict[shot][3]

        vector_x = shot_direction_dict[shot][2][1]
        vector_y = shot_direction_dict[shot][2][2]
            
        line_start_x = shot_direction_dict[shot][0][0] + vector_x * iterator * shot_speed
        line_start_y = shot_direction_dict[shot][0][1] + vector_y * iterator * shot_speed

        line_end_x = line_start_x + shot_direction_dict[shot][2][1]
        line_end_y = line_start_y + shot_direction_dict[shot][2][2]
            
        pygame.draw.line(screen, GREEN, [line_start_x, line_start_y], [line_end_x, line_end_y], width=5) #draw shot

        if(hit_detection(line_end_x, line_end_y, target_position_x, target_position_y, target_radius) == True):
            target_life -= 1

       #remove shot from dictionary --> save memory
        dt = datetime.now()
        time_difference = dt - shot
        if(time_difference.total_seconds() > 10):
            del shot_direction_dict[shot]

    #Win Condition
    while(target_life < 1):
        textsurface2 = myfont.render("GAME OVER, press SPACE to quit!", True, (0, 0, 0), (255, 255, 255))
        screen.blit(textsurface2, (500 - textsurface2.get_width() / 2, 500 - textsurface2.get_height() / 2))
        pygame.display.update()
        print("GAME OVER")
        print("It took you " + str(shots_performed) + " shots to finish!")
        while gameactive == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameactive = False
                    target_life = 100
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        gameactive = False
                        target_life = 100

    # Update screen
    pygame.display.update()

pygame.quit()
exit()
