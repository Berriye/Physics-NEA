import pygame
pygame.font.init()

class NumInputBox:
    FONT = pygame.font.SysFont('monospace', 20)
    def __init__(self,x,y,width,height,data_type,title,initial_value,variable,max_value):
        self.rect = pygame.Rect(x,y,width,height)
        self.title = title
        self.data_type = data_type
        self.input = str(initial_value)
        self.enabled = False
        self.valid = True
        self.variable = variable
        self.colour_enabled = (150,150,150)
        self.colour_disabled = (60,60,60)
        self.colour_invalid = (200,20,20)
        self.colour_text = (10,10,10)
        self.conversion = variable/initial_value
        self.clicked = False
        self.max_value = max_value
    def output(self,value):
        self.variable = self.data_type(value)*self.conversion
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
                if event.unicode in ["0","1","2","3","4","5","6","7","8","9","."]:
                    self.input += event.unicode
                    self.input = str(min(int(self.input), self.max_value))
        return True

    def draw(self,surface):
        colour = self.colour_invalid if not self.valid else (self.colour_enabled if self.enabled else self.colour_disabled)
        pygame.draw.rect(surface,colour,self.rect)
        text = self.FONT.render(self.title,True,colour)
        text_pos = (self.rect.x, self.rect.y - text.get_height())
        input_text = self.FONT.render(self.input,True,self.colour_text)
        surface.blit(text, text_pos)
        surface.blit(input_text,self.rect)

class TickBox:
    FONT = pygame.font.SysFont('monospace', 20)
    def __init__(self,x,y,width,height,title,initial_value,variable):
        self.rect = pygame.Rect(x,y,width,height)
        self.title = title
        self.state = initial_value
        self.variable = variable
        self.colour_enabled = (210,210,210)
        self.colour_disabled = (80,80,80)
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
        text = self.FONT.render(self.title,True,colour)
        text_pos = (self.rect.x, self.rect.y - text.get_height())
        surface.blit(text, text_pos)





