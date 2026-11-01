import pygame
import math
import random
import GUI

pygame.font.init()
# 100 PIXELS PER METRE
BG = (0,0,0)
GRAVITY = 981 # PIXELS / S^2
BOUNDS = (800,600)
SETTINGS_HEIGHT = 100
SETTINGS_RECT = pygame.Rect(0,0,BOUNDS[0],SETTINGS_HEIGHT)
VELOCITY_RECT = pygame.Rect(10,640,450,150)
FLOOR_Y = BOUNDS[1]+SETTINGS_HEIGHT - (BOUNDS[1]+SETTINGS_HEIGHT)/10
FLOOR_RECT = pygame.Rect(0,FLOOR_Y,BOUNDS[0],BOUNDS[1]+SETTINGS_HEIGHT*2-FLOOR_Y)
INITIAL_X = 100
INITIAL_Y = 100
RADIUS = 25
DENSITY = 1
WALL_LEFT = 1
WALL_RIGHT = 1
ARROW_SCALE = 10
COLOURS = [ (255, 23, 68),
            (255, 145, 0),
            (255, 234, 0),
            (118, 255, 3),
            (0, 230, 118),
            (0, 229, 255),
            (41, 121, 255),
            (101, 31, 255),
            (213, 0, 249),
            (255, 64, 129), ]

BOUNCE = 1
STEP_LENGTH = 0
X_VELOCITY = 0
Y_VELOCITY = 0
ALWAYS_DRAW_STATS = False
MOMENTUM_ARROW = False  # False = velocity, True = momentum
TIMESCALE = 1



class Circle:
    def __init__(self,x,y,vx,vy,radius,bounce,colour,density):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.bounce = bounce
        self.colour = colour
        self.density = density
        self.mass =(3.141592 * float(radius**2) * float(density))

    def gravity(self, dt):
        self.vy += GRAVITY * dt

    def step(self,dt,bounds):
        x_b,y_b = bounds

        #consider velocity
        self.x += self.vx * dt
        self.y += self.vy * dt

        #define x bounds
        if self.x - self.radius < 0 and WALL_LEFT:
            self.x = self.radius
            self.vx = -self.vx * self.bounce
        if self.x + self.radius > x_b and WALL_RIGHT:
            self.x = x_b - self.radius
            self.vx = -self.vx * self.bounce

        #define y bounds
        if self.y + self.radius > FLOOR_Y:
            self.y = FLOOR_Y - self.radius
            # ignore floor accelerationm
            if abs(self.vy) < GRAVITY * dt * 1.1:
                self.vy = 0
            else:
                self.vy = -self.vy * self.bounce
        if self.y - self.radius < 0+SETTINGS_HEIGHT:
            self.y = self.radius+SETTINGS_HEIGHT
            self.vy = -self.vy * self.bounce

    def draw(self,surface):
        pygame.draw.circle(surface,self.colour,(self.x,self.y),self.radius)

def Circle_collision(a: Circle,b: Circle):
    dx = a.x - b.x
    dy = a.y - b.y
    dist_square = dx * dx + dy * dy
    coll_dist = a.radius + b.radius

    if dist_square > coll_dist*coll_dist:
        return
    dist = math.sqrt(dist_square)
    if dist == 0:
        dist = 0.001
    unit_x, unit_y = dx/dist, dy/dist # unit vectors (direction correction)

    #fix overlap accounting for mass
    overlap = coll_dist-dist
    recip_mass_a = 1/a.mass
    recip_mass_b = 1/b.mass
    total_recip = recip_mass_a + recip_mass_b

    #general pos correction
    correct_a_x = unit_x * overlap * (recip_mass_a/total_recip)
    correct_a_y = unit_y * overlap * (recip_mass_a/total_recip)
    correct_b_x = unit_x * overlap * (recip_mass_b/total_recip)
    correct_b_y = unit_y * overlap * (recip_mass_b/total_recip)
    a.x += correct_a_x
    b.x -= correct_b_x
    a.y += correct_a_y
    b.y -= correct_b_y

    #consider relative velocity
    rel_vx = a.vx - b.vx
    rel_vy = a.vy - b.vy
    v_on_normal = rel_vx*unit_x + rel_vy*unit_y

    if v_on_normal > 0:
        return

    e = min(a.bounce, b.bounce)
    impulse = -(1+e)*v_on_normal/total_recip

    impulse_x, impulse_y = impulse*unit_x, impulse*unit_y
    a.vx += impulse_x * recip_mass_a
    a.vy += impulse_y * recip_mass_a
    b.vx -= impulse_x * recip_mass_b
    b.vy -= impulse_y * recip_mass_b






def main():
    global GRAVITY, DENSITY, RADIUS, WALL_LEFT, WALL_RIGHT, ARROW_SCALE, BOUNCE, STEP_LENGTH, X_VELOCITY, Y_VELOCITY, ALWAYS_DRAW_STATS, MOMENTUM_ARROW, TIMESCALE
    pygame.init()
    screen = pygame.display.set_mode((BOUNDS[0],BOUNDS[1]+200))
    clock = pygame.time.Clock()

    balls = []

    input_boxes = [
        GUI.NumInputBox(50, 25, 60, 20, float, "Gravity (9.81)", GRAVITY/100, GRAVITY,10000),
        GUI.NumInputBox(50,75,60, 20, float, "Density (1)", DENSITY, DENSITY,100),
        GUI.NumInputBox(250, 25, 60, 20, int, "Radius (25)", RADIUS, RADIUS,100),
        GUI.NumInputBox(250, 75, 60, 20, float, "Bounce (1)", BOUNCE, BOUNCE, 1),
        GUI.NumInputBox(450, 25, 60, 20, float, "Arrow Scale (10)", ARROW_SCALE, ARROW_SCALE, 50),
        GUI.NumInputBox(450, 75, 60, 20, float, "Step Seconds", STEP_LENGTH, STEP_LENGTH, 60),
        GUI.NumInputBox(40, 665, 60, 20, float, "X Velocity (m/s)", 0, X_VELOCITY, 50),
        GUI.NumInputBox(40, 715, 60, 20, float, "Y Velocity (m/s)", 0,Y_VELOCITY, 50),
        GUI.NumInputBox(40, 765, 60, 20, float, "Timescale (1)", 1, TIMESCALE, 2)
        ]

    tick_boxes = [
        GUI.TickBox(650,25,20,20,"Left Wall", 1, WALL_LEFT),
        GUI.TickBox(650,75,20,20,"Right Wall", 1, WALL_RIGHT),
        GUI.TickBox(270, 665, 20, 20, "Show all Stats", 0, ALWAYS_DRAW_STATS),
        GUI.TickBox(270, 715, 20, 20, "Momentum Arrows", 0, MOMENTUM_ARROW),
        ]

    paused = True
    remaining_time = 0

    running = True
    while running:
        dt = clock.tick(60)/1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and FLOOR_Y>event.pos[1]>SETTINGS_HEIGHT:
                    x,y = event.pos
                    x = min(max(x,RADIUS),BOUNDS[0]-RADIUS)
                    y = min(max(y,SETTINGS_HEIGHT+RADIUS),FLOOR_Y-RADIUS)
                    colour = random.choice(COLOURS)
                    while colour in [ball.colour for ball in balls]:
                        colour = random.choice(COLOURS)
                    balls.append(Circle(x,y,X_VELOCITY*100,-Y_VELOCITY*100,RADIUS, BOUNCE, colour,DENSITY))
                    if len(balls) == 10:
                        balls.remove(balls[0])
                elif event.button == 3:
                    mx, my = event.pos
                    for ball in balls:
                        if (ball.x - mx) ** 2 + (ball.y - my) ** 2 <= ball.radius ** 2:
                            balls.remove(ball)
                            break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for box in input_boxes:
                        box.interact(event)
                    for box in tick_boxes:
                        box.interact(event)
                        if box == tick_boxes[0]:
                            WALL_LEFT = box.variable
                            if box.interacted:
                                for ball in balls[:]:  # copy the list so removals dont cause index errors
                                    if ball.x + ball.radius < 0:
                                        balls.remove(ball)
                        elif box == tick_boxes[1]:
                            WALL_RIGHT = box.variable
                            if box.interacted:
                                for ball in balls:
                                    if ball.x - ball.radius > BOUNDS[0]:
                                        balls.remove(ball)
                        elif box == tick_boxes[2]:
                            ALWAYS_DRAW_STATS = box.variable
                        elif box == tick_boxes[3]:
                            MOMENTUM_ARROW = box.variable



            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    balls = []
                elif event.key == pygame.K_p:
                    paused = not paused
                    remaining_time = 0
                elif event.key == pygame.K_n and STEP_LENGTH > 0:
                    remaining_time = STEP_LENGTH
                    paused = False
                else:
                    for box in input_boxes:
                        box.interact(event)
                    if event.key == pygame.K_RETURN:
                        if input_boxes[0].valid:
                            GRAVITY = float(input_boxes[0].variable)

                        if input_boxes[1].valid:
                            DENSITY = max(float(input_boxes[1].variable), 0.01)  # Any value with "max" is prevented from being 0 or negative

                        if input_boxes[2].valid:
                            RADIUS = max(int(input_boxes[2].variable), 1)

                        if input_boxes[3].valid:
                            BOUNCE = max(float(input_boxes[3].variable), 0)

                        if input_boxes[4].valid:
                            ARROW_SCALE = float(input_boxes[4].variable)

                        if input_boxes[5].valid:
                            STEP_LENGTH = float(input_boxes[5].variable)

                        if input_boxes[6].valid:
                            X_VELOCITY = float(input_boxes[6].variable)

                        if input_boxes[7].valid:
                            Y_VELOCITY = float(input_boxes[7].variable)

                        if input_boxes[8].valid:
                            TIMESCALE = max(float(input_boxes[8].variable), 0.01)

        screen.fill(BG)


        if not paused:
            step_dt = dt * TIMESCALE
            if remaining_time > 0:
                step_dt = min(step_dt, remaining_time) # shrink the last frame so it lands exactly on the time
                remaining_time -= step_dt
                if remaining_time <= 0:
                    paused = True

            for ball in balls:
                ball.gravity(step_dt)
                ball.step(step_dt,BOUNDS)


            for _ in range(10):
                for i in range(0, len(balls)):
                    for j in range(i+1, len(balls)):
                        Circle_collision(balls[i],balls[j])


#int((ball.vx**2+ball.vy**2)**0.5)


        pygame.draw.line(screen,(255,255,255),(0,FLOOR_Y),(BOUNDS[0],FLOOR_Y),2)
        pygame.draw.rect(screen,(255,255,255),FLOOR_RECT)

        #pygame.draw.line(screen,(123,123,0),(0,0),(200,400),100)

        for ball in balls:
            ball.draw(screen)
            GUI.draw_arrow(screen,MOMENTUM_ARROW,ball.x,ball.y,ball.vx,ball.vy,ball.mass, 10,ARROW_SCALE,(255,0,0))

        mx, my = pygame.mouse.get_pos()
        for ball in balls:
            if (ball.x - mx) ** 2 + (ball.y - my) ** 2 <= ball.radius ** 2 or ALWAYS_DRAW_STATS:
                GUI.draw_stats(screen,SETTINGS_HEIGHT,  ball.x, ball.y, ball.colour, ball.vx, ball.vy, ball.mass, ball.radius)



        pygame.draw.rect(screen, (100,100,100),SETTINGS_RECT)
        pygame.draw.rect(screen, (100,100,100),VELOCITY_RECT)
        pygame.draw.line(screen,(255,255,255),(0,SETTINGS_HEIGHT),(BOUNDS[0],SETTINGS_HEIGHT),2)
        pygame.draw.line(screen,(10,10,10),(BOUNDS[0]-250,BOUNDS[1]+150),(BOUNDS[0]-50,BOUNDS[1]+150),5)
        scale_label = GUI.GUI_FONT.render("2 Metre Scale",True,(0,0,0))
        screen.blit(scale_label , (BOUNDS[0]-225,BOUNDS[1]+125))


        for box in input_boxes:
            box.draw(screen)

        for box in tick_boxes:
            box.draw(screen)

        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
