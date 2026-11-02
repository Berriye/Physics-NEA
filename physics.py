from main import *
import pygame
import math

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





