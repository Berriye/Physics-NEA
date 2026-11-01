import pygame
pygame.font.init()
GUI_FONT = pygame.font.SysFont('monospace', 20)

class BoxBase:
    def __init__(self, x, y, width, height,title, variable):
        self.rect = pygame.Rect(x, y, width, height)
        self.variable = variable
        self.title = title


class NumInputBox(BoxBase):
    def __init__(self,x,y,width,height,data_type,title,initial_value,variable,max_value):
        super().__init__(x,y,width,height,title,variable)
        self.data_type = data_type
        self.input = str(initial_value)
        self.enabled = False
        self.valid = True
        self.colour_enabled = (150,150,150)
        self.colour_disabled = (60,60,60)
        self.colour_invalid = (200,20,20)
        self.colour_text = (10,10,10)
        self.conversion = variable/initial_value if initial_value != 0 else 1
        self.clicked = False
        self.max_value = max_value
    def output(self,value):
        try:
            self.variable = self.data_type(float(value)) * self.conversion
            self.valid = True
        except ValueError:
            self.valid = False  # box turns red instead of crashing
        return self.variable

    def interact(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.clicked = self.rect.collidepoint(event.pos)
            if self.clicked and not self.enabled:
                self.input = ""
            self.enabled = self.clicked
            return self.enabled

        if event.type == pygame.KEYDOWN and self.enabled:
            if event.key == pygame.K_RETURN:
                self.output(self.input)
                self.enabled = False
            elif event.key == pygame.K_ESCAPE:
                self.enabled = False
            elif event.key == pygame.K_BACKSPACE:
                self.input = self.input[:-1]
            else:
                if event.unicode in ["0","1","2","3","4","5","6","7","8","9","."] or (event.unicode == "-" and self.input == ""):
                    final_input = self.input + event.unicode
                    try:
                        if abs(float(self.input+event.unicode)) > self.max_value:
                            self.input = str(self.max_value) if final_input[0] != "-" else str(-self.max_value)
                        else:
                            self.input = final_input
                    except ValueError: # ignorte extra decimal points
                        if final_input.count(".") <= 1:
                            self.input = final_input
        return True

    def draw(self,surface):
        colour = self.colour_invalid if not self.valid else (self.colour_enabled if self.enabled else self.colour_disabled)
        pygame.draw.rect(surface,colour,self.rect)
        text = GUI_FONT.render(self.title,True,colour)
        text_pos = (self.rect.x, self.rect.y - text.get_height())
        input_text = GUI_FONT.render(self.input,True,self.colour_text)
        surface.blit(text, text_pos)
        surface.blit(input_text,self.rect)

class TickBox(BoxBase):
    def __init__(self,x,y,width,height,title,initial_value,variable):
        super().__init__(x, y, width, height, title, variable)
        self.state = initial_value
        self.colour_enabled = (210,210,210)
        self.colour_disabled = (60,60,60)
        self.interacted = False

    def output(self,value):
        self.variable = bool(value)
        return self.variable

    def interact(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if  self.rect.collidepoint(event.pos) == 1:
                self.state = not self.state
                self.interacted = True

            else:
                self.state = self.state
                self.interacted = False

            self.output(self.state)



    def draw(self,surface):
        colour = self.colour_enabled if self.state else self.colour_disabled
        pygame.draw.rect(surface,colour,self.rect)
        text = GUI_FONT.render(self.title,True,colour)
        text_pos = (self.rect.x, self.rect.y - text.get_height())
        surface.blit(text, text_pos)



def draw_arrow(surface,momentum_arrow,x,y,vx,vy,mass,length,scale,colour):
    factor = scale / 100              # arrow length per 1m/s
    if momentum_arrow:
        factor *= mass / 2000         # gives value of one for full default
    end_pos = (x + vx*factor, y + vy*factor)
    pygame.draw.line(surface,(0,0,0),(x,y),end_pos,5)
    pygame.draw.line(surface,(255,255,255),(x,y),end_pos,3)



def draw_stats(surface,settings_height,x,y,colour,vx,vy,mass,radius):
    velocity = ((vx**2 + vy**2)**0.5)/100 #m/s
    mass_kg = mass/(100**2)
    KE = 0.5*mass_kg*(velocity)**2

    KE_text = GUI_FONT.render(f"KE: {abs(round(KE,2))}", True, colour)
    V_text = GUI_FONT.render(f" V: {abs(round(velocity,2))}", True, colour)
    M_text = GUI_FONT.render(f" M: {abs(round(mass_kg,2))}", True, colour)

    width = max(KE_text.get_width(), V_text.get_width(), M_text.get_width())
    height = 40 + KE_text.get_height()
    left = max(4, min(x - 100, surface.get_width() - width - 8))

    top = y - radius - height - 14
    if top - 4 < settings_height:
        top = y + radius + 14

    box = pygame.Rect(left-4, top-4, width+8, height+8)
    pygame.draw.rect(surface, (120,120,120), box)

    surface.blit(KE_text, (left, top))
    surface.blit(V_text, (left, top+20))
    surface.blit(M_text, (left, top+40))







