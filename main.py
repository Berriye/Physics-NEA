import pygame
import math
import random
import GUI

pygame.font.init()

BG = (0,0,0)
GRAVITY = 981 # PIXELS / S^2
BOUNDS = (800,600)
SETTINGS_HEIGHT = 100
SETTINGS_RECT = pygame.Rect(0,0,BOUNDS[0],SETTINGS_HEIGHT)
FLOOR_Y = BOUNDS[1]+SETTINGS_HEIGHT - (BOUNDS[1]+SETTINGS_HEIGHT)/10
FLOOR_RECT = pygame.Rect(0,FLOOR_Y,BOUNDS[0],BOUNDS[1]*SETTINGS_HEIGHT-FLOOR_Y)
INITIAL_X = 100
INITIAL_Y = 100
RADIUS = 25
DENSITY = 1
WALL_LEFT = 1
WALL_RIGHT = 1
#ARROW_SCALE = 1  --- ARROW NOT IMPLEMENTED YET ---



class Circle(pygame.sprite.Sprite):
    def __init__(self,x,y,vx,vy,radius,bounce,colour,density):
        super().__init__()
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.bounce = bounce
        self.colour = colour
        self.mass =(3.141592 * float(radius**2) * float(density))

    def gravity(self, gravity, dt):
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
    global GRAVITY, DENSITY, RADIUS, WALL_LEFT, WALL_RIGHT, ARROW_SCALE
    pygame.init()
    screen = pygame.display.set_mode((BOUNDS[0],BOUNDS[1]+200))
    clock = pygame.time.Clock()

    balls = []

    input_boxes = []
    input_boxes.append(GUI.NumInputBox(50, 25, 60, 20, float, "Gravity (9.81)", GRAVITY/100, GRAVITY,10000))
    input_boxes.append(GUI.NumInputBox(50,75,60, 20, float, "Density (1)", DENSITY, DENSITY,100))
    input_boxes.append(GUI.NumInputBox(250, 25, 60, 20, int, "Radius (25)", RADIUS, RADIUS,100))
    #input_boxes.append(GUI.NumInputBox(250, 75, 60, 20, int, "Arrow Scale (1)", ARROW_SCALE, ARROW_SCALE, 10)) --- ARROW NOT IMPLEMENTED YET ---

    tick_boxes = []
    tick_boxes.append(GUI.TickBox(450,25,20,20,"Left Wall", 1, WALL_LEFT))
    tick_boxes.append(GUI.TickBox(450,75,20,20,"Right Wall", 1, WALL_RIGHT))

    paused = True

    running = True
    while running:
        dt = clock.tick(60)/1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and event.pos[1]>SETTINGS_HEIGHT:
                    x,y = event.pos
                    x = min(max(x,RADIUS),BOUNDS[0]-RADIUS)
                    y = min(max(y,RADIUS),BOUNDS[1]+SETTINGS_HEIGHT-RADIUS)
                    balls.append(Circle(x,y,0,0,RADIUS, 0.8, (random.randint(0,255),random.randint(0,255),random.randint(0,255)),DENSITY))
                    if len(balls) == 10:
                        balls.remove(balls[0])
                elif event.button == 3:
                    mx, my = event.pos
                    for ball in balls:
                        if (ball.x - mx) ** 2 + (ball.y - my) ** 2 <= RADIUS ** 2:
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
                                for ball in balls:
                                    if ball.x + ball.radius < 0:
                                        balls.remove(ball)
                        elif box == tick_boxes[1]:
                            WALL_RIGHT = box.variable
                            if box.interacted:
                                for ball in balls:
                                    if ball.x - ball.radius > BOUNDS[0]:
                                        balls.remove(ball)



            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    balls = []
                elif event.key == pygame.K_q:
                    for ball in balls:
                        ball.vx += (random.randint(0,200)-100)*100
                        ball.vy += (random.randint(0,200)-100)*100
                elif event.key == pygame.K_p:
                    paused = not paused
                else:
                    for box in input_boxes:
                        box.interact(event)
                    if event.key == pygame.K_RETURN:
                        if input_boxes[0].valid:
                            GRAVITY = min(float(input_boxes[0].variable),10000)

                        if input_boxes[1].valid:
                            DENSITY = min(int(input_boxes[1].variable),100)

                        if input_boxes[2].valid:
                            RADIUS = min(int(input_boxes[2].variable),200)

                        if input_boxes[3].valid:
                            ARROW_SCALE = min(int(input_boxes[3].variable),10)

        screen.fill(BG)


        if not paused:
            for ball in balls:
                print(ball.x,ball.y)
                ball.gravity(GRAVITY,dt)
                ball.step(dt,BOUNDS)
                print(ball.x,ball.y)


            for _ in range(10):
                for i in range(0, len(balls)):
                    for j in range(i+1, len(balls)):
                        Circle_collision(balls[i],balls[j])

        for ball in balls:
            ball.draw(screen)



        pygame.draw.line(screen,(255,255,255),(0,FLOOR_Y),(BOUNDS[0],FLOOR_Y),2)
        pygame.draw.rect(screen,(255,255,255),FLOOR_RECT)
        pygame.draw.rect(screen, (100,100,100),SETTINGS_RECT)
        pygame.draw.line(screen,(255,255,255),(0,SETTINGS_HEIGHT),(BOUNDS[0],SETTINGS_HEIGHT),2)


        for box in input_boxes:
            box.draw(screen)

        for box in tick_boxes:
            box.draw(screen)

        pygame.display.flip()
        print(GRAVITY)
    pygame.quit()


if __name__ == '__main__':
    main()
