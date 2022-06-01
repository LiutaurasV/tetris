import pygame
import random
import sys
pygame.init()


WIDTH, HEIGHT = 500, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tetris')

GAME_WIDTH = 300 #Width of the game without the HUD

BACKGROUND_COLOR = '#221e3b'

GAME_OVER_FONT = pygame.font.SysFont("Comic sans", 40, True)
SCORE_FONT = pygame.font.SysFont('Comic sans', 24, True)

BLOCK_SIZE = 25

LINE_SOUND = pygame.mixer.Sound('music/line.wav')

COLORS = ['yellow', 'blue', 'orange', 'purple', 'green', 'red', 'cyan', 'pink']

S_SHAPES = [['.XX',
             'XX.'],

            ['X.',
             'XX',
             '.X']]

Z_SHAPES = [['XX.',
             '.XX'],

            ['.X',
             'XX',
             'X.']]

I_SHAPES = [['XXXX'],

            ['.X.',
             '.X.',
             '.X.',
             '.X.']]

T_SHAPES = [['.X.',
             'XXX'],

            ['.X.',
             '.XX',
             '.X.'],

            ['...',
             'XXX',
             '.X.'],

            ['.X.',
             'XX',
             '.X.']]

O_SHAPES = [['XX',
             'XX']]

L_SHAPES = [['X.',
             'X.',
             'XX'],

            ['XXX',
             'X..'],

            ['XX',
             '.X',
             '.X'],

            ['..X',
             'XXX', ]]

J_SHAPES = [['.X.',
             '.X.',
             'XX.'],

            ['X..',
             'XXX',
             '...'],

            ['.XX',
             '.X.',
             '.X.'],

            ['XXX',
             '..X']]


SHAPES = [S_SHAPES, Z_SHAPES, I_SHAPES, T_SHAPES, O_SHAPES, L_SHAPES, J_SHAPES]

groundedBlocks = []
fallSpeed = 300

pygame.mixer.music.load("music/tetrismusic.mp3")
pygame.mixer.music.set_volume(0.15)
pygame.mixer.music.play(-1)


class Figure:
    def __init__(self, shapes, color):
        self.color = color
        self.shapes = shapes #List of the figure positions
        self.current = 0 #Current position index
        self.xpos = 150 #Leftmost point of the figure
        self.top = -50 #Figure's highest point's y coordinate

        #All figures ar made of 4 blocks, so we cr
        self.blocks = [pygame.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE)
                       for i in range(4)]
        
        self.grounded = False
        self.lastMoved = pygame.time.get_ticks() #Time of the last descension, used for framerate independence

    def turn(self):
        if self.current == 0:
            self.current = len(self.shapes)-1
        else:
            self.current -= 1

    def updateBlocks(self):
        y = self.top
        x = self.xpos
        block = 0  # which block is being updated

        for line in self.shapes[self.current]:
            for symbol in line:
                if symbol == 'X':
                    self.blocks[block].topleft = (x, y)
                    block += 1
                x += BLOCK_SIZE
            x = self.xpos
            y += BLOCK_SIZE

        #If it is time to descend the figure and there would be no collision in doing so, descend the block
        if pygame.time.get_ticks() - self.lastMoved > fallSpeed and not collision(self, (0, BLOCK_SIZE)):
            self.top += BLOCK_SIZE
            self.lastMoved = pygame.time.get_ticks()

    def draw(self):

        # If the figure hit the ground, instead of drawing the figure add it's blocks to grounded blocks.
        if collision(self, (0, BLOCK_SIZE)) and pygame.time.get_ticks() - self.lastMoved > fallSpeed:
            

            for i in range(len(self.blocks)):
                groundedBlocks.append((self.blocks.pop(), self.color))

            self.grounded = True
            return

        self.updateBlocks()
        for i in self.blocks:
            drawBlock(i, self.color)


def collision(fig, direction):
    #Check for collision with boundaries and other blocks if the figure moves in the direction
    #(tuple of x and y coordinates) provided
    for block in fig.blocks:

        coordinates = block.centerx + \
            direction[0], block.centery + direction[1]
        if coordinates[0] > GAME_WIDTH or coordinates[0] < 0:
            return True
        if coordinates[1] > HEIGHT:
            return True

        for i in groundedBlocks:
            if i[0].collidepoint(coordinates):
                return True

    return False


def drawBlock(block, color):
    pygame.draw.rect(SCREEN, color, block)
    pygame.draw.line(SCREEN, 'black', block.topleft, block.topright)
    pygame.draw.line(SCREEN, 'black', block.bottomleft, block.bottomright)
    pygame.draw.line(SCREEN, 'black', block.topleft, block.bottomleft)
    pygame.draw.line(SCREEN, 'black', block.topright, block.bottomright)


def drawBlocks():
    for block, color in groundedBlocks:
        drawBlock(block, color)


def drawGrid():
    for i in range(0, GAME_WIDTH, BLOCK_SIZE):
        pygame.draw.line(SCREEN, 'black', (i, 0), (i, HEIGHT))
    for i in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(SCREEN, 'black', (0, i), (GAME_WIDTH, i))

def deleteLine(lineY):
        global score
        blocks_to_remove = []
        #Loop through all grounded blocks and delete those that are on the lineY height
        for block in groundedBlocks:

            if block[0].bottom == lineY:
                blocks_to_remove.append(block)
                score += 10

            elif block[0].bottom < lineY:
                block[0].bottom += BLOCK_SIZE
        for block in blocks_to_remove:
            groundedBlocks.remove(block)

def checkLines():
    #Loop through all lines (marked by the y coordinate) in the game (0, 25, etc..) and count them
    for i in range(0, HEIGHT+1, BLOCK_SIZE):
        counter = []

        for block in groundedBlocks:
            if block[0].bottom == i:
                counter.append(block)
            
            #If the amount of grounded blocks at that y coordinate make up a full line, delete the blocks at that line
            if len(counter) == GAME_WIDTH / BLOCK_SIZE:
                deleteLine(i)
                LINE_SOUND.play()
                checkLines()
                return


def gameOver(score):
    #Show a black screen with the score for a 4 seconds, then exit the game
    pygame.mixer.music.load('music/gameover.wav')
    pygame.mixer.music.play()

    SCREEN.fill('black')

    textsurf = GAME_OVER_FONT.render("GAME OVER", False, 'white')
    xpos = (WIDTH - textsurf.get_width()) // 2 #Center the text
    SCREEN.blit(textsurf, (xpos, 320))

    textsurf = SCORE_FONT.render("SCORE: " + str(score), False, 'white')
    xpos = (WIDTH - textsurf.get_width()) // 2
    SCREEN.blit(textsurf, ((xpos, 400)))

    pygame.display.flip()
    pygame.time.wait(4000)
    pygame.quit()
    sys.exit()


def drawHUD(score):
    textsurf = SCORE_FONT.render("SCORE: " + str(score), False, 'white')
    xpos = GAME_WIDTH +  ((WIDTH - GAME_WIDTH - textsurf.get_width()) // 2) # Center the text
    SCREEN.blit(textsurf, (xpos, 50))

    textsurf = SCORE_FONT.render("Next shape:", False, 'white')
    xpos = GAME_WIDTH +  ((WIDTH - GAME_WIDTH - textsurf.get_width()) // 2)
    SCREEN.blit(textsurf, (xpos, 250))

    for i in nextFig.blocks:
        drawBlock(i, nextFig.color)


def getNextFig():
    nextFig = Figure(random.choice(SHAPES), random.choice(COLORS))
    #Setting the next figure's position at HUD
    nextFig.xpos = 375
    nextFig.top = 300
    # I shape needs adjustment to display nciely
    if nextFig.shapes == I_SHAPES:
        nextFig.xpos -= BLOCK_SIZE
    nextFig.updateBlocks()

    return nextFig


activeFig = Figure(random.choice(SHAPES), random.choice(COLORS))
nextFig = getNextFig()
score = 0

while True:
    #EVENT HANDLING START
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                activeFig.turn()
                activeFig.updateBlocks()
                #If the figure collides with something after turning, turn it 3 more times to reset initial position
                if collision(activeFig, (0, 0)):
                    for i in range(3):
                        activeFig.turn()
                    activeFig.updateBlocks()

            if event.key == pygame.K_LEFT:
                #Move the figure only if there is no collision in the left side
                if not collision(activeFig, (-BLOCK_SIZE, 0)):
                    activeFig.xpos -= BLOCK_SIZE

            if event.key == pygame.K_RIGHT:
                #Move the figure only if there is no collision in the right side
                if not collision(activeFig, (BLOCK_SIZE, 0)):
                    activeFig.xpos += BLOCK_SIZE

            if event.key == pygame.K_DOWN:
                #reset the fall speed if the down arrow is released
                fallSpeed = 30

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                fallSpeed = 300
    ##EVENT HANDLING END

    SCREEN.fill(BACKGROUND_COLOR)

    #Draw the line seperating the game field from the HUD
    pygame.draw.line(SCREEN, 'white', (GAME_WIDTH+3, 0),
                     (GAME_WIDTH+3, HEIGHT), width=6)
    drawBlocks()
    drawHUD(score)

    #Keep draving the active figure while it has not hit the ground
    if not activeFig.grounded:
        activeFig.draw()
    
    #When the figure hits the ground, change the active figure
    else:
        activeFig = nextFig
        # Initializing again to reset the position
        activeFig.__init__(activeFig.shapes, activeFig.color)
        nextFig = getNextFig()
        checkLines()

        for i in groundedBlocks:
            if i[0].top == 0:
                gameOver(score)

    pygame.display.update()
