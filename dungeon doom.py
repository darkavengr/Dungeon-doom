        
# Dungeon Doom
#
# Version 2.0
#
import warnings
from tkinter import *
from tkinter import messagebox
import os
import time
import random
import copy
try:
 import pyaudio
except ImportError:                 # no pyaudio
    Sound.SoundEnabled=False
    Sound.SoundPossible=False
  
    warnings.warn("Unable to import module PyAudio. Sound will not be used.")
    
try:    
    import wave
except ImportError:                 # no sound
    Sound.SoundEnabled=False
    Sound.SoundPossible=False

    warnings.warn("Unable to import module wave. Sound will not be used.")
    
try:
    import mido
except:
    Midi.MusicEnabled=False
    Midi.MusicPossible=False
    warnings.warn("Unable to import module mido. Music will not be used.")

try:
    from mido import MidiFile
except:
    Midi.MusicEnabled=False
    Midi.MusicPossible=False
    warnings.warn("Unable to import module MidiFile from mido. Music will not be used.")
        
#
# Player class
#
class Player(object):
    DefaultNumberOfLives=4
    NumberOfLives=DefaultNumberOfLives
    MaximumNumberOfLives=99    
    DefaultHealthLevel=8
    HealthLevel=DefaultHealthLevel
    ExperiencePoints=0
    DefaultMaximumExperiencePoints=10
    MaximumExperiencePoints=DefaultMaximumExperiencePoints
    InventorySize=10    
    CurrentInventorySelected=0
    inventory=[None] * InventorySize
    level=1
    PLAYER_RESTORE_TIME=500   
    ApplyingEffect=False
    player_x=0
    player_y=0
    player_start_x=2
    player_start_y=1
    
    FACING_NORTH = 0  # Constants for facing north,south,east or west
    FACING_SOUTH = 1
    FACING_EAST  = 2
    FACING_WEST  = 3
    
    which_way_facing=0

    # Entries in player types
    
    PLAYER_ENTRY_NAME     = 0
    PLAYER_ENTRY_STRENGTH = 1
    PLAYER_ENTRY_AGILITY  = 2
    PLAYER_ENTRY_LUCK     = 3
    PLAYER_ENTRY_STAMINA  = 4
    PLAYER_ENTRY_SPRITE    = 5
    PLAYER_ENTRY_DAMAGED_SPRITE = 6
    PLAYER_ENTRY_DEAD_SPRITE = 7
    PLAYER_ENTRY_ATTACK = 8
    PLAYER_ENTRY_GRAPHIC = 9
    
    #                   Name       Strength  Agility  Luck      Stamina   Player sprite tile             Damaged sprite tile                  Dead sprite tile                  Player attack tile                  Character graphic
    player_types = [ [ "barbarian",0.90,    0.70,     0.10,     0.10,     "tiles/barbarian-sprite.gif", "tiles/damaged-barbarian-sprite.gif","tiles/dead-barbarian-sprite.gif","tiles/barbarian-sprite-attack.gif","graphics/barbarian.gif" ],\
                     [ "elf",      0.40,    0.20,     0.20,     0.90,     "tiles/elf-sprite.gif",       "tiles/damaged-elf-sprite.gif",      "tiles/dead-elf-sprite.gif",      "tiles/elf-sprite-attack.gif",      "graphics/elf.gif"   ],\
                     [ "dwarf",    0.80,    0.20,     0.10,     0.20,     "tiles/dwarf-sprite.gif",     "tiles/damaged-dwarf-sprite.gif",    "tiles/dead-elf-sprite.gif",      "tiles/dwarf-sprite-attack.gif",    "graphics/dwarf.gif" ],\
                     [ "cleric",   0.50,    0.10,     0.20,     0.40,     "tiles/cleric-sprite.gif",    "tiles/damaged-cleric-sprite.gif",   "tiles/dead-elf-sprite.gif",      "tiles/cleric-sprite-attack.gif",   "graphics/cleric.gif" ],\
                     [ "paladin",  0.60,    0.10,     0.20,     0.50,     "tiles/paladin-sprite.gif",   "tiles/damaged-paladin-sprite.gif",  "tiles/dead-paladin-sprite.gif",  "tiles/paladin-sprite-attack.gif",  "graphics/paladin.gif" ],\
                   ]
  
    #
    # Create player
    #
    def __init__(self,canvas,image,x,y):
        Player.NumberOfLives=Player.DefaultNumberOfLives
        Player.HealthLevel=Player.DefaultHealthLevel      
        Player.ExperiencePoints=0
        Player.CurrentInventorySelected=0
        Player.inventory=[None] * Player.InventorySize
        
# load default player image
        p=self.player_types[Player.player_selected]        
        Player.PlayerImage=PhotoImage(file=p[self.PLAYER_ENTRY_SPRITE])
        Player.saveimage=None
        Player.savebackground=None
        Player.PlayerType=p[self.PLAYER_ENTRY_NAME]
        Player.which_way_facing=Player.FACING_EAST

        targetxy=int(y*((Game.w/Tile.TILE_Y_SIZE)))+x
                
        if Player.which_way_facing == Player.FACING_NORTH:
            Tile.copy_image(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)            
        elif Player.which_way_facing == Player.FACING_WEST:
            Tile.rotate_anticlockwise_90degrees(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)
        elif Player.which_way_facing == Player.FACING_SOUTH:            
            Tile.flip_image_y(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)
        elif Player.which_way_facing == Player.FACING_EAST:
            Tile.rotate_clockwise_90degrees(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)

        Player.savebackground=PhotoImage(file="")
        Player.saveimage=PhotoImage(file="")
   # 
    # Destroy player
    #
    def DestroyPlayer():
        return
                
    def die():       
        Player.NumberOfLives -= 1
        HUD.UpdateHUD()
        
        if Player.NumberOfLives == 0:                       # no more livess
           Game.GameOver(Game)                  # game over
        else:
            soundpath=os.path.join(os.getcwd(),"sounds/die.wav")            # player dies
            Sound.PlaySound(soundpath)                      # play sound

            p=Player.player_types[Player.player_selected]
            tilepath=os.path.join(os.getcwd(),p[Player.PLAYER_ENTRY_DEAD_SPRITE])
            Player.ApplyEffect(Player.player_x,Player.player_y,Player.PLAYER_RESTORE_TIME,tilepath)
            
            Player.HealthLevel=Player.DefaultHealthLevel
            HUD.UpdateHUD()
            
            
    #
    # Player hit
    #
    def hit(NumberOfPointsToDeduct):       
        soundpath=os.path.join(os.getcwd(),"sounds/hit.wav")
        Sound.PlaySound(soundpath)                      # play sound

        Player.HealthLevel -= NumberOfPointsToDeduct                # update health level

        p=Player.player_types[Player.player_selected]

        if Player.HealthLevel <= 0:     # player is dead
            tilepath=os.path.join(os.getcwd(),p[Player.PLAYER_ENTRY_DEAD_SPRITE])
            Player.ApplyEffect(Player.player_x,Player.player_y,Player.PLAYER_RESTORE_TIME,tilepath)

            if Player.NumberOfLives == 0:           # game over            
                Game.GameOver(Game)
            else:
                Player.die()            
        else:         
         tilepath=os.path.join(os.getcwd(),p[Player.PLAYER_ENTRY_DAMAGED_SPRITE])
         Player.ApplyEffect(Player.player_x,Player.player_y,Player.PLAYER_RESTORE_TIME,tilepath)
         HUD.UpdateHUD()

#
# Apply affect to player
#
    def ApplyEffect(x,y,wait,affect_tile):
        if Player.ApplyingEffect == True:                   # If already applying effect, return
            return

        Player.ApplyingEffect=True                      # Set flag for applying effect
        
        targetxy=int(y*((Game.w/Tile.TILE_Y_SIZE)))+x
        
        Tile.copy_image(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Player.saveimage)
        Tile.copy_image(Game.blockimages[targetxy].image,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Player.savebackground)
        
        Player.PlayerImage=PhotoImage(file=affect_tile)
        Player.PlayerImage.img=Player.PlayerImage
                          
        if Player.which_way_facing == Player.FACING_NORTH:                           # moving north            
            Tile.copy_image(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)            
        elif Player.which_way_facing == Player.FACING_WEST:                          # moving west:            
            Tile.rotate_anticlockwise_90degrees(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)
        elif Player.which_way_facing == Player.FACING_SOUTH:            
            Tile.flip_image_y(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)
        elif Player.which_way_facing == Player.FACING_EAST:            
            Tile.rotate_clockwise_90degrees(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)
          
        Game.rootwindow.after(wait,Player.RestorePlayer)     # restore sprite


    #
    # restore player sprite
    #
    def RestorePlayer():
        if Game.InGame == False:
            return
        
        targetxy=int(Player.player_y*((Game.w/Tile.TILE_Y_SIZE)))+Player.player_x
        
        # restore background and player image
        if Player.savebackground != None and Player.PlayerImage != None and Player.saveimage != None:
            Tile.copy_image(Player.savebackground,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Player.PlayerImage)
        
            Tile.copy_image(Player.saveimage,Tile.TILE_X_SIZE-1,Tile.TILE_Y_SIZE-1,Player.PlayerImage)

# restore background        
        if Player.which_way_facing == Player.FACING_NORTH:                           # moving north            
            Tile.copy_image(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)           
            
        elif Player.which_way_facing == Player.FACING_WEST:                          # moving west            
            Tile.rotate_anticlockwise_90degrees(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)
            
        elif Player.which_way_facing == Player.FACING_SOUTH:            
            Tile.flip_image_y(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)
            
        elif Player.which_way_facing == Player.FACING_EAST:
            
            Tile.rotate_clockwise_90degrees(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)

        Player.ApplyingEffect=False              # Clear flag for applying effect
       
    #
    # select inventory item
    #
    def select_inventory(which,event=None):        
        Player.CurrentInventorySelected=WHICH_WAY   
        HUD.UpdateHUD()

    #
    # use inventory item
    #
    def use_inventory_item(which,event=None):
        
        inventory_item=Player.inventory[which]              # get inventory item
                
        inventory_item[Game.BLK_FUNCTION]()                                 # call function from list

        del(Player.inventory[which])

    def attack_handler():
            stagetiles=Game.stage_tiles[Game.CurrentStage-1]          # point to tiles for stage
        
            foregroundtiles=stagetiles[Game.STAGE_FOREGROUND_TILES]
            backgroundtiles=stagetiles[Game.STAGE_BACKGROUND_TILES]
            background=stagetiles[Game.STAGE_BACKGROUND]

            soundpath=os.path.join(os.getcwd(),"sounds/sword.wav")
            Sound.PlaySound(soundpath)                      # play sound
    
            p=Player.player_types[Player.player_selected]
            attackpercent=(p[Player.PLAYER_ENTRY_STRENGTH]+p[Player.PLAYER_ENTRY_AGILITY])*p[Player.PLAYER_ENTRY_LUCK]
            
            tilepath=os.path.join(os.getcwd(),p[Player.PLAYER_ENTRY_ATTACK]) 
            Player.ApplyEffect(Player.player_x,Player.player_y,Player.PLAYER_RESTORE_TIME,tilepath)

            targetxy=int(Player.player_y*((Game.w/Tile.TILE_Y_SIZE)+1))+Player.player_x
            
# attack all around
            for blockxy in (Player.player_x,Player.player_y+1),(Player.player_x,Player.player_y-1),(Player.player_x-1,Player.player_y),(Player.player_x+1,Player.player_y):
                x=blockxy[0]
                y=blockxy[1]

            # attacking block
            
                for object_type_list in foregroundtiles:                    
                       if object_type_list[Game.BLK_FILENAME] == Game.blockimages[targetxy+1]:         # if block matches
                        if (object_type_list[Game.BLK_FLAGS] & Game.BLOCK_BREAKABLE):     # block is breakable                        
                             soundpath=os.path.join(os.getcwd(),"sounds/breakobject.wav")
                             Sound.PlaySound(soundpath)

                             Game.blockimages[targetxy]="="          # remove tile from database
                        
                             tilepath=os.path.join(os.getcwd(),"tiles/object-destroyed.gif")
                             Player.ApplyEffect(Player.player_x,Player.player_y,Player.PLAYER_RESTORE_TIME,tilepath)           # show destroyed tile
                             return
    
                # attacking npc

                for n in Game.npcs:                   
                    if (n.x == x) and (n.y == y):           # is npc at coordinates                        
                        n.stamina -= attackpercent

                        if (n.stamina < 1):                            
                            soundpath=os.path.join(os.getcwd(),"sounds/monster_die.wav")
                            Sound.PlaySound(soundpath)                      # play sound
                           
                            n.DestroyNPC()                                                    
                            Game.npcs.remove(n)                            
                        else:
                
                            soundpath=os.path.join(os.getcwd(),"sounds/hit.wav")
                            Sound.PlaySound(soundpath)                      # play sound

                            NPC.Invert_NPC_Sprite(n.npc_tiles,n.x,n.y)
                            Game.rootwindow.after(Player.PLAYER_RESTORE_TIME,n.RestoreAfterAttack)     # restore npc
              

    #
    # Adust health level
    #
    def AdjustHealthLevel(points):
      if Player.HealthLevel < Player.DefaultHealthLevel:            # Only adjust if below maximum
          Player.HealthLevel += points
          HUD.UpdateHUD()
  
                    
# Tile class
#
class Tile(object):
    TILE_X_SIZE=32
    TILE_Y_SIZE=32
    previousimage=None
    previousimagename=""
    currentimagename=""
    attributes=0
    x=0
    y=0
    
    #
    # Create tile
    #
    def __init__(self,imagename,x,y):
     self.previousimagename=imagename
     self.currentimagename=imagename      
     self.x=x
     self.y=y
     self.OverlayImage=None
     
     self.ChangeTileImage(imagename)
      
    #
    # Show tile
    #
    def ShowTile(self,canvas):
        canvas.create_image(self.x,self.y, image=self.image)       # display image
        Game.canvas.pack()
            

    #
    # Destroy tile
    #
    def DestroyTile(self):
        self.destroy()

    #
    # Change tile image
    #
    def ChangeTileImage(self,imagename):
        self.image=PhotoImage(file=imagename)        # load image
        self.currentimagename=imagename
        self.previousimagename=imagename
        
        Game.canvas.create_image(self.x,self.y,anchor=NW,image=self.image)                # place image on top of background
        Game.canvas.pack()

    #
    # Restore tile image
    #
    def RestoreTileImage(self):
        if Game.InGame == False:
            return

        if self.previousimagename != None:
            self.image.config(file=self.previousimagename)      # change image
            self.currentimagename=self.previousimagename
            
        if self.OverlayImage != None:           
            Tile.copy_image(self.OverlayImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,self.image)
            
    def SetAttributes(self,attribs):
        self.attributes=attribs
        
    #
    # Copy image
    #
    
    def copy_image(image,xsize,ysize,newimage):
        newcount=0

        for x in range(0,xsize):                # until end of x
            for y in range(0,ysize):            # until end of y                
                pixel=image.get(x,y)   # get pixel
            
                pix="%x%x%x" % pixel         # format as a string
            
                if len(pix) < 6:              # pad out if less than 6 digits
                   for count in range(0,6-len(pix)):
                        pix += "0"
    
                pix="#"+pix

                if  pix != "#000000":              
                    newimage.put(pix,(x,y)) # put pixel                    

    #
    # Flip image on the X axis
    #
    def flip_image_x(image,xsize,ysize,newimage):
        newcount=0

        y=0;
    
        while y < ysize:                    # for each column
        
        #
        # copy each row in reverse to the new image
        # across the x-axis
        #
            xcount=0
            newcount=xsize-1

            while xcount < xsize:         # for each pixel in row
                pixel=image.get(xcount,y)   # get pixel
            
                x="%x%x%x" % pixel         # format as a string
            
                if len(x) < 6:              # pad out if less than 6 digits
                   for count in range(0,6-len(x)):
                        x += "0"
    
                x="#"+x

                if  x != "#000000":              
                    newimage.put(x,(newcount,y)) # put pixel
                    newcount -= 1
                    xcount +=1

                y += 1

    #
    # Flip image on Y axis
    #
    # Copies image pixels in columns in reverse
    #
    def flip_image_y(image,xsize,ysize,newimage):
        newcount=0
        y=0
        x=0
        
        while x < xsize:                      # for each row
            ycount=ysize-1          # zero-based
            newcount=0         # Start at Y=0

            while ycount > 0:
#                print(x,y)
                
                pixel=image.get(x,ycount)       # read pixel from source

                #print(x,ycount)

                # get pixel into string and pad
                
                formatted_pixel="%x%x%x" % pixel    

                if len(formatted_pixel) < 6:
                   for count in range(0,6-len(formatted_pixel)):
                        formatted_pixel += "0"

                formatted_pixel="#"+formatted_pixel
                       
                if formatted_pixel != "#000000":                # ignore trasparency
                    newimage.put(formatted_pixel,(x,newcount))  # put pixel
        
                newcount += 1   
                ycount -=1    # copying in reverse

            x += 1

#
# Rotate image anticlockwise 90 degrees
#
# Copy rows into columns forwards

    def rotate_anticlockwise_90degrees(image,xsize,ysize,newimage):
        x=0
        y=0

        outx=0
        outy=0

        while x < xsize:
           
           y=0    # start from column 0
           
           while y < ysize:
                               
                pixel=image.get(x,y)                # get pixel
        
                #print(x,y,outx,outy)

               # format and pad pixel into string
               
                formatted_pixel="%x%x%x" % pixel                   
                
                if len(formatted_pixel) < 6:
                   for count in range(0,6-len(formatted_pixel)):
                        formatted_pixel += "0"


                formatted_pixel="#"+formatted_pixel
                
                if formatted_pixel != "#000000":                # ignore transparency                                 
                 newimage.put(formatted_pixel,(outx,outy))      # put pixel
          
                y += 1
                outx += 1    # increment row


           outx=0         
           x += 1
           outy += 1

    #
    # Rotate tile clockwise 90 degrees
    #
    # Copies rows into columns, where the rows are read forwards
    # and written in reverse
    #
    def rotate_clockwise_90degrees(image,xsize,ysize,newimage):
        x=0
        y=0
        outx=0
        outy=0

        while x < xsize:
           
           y=ysize-1
           
           while y > 0:
                                   
                pixel=image.get(x,y)                        # get pixel
        
                #print(x,y,outx,outy)

                # format and pad pixel into string
                
                formatted_pixel="%x%x%x" % pixel                   
               
                if len(formatted_pixel) < 6:
                   for count in range(0,6-len(formatted_pixel)):
                        formatted_pixel += "0"


                formatted_pixel="#"+formatted_pixel
                
                if formatted_pixel != "#000000":                            # ignore transparency       
                 newimage.put(formatted_pixel,(outx,outy))      # put pixel
          
                y -= 1
                outx += 1


           outx=0         
           x += 1
           outy += 1           

    def invert_image(image,xsize,ysize,newimage):
        newcount=0

        
        for x in range(0,xsize):                # until end of x
            for y in range(0,ysize):            # until end of y                
                pixel=image.get(x,y)   # get pixel

                if pixel != (0,0,0):
                    red=((pixel[0] & 0xff0000) >> 16)
                    green=((pixel[1] & 0x00ff00) >> 8)
                    blue=(pixel[2] & 0x0000ff)

                    if red < 0:
                        red=256-abs(red)

                    if green < 0:
                        green=256-abs(green)

                    if blue < 0:                    
                        blue=256-abs(blue)
                    
                    newpixel=(red),(green),(blue)

                    pix="%x%x%x" % newpixel         # format as a string
                    
                    if pix != "#000000":                            # ignore transparency       
                     if len(pix) < 6:              # pad out if less than 6 digits
                       for count in range(0,6-len(pix)):
                            pix += "0"
                
                    pix="#"+pix
                                   
                    newimage.put(pix,(x,y)) # put pixel                    

#
# Game class
#
class Game(object):
    rootwindow=None       
    w=0
    h=0
    tilepos=0         
    blockimages=[]
    tiles=[]
    CurrentStage=1
    CurrentAreaInStage=1
    MaxAreasInStage=4
    MaxStages=8
    npcs = []
    buttons = []
    images =  []
    player_selected=-1
    ROW_COUNT=5
    key_press_count=0
    max_items=10
    min_items=1    
    max_npcs=10
    min_npcs=1
    move_forward_locked=True
    MenuBarHeight=3
    
    BLK_FILENAME = 0
    BLK_FUNCTION = 1
    BLK_FLAGS    = 2
    BLK_GENPROB  = 3
    BLK_MAX_X_SIZE = 4
    BLK_MAX_Y_SIZE = 5
    BLK_MAX_ITEMS = 6
    
    # block properties
    BLOCK_PICKUPABLE  = 1
    BLOCK_TRAVERSABLE = 2
    BLOCK_MOVEABLE    = 4
    BLOCK_BREAKABLE   = 8    
    BLOCK_MAGIC       = 16
    BLOCK_GENERATED   = 32
    BLOCK_OVERLAYABLE = 64
    BLOCK_UNIQUE = 128
    BLOCK_TRAVERSABLE_NOT_NPC = 256

    STAGE_FOREGROUND_TILES = 0
    STAGE_BACKGROUND_TILES = 1
    STAGE_BACKGROUND = 2

    WORLD_ORDINARY = 1
    WORLD_BOSS_FIGHT = 2
    
    item_tiles = [
                        ["tiles/healthpotion.gif",lambda: Game.do_health_potion(),BLOCK_TRAVERSABLE | BLOCK_PICKUPABLE | BLOCK_GENERATED,2,0,0,2],\
		  	["tiles/extralifepotion.gif",lambda: Game.do_extra_life_potion(),BLOCK_TRAVERSABLE | BLOCK_PICKUPABLE | BLOCK_GENERATED,1,0,0,1],\
		  	
    ]

    stage1_foreground_tiles = [                        		  	
		  	[ [["tiles/rock_plant.gif"]],lambda: Game.NullFunction(),0 ,100,5,5],\
                        
                        [ [["tiles/largetree001.gif","tiles/largetree002.gif","tiles/largetree003.gif"],\
                           ["tiles/largetree004.gif","tiles/largetree005.gif","tiles/largetree006.gif"],\
                           ["tiles/largetree007.gif","tiles/largetree008.gif","tiles/largetree009.gif"],\
                           ["tiles/largetree010.gif","tiles/largetree011.gif","tiles/largetree012.gif"],\
                           ],lambda: Game.NullFunction(),0 ,20,10,10],\
                       [   [["tiles/smalltree001.gif","tiles/smalltree002.gif","tiles/smalltree003.gif"],\
                           ["tiles/smalltree004.gif","tiles/smalltree005.gif","tiles/smalltree006.gif"],\
                           ["tiles/smalltree007.gif","tiles/smalltree008.gif","tiles/smalltree009.gif"],\
                           ],lambda: Game.NullFunction(),0 ,20,10,10],\
                       [   [["tiles/mediumtree001.gif","tiles/mediumtree002.gif","tiles/mediumtree003.gif","tiles/mediumtree004.gif"],\
                           ["tiles/mediumtree005.gif","tiles/mediumtree006.gif","tiles/mediumtree007.gif","tiles/mediumtree008.gif"],\
                           ["tiles/mediumtree009.gif","tiles/mediumtree010.gif","tiles/mediumtree011.gif","tiles/mediumtree012.gif"],\
                           ],lambda: Game.NullFunction(),0 ,10,10,10],\
                              [   [["tiles/sand-top-left.gif","tiles/sand.gif","tiles/sand.gif","tiles/sand-top-right.gif"],\
                           ["tiles/sand-left.gif","tiles/sand.gif","tiles/sand.gif","tiles/sand-right.gif"],\
                           ["tiles/sand-left.gif","tiles/sand.gif","tiles/sand.gif","tiles/sand-right.gif"],\
                           ["tiles/sand-left.gif","tiles/sand.gif","tiles/sand.gif","tiles/sand-right.gif"],\
                           ["tiles/sand-bottom-left.gif","tiles/sand.gif","tiles/sand.gif","tiles/sand-bottom-right.gif"],\
                           ],lambda: Game.do_quicksand(),BLOCK_TRAVERSABLE,10,10,10]                         
                        ]
    
    #                    graphic file        function to call            flags               Gen. prob
    stage1_background_tiles = [
		  	[ "tiles/bush.gif",lambda: Game.NullFunction(),0,5,20,20],\
                        ["tiles/mossy_tile.gif",lambda: Game.NullFunction(),BLOCK_TRAVERSABLE,5,10,10],\
                        ["tiles/spikes.gif",lambda: Game.do_spikes(),BLOCK_TRAVERSABLE,5,10,10],\
                       ]

    stage2_foreground_tiles = [                        		  	
		  	[  [["tiles/largetree001.gif","tiles/largetree002.gif","tiles/largetree003.gif"],\
                           ["tiles/largetree004.gif","tiles/largetree005.gif","tiles/largetree006.gif"],\
                           ["tiles/largetree007.gif","tiles/largetree008.gif","tiles/largetree009.gif"],\
                           ["tiles/largetree010.gif","tiles/largetree011.gif","tiles/largetree012.gif"],\
                           ],lambda: Game.NullFunction(),0 ,5,10,10],\
                       [   [["tiles/smalltree001.gif","tiles/smalltree002.gif","tiles/smalltree003.gif"],\
                           ["tiles/smalltree004.gif","tiles/smalltree005.gif","tiles/smalltree006.gif"],\
                           ["tiles/smalltree007.gif","tiles/smalltree008.gif","tiles/smalltree009.gif"],\
                           ],lambda: Game.NullFunction(),0 ,5,10,10],\
                       [   [["tiles/mediumtree001.gif","tiles/mediumtree002.gif","tiles/mediumtree003.gif","tiles/mediumtree004.gif"],\
                           ["tiles/mediumtree005.gif","tiles/mediumtree006.gif","tiles/mediumtree007.gif","tiles/mediumtree008.gif"],\
                           ["tiles/mediumtree009.gif","tiles/mediumtree010.gif","tiles/mediumtree011.gif","tiles/mediumtree012.gif"],\
                           ],lambda: Game.NullFunction(),0 ,10,10,10],\
                          [ [[ "tiles/cottage_ul.gif","tiles/cottage_ur.gif"], [ "tiles/cottage_bl.gif","tiles/cottage_br.gif"]],lambda: Game.do_spikepit(),BLOCK_TRAVERSABLE ,1,10,10],\
                        ]

    stage2_background_tiles = [		  	
                        ["tiles/mossy_tile.gif",lambda: Game.NullFunction(),BLOCK_TRAVERSABLE,5,10,10],\
                        ["tiles/spikes.gif",lambda: Game.do_spikes(),BLOCK_TRAVERSABLE,5,10,10],\
                       ]

    stage3_foreground_tiles = [                        		  	
		  	[  [["tiles/smalltree001.gif","tiles/smalltree002.gif","tiles/smalltree003.gif"],\
                           ["tiles/smalltree004.gif","tiles/smalltree005.gif","tiles/smalltree006.gif"],\
                           ["tiles/smalltree007.gif","tiles/smalltree008.gif","tiles/smalltree009.gif"],\
                           ],lambda: Game.NullFunction(),0 ,5,10,10],\
                        ]

    stage3_background_tiles = [		  	                        
                        ["tiles/spikes.gif",lambda: Game.do_spikes(),BLOCK_TRAVERSABLE,200,10,10],\
                       ]

    stage_tiles = [ [stage1_foreground_tiles,stage1_background_tiles,"tiles/grass.gif"],\
                    [stage2_foreground_tiles,stage2_background_tiles,"tiles/grass.gif"],\
                    [stage3_foreground_tiles,stage3_background_tiles,"tiles/grass.gif"]]
                
#
# block functions
#
    def NullFunction():
        pass

    def do_lava():
        Player.hit(1)
        
    def do_health_potion():
        soundpath=os.path.join(os.getcwd(),"sounds/drinkpotion.wav")                                          
        Sound.PlaySound(soundpath)                      # play sound

        Player.AdjustHealthLevel(1)
                
    def do_extra_life_potion():
        print("extra life")
        
        soundpath=os.path.join(os.getcwd(),"sounds/extralife.wav")                                          
        Sound.PlaySound(soundpath)                      # play sound

        if Player.NumberOfLives < Player.MaximumNumberOfLives:
            Player.NumberOfLives += 1
            HUD.UpdateHUD()
    
    def do_spikepit():
         source_targetxy=int(Player.player_y*((Game.w/Tile.TILE_Y_SIZE)))+Player.player_x   
         Game.blockimages[source_targetxy].RestoreTileImage()                                 # restore tile

         Player.player_x=Player.player_start_x  
         Player.player_y=Player.player_start_y         
         Player.die();

    def do_spikes():         
         Player.hit(1)
         
    def do_quicksand():        
         Player.hit(1)
         
    def do_burning_flame():
        Player.hit(1)
        
    def do_stone_block():        
        pass
    
    def NullFunction():
        pass
	                     
    # do block action
    #
    def do_block(x,y):
        stagetiles=Game.stage_tiles[Game.CurrentStage-1]          # point to tiles for stage
        
        foregroundtiles=stagetiles[Game.STAGE_FOREGROUND_TILES]
        backgroundtiles=stagetiles[Game.STAGE_BACKGROUND_TILES]
        background=stagetiles[Game.STAGE_BACKGROUND]

        targetxy=int(y*((Game.w/Tile.TILE_Y_SIZE)))+x

        for object_type_list in backgroundtiles:
            if object_type_list[Game.BLK_FILENAME] == Game.blockimages[targetxy].currentimagename:         # if block matches              
              object_type_list[Game.BLK_FUNCTION]()                 # call function

        for object_type_list in foregroundtiles:           
             x_tiles=object_type_list[0]

             for tile_line in x_tiles:
                for tile in tile_line:
                   
                   if tile == Game.blockimages[targetxy].currentimagename:

                      #print("found=",tile)
                      object_type_list[Game.BLK_FUNCTION]()                 # call function

        # remove object from world
        
        for object_type_list in Game.item_tiles:           
            if object_type_list[Game.BLK_FILENAME] == Game.blockimages[targetxy].currentimagename:         # if block matches

              print("found item")
            
              object_type_list[Game.BLK_FUNCTION]()                 # call function

              if (object_type_list[Game.BLK_FLAGS] & Game.BLOCK_GENERATED):
                      Game.blockimages[targetxy].OverlayImage=None
                      Game.blockimages[targetxy].RestoreTileImage()
                      
                      return
                    
              return
        
    # 
   # check if player can move
    #
    
    def check_if_moveable(x,y):        
        if x < 0 or x >= int(Game.w/Tile.TILE_X_SIZE):          # check if x value is valid                       
           return -1

        if y < 0 or y >= int(Game.h/Tile.TILE_Y_SIZE)-Game.MenuBarHeight:          # check if y value is valid
           return -1

        if (x == Player.player_x) and (y == Player.player_y):            
            return -1
        
        targetxy=int(y*(int(Game.w/Tile.TILE_Y_SIZE)))+x

        stagetiles=Game.stage_tiles[Game.CurrentStage-1]          # point to tiles for stage
        
        foregroundtiles=stagetiles[Game.STAGE_FOREGROUND_TILES]
        backgroundtiles=stagetiles[Game.STAGE_BACKGROUND_TILES]
        background=stagetiles[Game.STAGE_BACKGROUND]
        
        for object_type_list in foregroundtiles:            
             tile_list=object_type_list[0]          # get tile list
             
             for x_tile in tile_list:
                for y_tile in x_tile:                    
                    if y_tile  == Game.blockimages[targetxy].currentimagename:                      
                      if (object_type_list[Game.BLK_FLAGS] & Game.BLOCK_TRAVERSABLE) == 0:                       
                       return -1                  
        
        for object_type_list in backgroundtiles:            
           if object_type_list[Game.BLK_FILENAME] == Game.blockimages[targetxy].currentimagename:

                 if (object_type_list[Game.BLK_FLAGS] & Game.BLOCK_TRAVERSABLE) == 0:                   
                   return -1

        if (Game.npcs != None) and (Game.npcs != []):        # check if NPC is at coordinates
                    for n in Game.npcs:
                        if n.CheckMoveableNPC(Player.player_x,Player.player_y) == -1:
                            return -1
                        
        return 0
                                            
              
    #
    # Move player
    #

    def player_move(self,x,y):
           print("check=",x,y)

           if Game.check_if_moveable(x,y) == -1:            # check if moveabke
               return -1

           for n in Game.npcs:
               if n.CheckMoveableNPC(x,y) == -1:
                   return -1
                
           source_targetxy=int(Player.player_y*((Game.w/Tile.TILE_Y_SIZE)))+Player.player_x
           dest_targetxy=int(y*((Game.w/Tile.TILE_Y_SIZE)))+x

           # change tile depending on which way the player is facing
    
           # rotate or copy image
        
           if x > Player.player_x:                                                 # moving east               
               Tile.rotate_clockwise_90degrees(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,self.blockimages[dest_targetxy].image)        
           elif x < Player.player_x:                                                 # moving west:               
               Tile.rotate_anticlockwise_90degrees(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,self.blockimages[dest_targetxy].image)
           elif y > Player.player_y:                                                 # moving south               
               Tile.flip_image_y(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,self.blockimages[dest_targetxy].image)
           elif y < Player.player_y:            
               Tile.copy_image(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,self.blockimages[dest_targetxy].image)
           else:
               Tile.copy_image(Player.PlayerImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,self.blockimages[dest_targetxy].image)

           self.blockimages[source_targetxy].RestoreTileImage()                                 # restore tile

           Player.player_x=x
           Player.player_y=y           

           print(x,y)
           
           Game.do_block(x,y)                                 # do block

    #
    # Keyboard event handlers
    #
    
    def move_player_right(self,event=None):
        Game.key_press_count += 1             # increment key count

        if Game.key_press_count > 1:          # key held down
            return

        Game.key_press_count=0
              
        Player.which_way_facing=Player.FACING_EAST        # change which way the player is facing

        if Player.player_x+1 >= (Game.w/Tile.TILE_X_SIZE):                  # at edge of world
            if Game.move_forward_locked == False:

                # if boss fight, generate boss fight
                # generate level otherwise
                if Game.CurrentAreaInStage == Game.MaxAreasInStage-1:
                    self.generateworld(Game.WORLD_BOSS_FIGHT,Player.player_x,Player.player_y)
                else:                    
                    self.generateworld(Game.WORLD_ORDINARY,Player.player_x,Player.player_y)

                Player.player_x=0
                Player.RestorePlayer()              # draw player sprite
                HUD.UpdateHUD()

                self.player_move(Player.player_x,Player.player_y)

                Game.CurrentAreaInStage += 1

                # if at end of stage
                
                if Game.CurrentAreaInStage == Game.MaxAreasInStage:
                    Game.CurrentStage += 1

                    if Game.CurrentStage > Game.MaxStages:          # at end of game
                        Game.WinScreen();
                        
                Game.move_forward_locked=True           # reset move forward locked flag
                
        else:                   
            if Game.check_if_moveable(Player.player_x+1,Player.player_y) == 0:                
                self.player_move(Player.player_x+1,Player.player_y)                # move player character
          
    def move_player_left(self,event=None):
          Game.key_press_count += 1             # increment key count

          if Game.key_press_count > 1:          # key held down
            return

          Game.key_press_count=0
        
          Player.which_way_facing=Player.FACING_WEST      # change way the player is facing 
                     
          if Game.check_if_moveable(Player.player_x-1,Player.player_y) == 0:    
                        self.player_move(Player.player_x-1,Player.player_y)                # move player character
            
    def move_player_up(self,event=None):
         Game.key_press_count += 1             # increment key count

         if Game.key_press_count > 1:          # key held down
            return
 
         Player.which_way_facing=Player.FACING_NORTH       # change which way the player is facing

         Game.key_press_count=0
        
         if Player.player_y-1 >= 1:
            print("move up=",Game.check_if_moveable(Player.player_x,Player.player_y-1))
            
            if Game.check_if_moveable(Player.player_x,Player.player_y-1) == 0:
                print("MOVE UP")
                self.player_move(Player.player_x,Player.player_y-1)
            
    def move_player_down(self,event=None):
         Game.key_press_count += 1             # increment key count

         if Game.key_press_count > 1:          # key held down
            return

         Game.key_press_count=0

         playertype=Player.player_types[Player.player_selected]

         Player.which_way_facing=Player.FACING_SOUTH       # change which way the player is facing
                              
         if Game.check_if_moveable(Player.player_x,Player.player_y+1) == 0:    
                      self.player_move(Player.player_x,Player.player_y+1)
                      
    #
    # Set starting position
    #
    def SetStartPos(self,canvas):
        counter=0
        tempx=0
        tempy=0

        playertype=Player.player_types[Player.player_selected]
        tile=playertype[Player.PLAYER_ENTRY_SPRITE]

        self.player_move(Player.player_start_x,Player.player_start_y)          # draw player


    #
    # Start new game
    def NewGameMenuItem():       
        if Game	.InGame == True:                 # only if in game
            result=messagebox.askyesno("Are you sure?","All progress will be lost! Do you want to start a new game?")

            if result == True:            
                Game.EndGame(Game)
                Game()
        else:                
                Game()


    #
    # Quit
    #
    def Quit():
        if Game.InGame == True:                 # only if in game
            result=messagebox.askyesno("Are you sure?","All progress will be lost! Do you want to exit?")

            if result == True:            
                os._exit(0)
        else:
            os._exit(0)
            
    def pick_up_object(self,event=None):
	    
           if Player.which_way_facing == Player.FACING_NORTH:                           # moving north            
               x=Player.player_x
               y=Player.player_y-1
           elif Player.which_way_facing == Player.FACING_WEST:                          # moving west            
               x=Player.player_x-1
               y=Player.player_y            
           elif Player.which_way_facing == Player.FACING_SOUTH:            
               x=Player.player_x
               y=Player.player_y+1           
           elif Player.which_way_facing == Player.FACING_EAST:
               x=Player.player_x+1
               y=Player.player_y           

           foregroundtiles=Game.stage_tiles[Game.STAGE_FOREGROUND_TILES]   
           targetxy=int(y*((Game.w/Tile.TILE_Y_SIZE)))+x
        
           for object_type_list in Game.item_tiles:
                print(object_type_list[self.BLK_FILENAME],Game.blockimages[targetxy].currentimagename)
                
                if object_type_list[self.BLK_FILENAME] == Game.blockimages[targetxy].currentimagename:         # if tile matches
                
                    if (object_type_list[self.BLK_FLAGS] & self.BLOCK_PICKUPABLE):       # tile can be picked up
                        Player.inventory[Player.CurrentInventorySelected]=object_type_list          # add to inventory                        
                        HUD.UpdateHUD()                                   # update hud

                        # remove object from world

                        self.blockimages[targetxy].ChangeTileImage("tiles/background.gif")     # set  image
                        self.blockimages[targetxy].img=self.blockimages[targetxy].image
                        self.blockimages[targetxy].OverlayImage=None
                        
                        return
                    
    def drop_object(self,event=None):
        inventory_entry=Player.inventory[Player.CurrentInventorySelected]

        if inventory_entry != None:
            for (x,y) in (Player.player_x+1,Player.player_y),(Player.player_x-1,Player.player_y),(Player.player_x,Player.player_y-1),(Player.player_x,Player.player_y+1):
               
             if Game.check_if_moveable(x,y) == 0:  
               # add object to world
           
               targetxy=int(y*((Game.w/Tile.TILE_Y_SIZE)))+x           
               Player.inventory[Player.CurrentInventorySelected]=None

               HUD.UpdateHUD()
               return

    def selected_character(player):      
        soundpath=os.path.join(os.getcwd(),"sounds/character_select.wav")                                          
        Sound.PlaySound(soundpath)                      # play sound

        Player.player_selected=player           # save player type number

        # destroy buttons
        
        countx=0
    
        for name in Player.player_types:                        
             Game.buttons[countx].destroy()             
             countx += 1

        # destroy images
        
        del Game.backgroundimage.image        
        del Game.choosecharimage

        Game.backgroundimage=None
        Game.choosecharimage=None

    #
    # create window
    #
    #
    def CreateWindow(self):
            Game.rootwindow=Tk()                             # create root window
            Game.rootwindow.title("Dungeon Doom")
                        
            
            Game.w=Game.rootwindow.winfo_screenwidth()      # set window size
            Game.h=Game.rootwindow.winfo_screenheight() - (Game.rootwindow.winfo_rooty() - Game.rootwindow.winfo_y())
            
            Game.rootwindow.geometry("%dx%d+0+0" % (Game.w,self.h))

            self.menubar=Menu(Game.rootwindow)                      # create menubar
        
            self.filemenu=Menu(self.menubar)
            self.menubar.add_cascade(label="File",menu=self.filemenu)

            self.filemenu.add_command(label="New Game",command=self.NewGameMenuItem)   
            self.filemenu.add_command(label="Quit",command=self.Quit)

            self.OptionsMenu=Menu(self.menubar)         # add options menu to menu bar
            self.menubar.add_cascade(label="Options",menu=self.OptionsMenu)
            self.OptionsMenu.add_command(label="Disable sound",command=lambda: Sound.ToggleSound(self))
            self.OptionsMenu.add_command(label="Disable music",command=lambda: Midi.ToggleMusic(self))

            if Sound.SoundPossible == False:                    # if no sound, disable menu
                self.OptionsMenu.entryconfig(1,state=DISABLED)
                self.OptionsMenu.entryconfig(1,label="Enable sound")

            if Midi.MusicPossible == False:                    # if no music, disable menu
                self.OptionsMenu.entryconfig(2,state=DISABLED)
                self.OptionsMenu.entryconfig(2,label="Enable music")

            self.helpmenu=Menu(self.menubar)
            self.menubar.add_cascade(label="Help",menu=self.helpmenu)

            self.helpmenu.add_command(label="Help",command=Help.help)   
            self.helpmenu.add_command(label="About",command=Help.about)

            Game.rootwindow.config(menu=self.menubar)    # add the menu bar
            
            self.max_y_blocks=(self.h/Tile.TILE_Y_SIZE)
            self.max_x_blocks=(Game.w/Tile.TILE_X_SIZE)
              
            # create canvas that covers the whole window
            Game.canvas = Canvas(Game.rootwindow,width = Game.rootwindow.winfo_screenwidth(), height = Game.rootwindow.winfo_screenheight())

    # Initialize game
    #
    def __init__(self):
        Game.InGame=True

        Game.blockimages=[]
        Game.CurrentArea=0
        Game.npcs = []
        Player.player_selected=-1
        Game.key_press_count=0
                
        # get an image object  
        Game.backgroundimage = PhotoImage(file="graphics/charselectbackground.gif")

        # resize image so it covers the window

        Game.backgroundimage=Game.backgroundimage.zoom(2)
        Game.backgroundimage.image=Game.backgroundimage       # save copy of image

        # put image onto canvas

        Game.canvas.create_image(0,0, anchor=NW, image=Game.backgroundimage)  
        Game.canvas.pack(expand=YES)

        Game.choosecharimage=PhotoImage(file="graphics/choosecharacter.gif")        # load image
        Game.canvas.create_image(350,0, anchor=NW, image=Game.choosecharimage)  
    
        count=0
        rowcount=0
        charx=200
        chary=300
        xcount=0

        Game.buttons= []
        
        for player in Player.player_types:
            player_graphic=player[Player.PLAYER_ENTRY_GRAPHIC]
            
            Game.images.append(PhotoImage(file=player_graphic))        # add image
    
            Game.buttons.append(Button(image=Game.images[count],command=lambda count=count: Game.selected_character(count)))
            Game.buttons[count].place(x=charx,y=chary)       

            count += 1
            charx += 200+50
            
            rowcount += 1
            
            if rowcount == self.ROW_COUNT:
                rowcount=0
                chary += 250
                
                xcount=0
                charx=(1*250)+300
        
        while 1:   
             if Player.player_selected != -1:         # continue from select screen to mainscreen
                break
                
             Game.rootwindow.update()

        
#*******************************************************
#
# redraw window and game world
#*******************************************************
        
        Game.screen_real_x_size=Game.w
        Game.screen_real_y_size=Game.h

        Player.player_x=2
        Player.player_y=2
        
        self.generateworld(Game.WORLD_ORDINARY,Player.player_x,Player.player_y)               
                
        playertype=Player.player_types[Player.player_selected]
        tile=playertype[Player.PLAYER_ENTRY_SPRITE]

        Player(Game.canvas,tile,Player.player_start_x,Player.player_start_y)                             # create player
        
        HUD(Game.canvas)
        
        self.SetStartPos(Game.canvas)
       
        
        Game.rootwindow.bind("w",self.move_player_up)            # bind keys to functions        
        Game.rootwindow.bind("W",self.move_player_up)
        Game.rootwindow.bind("A",self.move_player_left) 
        Game.rootwindow.bind("a",self.move_player_left)        
        Game.rootwindow.bind("S",self.move_player_down)
        Game.rootwindow.bind("s",self.move_player_down)
        Game.rootwindow.bind("D",self.move_player_right) 
        Game.rootwindow.bind("d",self.move_player_right)

        Game.rootwindow.bind("c",self.pick_up_object) 
        Game.rootwindow.bind("C",self.pick_up_object)

        Game.rootwindow.bind("e",self.drop_object) 
        Game.rootwindow.bind("E",self.drop_object)

        Game.rootwindow.bind("V",lambda event: Player.use_inventory_item(Player.CurrentInventorySelected))
        Game.rootwindow.bind("v",lambda event: Player.use_inventory_item(Player.CurrentInventorySelected))

        Game.rootwindow.bind("X", lambda event: Player.attack_handler())
        Game.rootwindow.bind("x", lambda event: Player.attack_handler())
                                
        Game.rootwindow.bind("1",lambda event:Player.select_inventory(1)) 
        Game.rootwindow.bind("2",lambda event: Player.select_inventory(2)) 
        Game.rootwindow.bind("3",lambda event: Player.select_inventory(3)) 
        Game.rootwindow.bind("4",lambda event: Player.select_inventory(4)) 
        Game.rootwindow.bind("5",lambda event: Player.select_inventory(5)) 
        Game.rootwindow.bind("6",lambda event: Player.select_inventory(6))
        Game.rootwindow.bind("7",lambda event: Player.select_inventory(7)) 
        Game.rootwindow.bind("8",lambda event: Player.select_inventory(8))
        Game.rootwindow.bind("9",lambda event: Player.select_inventory(9))
      
     #
     # main event loop
     #
        
        while 1:        
            if Game.InGame == True:
          #     if Midi.MusicEnabled == True and Midi.File != None:
            #        Midi.PlayNextPartOfMidiFile()

                # If the player is on a block that has an action
                # continue to do that action while they are on it
            
               Game.do_block(Player.player_x,Player.player_y)      # do block action for current position
                                                                                  
                # move the NPCs

               if (Game.npcs != None) and (Game.npcs != []):        # if there are NPCs, do the NPC actions
                    for n in Game.npcs:     # loop through npcs and move
                        
                        n.MoveNPC_Toward_Player()
               else:                                  
                       if Game.move_forward_locked == True:
                           HUD.DisplayMoveForwardMessage()
                           Game.move_forward_locked=False
                       
                       
            Game.rootwindow.update()
  
    #
    # Game over
    #

    def GameOver(self):
      if Game.InGame == False:      # not in game
          return
        
      Game.InGame=False              # clear in-game flag

      for char in ["W","A","S","D","w","a","s","d","C","c","d","D","V","v","X","x","0","1","2","3","4","5","6","7","8","9"]:       
           Game.rootwindow.unbind(char)                   # unbind keys
       
      HUD.DestroyHUD()
    
      Player.DestroyPlayer()            # destroy player
          
      if Midi.MusicPossible == True:
            Midi.MidiEnd()                        # Disable music

        # Destroy tiles
        
      Game.npcs=[]
      
      for b in Game.blockimages:                  
          b.ChangeTileImage("tiles/black.gif")
    
      # show game over graphic
      tilepath=os.path.join(os.getcwd(),"graphics/gameover.gif")
      self.image=PhotoImage(file=tilepath)        # load image
      
      # show game over graphic
      self.img=self.image       # save copy of image

        # put image onto canvas

      Game.canvas.create_image(Game.w/3,Game.h/4, anchor=NW, image=self.image)  
      Game.canvas.pack()

      soundpath=os.path.join(os.getcwd(),"sounds/gameover.wav")
      Sound.PlaySound(soundpath)

      Midi.wavfile=None
      
      print("Game over")

      print("InGame=",Game.InGame)

#
# Player wins
#
    def WinScreen(self):
      Game.InGame=False              # clear in-game flag

      HUD.DestroyHUD()
    
      Player.DestroyPlayer()            # destroy player
              
        # Destroy tiles
        
      Game.npcs=[]
      
      for b in Game.blockimages:                  
          b.ChangeTileImage("tiles/black.gif")

      for char in ["W","A","S","D","w","a","s","d","C","c","d","D","V","v","X","x","0","1","2","3","4","5","6","7","8","9"]:       
       Game.rootwindow.unbind(char)                   # unbind keys
       
      # show game over graphic
      tilepath=os.path.join(os.getcwd(),"graphics/winscreen_"+Player.PlayerType+".gif")
      self.image=PhotoImage(file=tilepath)        # load image
      
      # show game over graphic
      self.img=self.image       # save copy of image

        # put image onto canvas

      Game.canvas.create_image(0,0, anchor=NW, image=self.image)  
      Game.canvas.pack()

      soundpath=os.path.join(os.getcwd(),"sounds/win.wav")
      Sound.PlaySound(soundpath)

      Midi.wavfile=None
            
      if Midi.MusicPossible == True:
             Midi.StartMidiPlay("midi/ending.mid")    

      while 1:        
         if Midi.MusicEnabled == True and Midi.File != None:            
            Midi.PlayNextPartOfMidiFile()
                      
                       
         Game.rootwindow.update()     
#          
#
# Generate paths
#
    def generatepaths(x,y):
            paths = []
            pathcount=0

            PATH_X=0
            PATH_Y=1
            PATH_DIRECTION=2
            PATH_SIZE=3
            MAX_PRIMARY_PATH_SIZE=20
            MAX_SECONDARY_PATH_SIZE=10
            SPIKE_PROBABILITY=10
            
            # generate the paths
            
            for numberofpaths in range(0,int((Game.w/Tile.TILE_Y_SIZE))):
                
                whichway=random.randint(0,2)        # horizontal or vertical

                size=random.randint(1,MAX_PRIMARY_PATH_SIZE)

                paths += [[x,y,whichway,size]]

                # generate the path
                
                for count in range(0,size):
                  targetxy=int(y*((Game.w/Tile.TILE_Y_SIZE)))+x

                  pathcount += 1
                  
                 # print(x,y,targetxy,whichway)

                  Game.blockimages[targetxy].ChangeTileImage("tiles/slabs.gif")
                 
                  if whichway == 0:           # vertical up
                        y -= 1
                        if y <= 0:
                            whichway=1
                            y=1
                            break
                        
                  elif whichway == 1:           # vertical down
                        y += 1
                        if y >= int(Game.h/Tile.TILE_Y_SIZE):                            
                            y=1
                            whichway=1
                            break

                #  elif whichway == 2:           # horizontal left                        
                 #       x -= 1
                #        if x <= 0:                            
                 #           x=0
                 #           whichway=3
                 #           break

                  elif whichway == 2:           # horizontal right                        
                        x += 1
                        if x >= int(Game.w/Tile.TILE_X_SIZE):                            
                            x=0
                            break
  
                if whichway == 0:           # vertical up
                        whichway=random.randint(2,3)
                        
                elif whichway == 1:           # vertical down                        
                        whichway=random.randint(2,3)
        
                        
                elif whichway == 2:           # horizontal left                        
                        whichway=random.randint(0,1)

                elif whichway == 3:           # horizontal right
                        whichway=random.randint(0,1)
            
    # Generate secondary paths
            whichway=0
            
            for p in paths:
                # generate the new path perpendicular to the path

             if random.randint(0,10) == 2:                
                if (p[PATH_DIRECTION] == 0) or (p[PATH_DIRECTION] == 1):           # vertical
                    whichway=random.randint(2,3)
                else:
                    whichway=random.randint(0,1)
                    
                size=random.randint(1,MAX_SECONDARY_PATH_SIZE)

                # find start x and y of secondary path
                
                if whichway == 0:
                    startx=p[PATH_X]
                    starty=random.randint(p[PATH_Y],p[PATH_Y]+p[PATH_SIZE])

                    if starty >= int(Game.h/Tile.TILE_Y_SIZE):
                        starty=int(Game.h/Tile.TILE_Y_SIZE)-1

                elif whichway == 1:
                    startx=p[PATH_X]-p[PATH_SIZE]
                    starty=p[PATH_Y]
                    
                    if starty < 0:
                        starty=0

                elif whichway == 2:
                    startx=random.randint(p[PATH_X],p[PATH_X]+p[PATH_SIZE])
                    starty=p[PATH_Y]

                    if startx >= int(Game.w/Tile.TILE_X_SIZE):
                        startx=int(Game.w/Tile.TILE_X_SIZE)-1

                elif whichway == 3:
                    startx=random.randint(p[PATH_X]-p[PATH_SIZE],p[PATH_X])
                    starty=p[PATH_Y]
                    
                    if startx < 0:
                        startx=0

                 # generate the secondary paths
                 
                for count in range(0,5):
                  targetxy=int(starty*((Game.w/Tile.TILE_Y_SIZE)))+startx
                  
                  Game.blockimages[targetxy].ChangeTileImage("tiles/slabs.gif")

                  # point to next tile position
                  
                  if whichway == 0:
                    starty += 1
                    
                    if starty >= int(Game.h/Tile.TILE_Y_SIZE):          # at end
                        break

                  elif whichway == 1:
                    starty -= 1

                    if starty < 0:
                        break
                    
                  elif whichway == 2:
                    startx += 1

                    if startx >= int(Game.w/Tile.TILE_X_SIZE):
                        break
                    
                  elif whichway == 3:
                    startx -= 1

                    if startx < 1:
                        break
                      
                
    #
    # Generate items
    #
    def generateitems(self):
        stagetiles=Game.stage_tiles[Game.CurrentStage-1]          # point to tiles for stage
        
        foregroundtiles=stagetiles[Game.STAGE_FOREGROUND_TILES]
        backgroundtiles=stagetiles[Game.STAGE_BACKGROUND_TILES]
        background=stagetiles[Game.STAGE_BACKGROUND]

        count=Game.min_items
        	
        while count < Game.max_items/len(Game.item_tiles):
            itemcount=0

            whichitem=random.randint(0,len(Game.item_tiles)-1)            # which item to generate
            tile_line=Game.item_tiles[whichitem]

            while itemcount < tile_line[Game.BLK_MAX_ITEMS]:
            
                if random.randint(0,int(1000/tile_line[Game.BLK_GENPROB])) == 1:
                
                    tilefilename=tile_line[Game.BLK_FILENAME] # Get name of item
                    targetxy=random.randint(0,int((Game.w/Tile.TILE_X_SIZE)*(Game.h/Tile.TILE_Y_SIZE))) # Get location            

                    # check if item can be placed there
            
                    for tile in backgroundtiles:
                    # if found block and is overlayable
    
                        if ((Game.blockimages[targetxy].currentimagename == tile[Game.BLK_FILENAME]) and (tile[Game.BLK_FLAGS] & Game.BLOCK_OVERLAYABLE)) or Game.blockimages[targetxy].currentimagename == "tiles/slabs.gif":

                            Game.blockimages[targetxy].OverlayImage=PhotoImage(file=tilefilename)        # load image
                            Game.blockimages[targetxy].OverlayImage.img=Game.blockimages[targetxy].OverlayImage
                    
                            Tile.copy_image(Game.blockimages[targetxy].OverlayImage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)
                            Game.blockimages[targetxy].currentimagename=tilefilename
                
                            count += 1
                            
                itemcount += 1
            

    def generateforeground(self):
        x=0
        y=0

        stagetiles=Game.stage_tiles[Game.CurrentStage-1]          # point to tiles for stage
        
        foregroundtiles=stagetiles[Game.STAGE_FOREGROUND_TILES]
        backgroundtiles=stagetiles[Game.STAGE_BACKGROUND_TILES]
        background=stagetiles[Game.STAGE_BACKGROUND]
        
        while y < int(Game.h/Tile.TILE_Y_SIZE)-1:
          x=0
          
          while x < int(Game.w/Tile.TILE_X_SIZE)-1:           
           which_tile=random.randint(0,len(backgroundtiles)-1)
            
           tile_line=backgroundtiles[which_tile]
           
           tilefilename=tile_line[Game.BLK_FILENAME]

           if random.randint(1,tile_line[Game.BLK_GENPROB]) != 1:
               x += 1
             
               if x >= int(Game.w/Tile.TILE_X_SIZE)-1:
                y += 1                                
                break                        
           else:             
                x_count=random.randint(1,tile_line[Game.BLK_MAX_X_SIZE])
                y_count=random.randint(1,tile_line[Game.BLK_MAX_Y_SIZE])
            
                yc=0
                xc=0
                for yc in range(y,y+y_count):            
                    for xc in range(x,x+x_count):                    
                        targetxy=int(yc*((Game.w/Tile.TILE_Y_SIZE)))+xc

                        if targetxy >= int(Game.w/Tile.TILE_X_SIZE)*int(Game.h/Tile.TILE_Y_SIZE):
                            break

                        if (x != Player.player_start_x) and (y != Player.player_start_y):
                            if Game.blockimages[targetxy].currentimagename != "tiles/slabs.gif":
                                 
                                 Game.blockimages[targetxy].ChangeTileImage(tilefilename)
                                 Game.blockimages[targetxy].SetAttributes(tile_line[Game.BLK_FLAGS])
                                
                x += 1                 
                y += 1


    def generatebackground(self):
        x=0
        y=0

        stagetiles=Game.stage_tiles[Game.CurrentStage-1]          # point to tiles for stage
        
        foregroundtiles=stagetiles[Game.STAGE_FOREGROUND_TILES]
        backgroundtiles=stagetiles[Game.STAGE_BACKGROUND_TILES]
        background=stagetiles[Game.STAGE_BACKGROUND]
        
    # generate background

        x=0
        y=0
                
        
        while y < int(Game.h/Tile.TILE_Y_SIZE):    
          while x < int(Game.w/Tile.TILE_X_SIZE):
          
          # Generate foreground
           max_x_size=0

           which_tile=random.randint(0,len(foregroundtiles)-1)

           tiles=foregroundtiles[which_tile]

           if random.randint(1,tiles[Game.BLK_GENPROB]) != 1:
               x += 1
             
               if x >= int(Game.w/Tile.TILE_X_SIZE)-1:
                y += 1
                x=0
                
                break                        
           else:
               
            # Check if foreground item can be placed

            IsGeneratable=False
       
            tiles=foregroundtiles[which_tile]


            x_tiles=tiles[0]
            
            savex=x
            savey=y

            for tile_line in x_tiles:
                for tile in tile_line:        
                   targetxy=int(savey*((Game.w/Tile.TILE_Y_SIZE)))+savex
                   savex += 1
                   
                   if targetxy >= int(Game.w/Tile.TILE_X_SIZE)*int(Game.h/Tile.TILE_Y_SIZE):
                            break
                
                   if Game.blockimages[targetxy].currentimagename == background:                       
                       IsGeneratable=True
                   else:
                       IsGeneratable=False
                       break
                    
                savey += 1
                if IsGeneratable == False:
                      break
       
            x_tiles=tiles[0]

           # print("IsGeneratable=",IsGeneratable)
            
            if IsGeneratable == False:
                    x += 1

                    if x >= (Game.w/Tile.TILE_X_SIZE):
                       y += 1
                       x=0

                       if y >= int(Game.h/Tile.TILE_Y_SIZE):
                        break    
                       
            if IsGeneratable == True:
                  
                    x=savex
                    y=savey
                    
                    x_tiles=tiles[0]
                    oldx=x

                    savey=y

                    for tile_line in x_tiles:
                   
                        savex=x
                        for tile in tile_line:
        
                           if len(tile) > max_x_size:           # find end
                               max_x_size=len(tile_line)                    

                          # print(tile,x,y,count)
                           targetxy=int(y*((Game.w/Tile.TILE_Y_SIZE)))+x

                           if targetxy >= int(Game.w/Tile.TILE_X_SIZE)*int(Game.h/Tile.TILE_Y_SIZE):
                                break
                           
                           self.tempimage=PhotoImage(file=tile)        # load image
                           self.tempimage.img=self.tempimage
                    
                           Tile.copy_image(self.tempimage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)
                           
                           Game.blockimages[targetxy].currentimagename=tile
                           Game.blockimages[targetxy].SetAttributes(foregroundtiles[Game.BLK_FLAGS])
                           
                           x +=  1                    
                        y += 1
                        x=oldx+max_x_size+1
                    

                    if y >= int(Game.h/Tile.TILE_Y_SIZE)-1:
                        break
                    
                    y=savey
                      
                    if x >= int(Game.w/Tile.TILE_X_SIZE)-1:
                       y += len(x_tiles)
                       savey=y
                       x=0                
                                                       
        Game.number_of_items=self.generateitems()

    #
    # Generate world
    #
    def generateworld(self,worldtype,startx,starty):        
        generatable_items=[]
        Game.blockimages=[]
        Game.npcs=[]
        Player.player_start_x=startx
        Player.player_start_y=starty
        
        x=0
        y=0

        stagetiles=Game.stage_tiles[Game.CurrentStage-1]          # point to tiles for stage
        
        foregroundtiles=stagetiles[Game.STAGE_FOREGROUND_TILES]
        backgroundtiles=stagetiles[Game.STAGE_BACKGROUND_TILES]
        background=stagetiles[Game.STAGE_BACKGROUND]
    
# fill tile list
        
        while y < Game.h:
          while x < Game.w:
            
            Game.blockimages += [Tile(background,x,y)]
            		            
            x += Tile.TILE_X_SIZE
            
          y += Tile.TILE_Y_SIZE
          x=0
    
        Game.generatepaths(startx,starty)                       # generate paths
        
        #
        # If it's an ordinary world, generate the backround and foreground
        
        if worldtype == Game.WORLD_ORDINARY:
            Game.generateforeground(self)               # generate foreground
            Game.generatebackground(self)               # generate background

            if Midi.MusicPossible == True:
                Midi.PlayRandomMidi()

        # generate NPCs
        
        if (len(Game.npcs) < Game.min_npcs) and (Game.npcs != None):   
                    Game.number_of_npcs=(2^Game.CurrentStage)+1

                    Game.npcs=[]
                    
                    for n in range(0,Game.number_of_npcs):
                        npc_type=NPC.npc_types[random.randint(0,len(NPC.npc_types)-1)]
                        Game.npcs += [NPC(npc_type)]

         # generate boss NPC
         
        if worldtype == Game.WORLD_BOSS_FIGHT:
            npc_type=NPC.boss_npc_types[Game.CurrentStage]       
            Game.npcs += [NPC(npc_type)]

            if Midi.MusicPossible == True:
                Midi.StartMidiPlay("midi/bossfight.mid")

 
#
# Heads-up display
class HUD:
    barlabel=None
    
    #
    # Initialize heads-up display
    #
    def __init__(self,canvas):        
      HUD.UpdateHUD()
          
    def update_meter(icon,x,y,TotalNumberOfSegments,NumberOfSegments):

        #
        # show icon before bar
      
      targetxy=int(x)

      tilepath=os.path.join(os.getcwd(),"tiles/background.gif")
      Game.blockimages[targetxy].ChangeTileImage(tilepath)    # draw tile
                   
      tilepath=os.path.join(os.getcwd(),icon)

      image=PhotoImage(file=tilepath)
      Tile.copy_image(image,int(Tile.TILE_X_SIZE),int(Tile.TILE_Y_SIZE),Game.blockimages[targetxy].image)            

      targetxy += 1
      
# draw start

      tilepath=os.path.join(os.getcwd(),"tiles/healthbar_start.gif")

      image=PhotoImage(file=tilepath)
      Tile.copy_image(image,int(Tile.TILE_X_SIZE),int(Tile.TILE_Y_SIZE),Game.blockimages[targetxy].image)            
    
      targetxy += 1
      
    # draw middle
      nl=TotalNumberOfSegments
      
      while nl > 0:              
              tilepath=os.path.join(os.getcwd(),"tiles/healthbar_middle_empty.gif")

              image=PhotoImage(file=tilepath)
              Tile.copy_image(image,int(Tile.TILE_X_SIZE),int(Tile.TILE_Y_SIZE),Game.blockimages[targetxy].image)            

              nl -= 1
              targetxy += 1

              
     #
     # draw empty bar
     # draw end

      tilepath=os.path.join(os.getcwd(),"tiles/healthbar_end.gif")

      image=PhotoImage(file=tilepath)
      Tile.copy_image(image,int(Tile.TILE_X_SIZE),int(Tile.TILE_Y_SIZE),Game.blockimages[targetxy].image)            

            
    # fill in bar
      
      targetxy=x+2
      remainder_meter=NumberOfSegments
          
      while remainder_meter > 0:
    
         # draw different colors of health bar depending on level of meter
       
       if NumberOfSegments/TotalNumberOfSegments >= 0.7:
           tilepath=tilepath=os.path.join(os.getcwd(),"tiles/healthbar_middle.gif")                         
       elif NumberOfSegments/TotalNumberOfSegments >= 0.4 and NumberOfSegments/TotalNumberOfSegments < 0.7:
           tilepath=os.path.join(os.getcwd(),"tiles/healthbar_amber.gif")                   
       elif NumberOfSegments/TotalNumberOfSegments <= 0.4:
          tilepath=tilepath=os.path.join(os.getcwd(),"tiles/healthbar_red.gif")

       image=PhotoImage(file=tilepath)
       Tile.copy_image(image,int(Tile.TILE_X_SIZE),int(Tile.TILE_Y_SIZE),Game.blockimages[targetxy].image)            
       
       targetxy += 1
       remainder_meter -= 1
     
          
    #
    # draw heads-up display
    #
    def UpdateHUD():
         HUD_GAP_VAL = 2
         HUD_METER_MAX = 10
         
      # show inventory
      
         xpos=1

         TotalNumberOfSegments=Player.InventorySize         
         inventorycount=0

         while TotalNumberOfSegments != 0:              
              if Player.CurrentInventorySelected == TotalNumberOfSegments:     # if selected entry
                  tilepath=os.path.join(os.getcwd(),"tiles/inventory_selected.gif")                  
              else:
                  tilepath=os.path.join(os.getcwd(),"tiles/inventorybar.gif")

              image=PhotoImage(file=tilepath)
              Tile.copy_image(image,int(Tile.TILE_X_SIZE),int(Tile.TILE_Y_SIZE),Game.blockimages[xpos].image)            
              
              if Player.inventory != None and inventorycount < len(Player.inventory):
                inventory_entry=Player.inventory[inventorycount]              # get entry

                if inventory_entry != None:
                  # show small image                    
                    tilepath=os.path.join(os.getcwd(),inventory_entry[Game.BLK_FILENAME])         # get name
                
                    HUD.image=PhotoImage(file=tilepath)
                    HUD.image.img=HUD.image
          
                    HUD.halfimage=HUD.image.subsample(2,2)              # shrink image
                    HUD.halfimage.img=HUD.halfimage
                
                    Tile.copy_image(HUD.halfimage,int(Tile.TILE_X_SIZE/2),int(Tile.TILE_Y_SIZE/2),Game.blockimages[xpos].image)
                
                    inventorycount += 1

              xpos += 1
              TotalNumberOfSegments -= 1
        
         # show health meter        

         xpos += HUD_GAP_VAL
                       
         tile="tiles/heart"+str(Player.NumberOfLives)+".gif"
         
         meter_proportion=(Player.HealthLevel/Player.DefaultHealthLevel)*HUD_METER_MAX 
        
         HUD.update_meter(tile,xpos,0,HUD_METER_MAX,meter_proportion)

         # Copy the image to a tile so that it draws on top of the background rather than replacing the tile

         xpos += HUD_METER_MAX+(HUD_GAP_VAL*2)
         image=PhotoImage(file="tiles/stage"+str(Game.CurrentStage)+".gif") 
         Tile.copy_image(image,int(Tile.TILE_X_SIZE),int(Tile.TILE_Y_SIZE),Game.blockimages[xpos].image)
                       
    def DestroyHUD():
        return
    
    def DisplayMoveForwardMessage():
        HUD.moveimage=PhotoImage(file="graphics/movenext.gif")        # load image        
        Game.canvas.create_image((Game.w/8)*7,Tile.TILE_Y_SIZE, anchor=NW, image=HUD.moveimage)

        Sound.PlaySound("sounds/moveon.wav")
      
#
# Sound class
#
class Sound:
 SoundEnabled=True          # sound is enabled/possible
 SoundPossible=True

 SoundChunkSize=2048        #default number of bytes to use

 #
 # Play sound
 #
 def PlaySound(filename):
        buffer=[]
        wavfile=[]

        if Sound.SoundEnabled == False:
            return
        
        wavfile=wave.open(filename,"rb")                    # open wave file
        p=pyaudio.PyAudio()                                                     # create pyaudio instance

        stream=p.open(format=p.get_format_from_width(wavfile.getsampwidth()),channels=wavfile.getnchannels(),rate=wavfile.getframerate(),output=True)  # create output
    
        buffer=wavfile.readframes(Sound.SoundChunkSize)                    # read first frame

        while len(buffer) > 0:                          # while data avaliable
            buffer=wavfile.readframes(Sound.SoundChunkSize)               # read data
            stream.write(buffer)                       # write to audio device

        stream.stop_stream()                        # stop audio device

        p.close(stream);
        wavfile.close()                             # close wave file
    
#
# toggle sound
#
 def ToggleSound(self):     
  if Sound.SoundEnabled == True:                # if enabled, disable sound
   Sound.SoundEnabled=False

   self.OptionsMenu.entryconfig(1,label="Enable Sound")
  else:       
   Sound.SoundEnabled=True                      # if disabled, enable sound

   self.OptionsMenu.entryconfig(1,label="Disable Sound")

#
# NPC
#
class NPC:
    FACING_NORTH = 0
    FACING_SOUTH = 1
    FACING_EAST  = 2
    FACING_WEST  = 3

    WHICH_WAY_NORTH=0
    WHICH_WAY_SOUTH=1
    WHICH_WAY_EAST=2
    WHICH_WAY_WEST=3


# list entries
    NPC_TILE = 0
    NPC_ATTACK_TILE=1
    NPC_STAMINA = 2
    NPC_EVIL = 3
    NPC_MOVEODDS = 4
    NPC_GENODDS = 5
    NPC_MOVEWAIT = 6
    NPC_ATTACK_DAMAGE = 7
    NPC_NO_Y_FLIP = 8
    
    movement=0
    npc_tiles = []
        
    goblin_tiles = [[ "tiles/goblin.gif"] ]
    goblin_attack_tiles = [[ "tiles/goblin_attack.gif"] ]
    
    ork_tiles = [[ "tiles/ork1.gif","tiles/ork2.gif"],\
                 [ "tiles/ork3.gif","tiles/ork4.gif"]]    
    ork_attack_tiles = [[ "tiles/attack_ork1.gif","tiles/attack_ork2.gif"],\
                 [ "tiles/attack_ork3.gif","tiles/attack_ork4.gif"]]
    
    ogre_tiles = [[ "tiles/ogre1.gif","tiles/ogre2.gif"],\
                 [ "tiles/ogre3.gif","tiles/ogre4.gif"]]
    
    ogre_attack_tiles = [[ "tiles/ogre_attack1.gif","tiles/ogre_attack2.gif"],\
                 [ "tiles/ogre_attack3.gif","tiles/ogre_attack4.gif"]]
    
    troll_tiles = [[ "tiles/troll.gif" ]]
    troll_attack_tiles = [[ "tiles/troll_attack.gif" ]]    
    
    sk_tiles = [[ "tiles/skeleton.gif"] ]
    sk_attack_tiles = [[ "tiles/skeleton_attack.gif"] ]

    zombie_tiles = [[ "tiles/zombie.gif"] ]
    zombie_attack_tiles = [[ "tiles/zombie_attack.gif"] ]

    demon_tiles = [[ "tiles/demon.gif"]]
    demon_attack_tiles = [[ "tiles/demon_attack.gif"] ]

# boss tiles

    dragon_tiles = [ ["tiles/dragon_001.gif","tiles/dragon_002.gif","tiles/dragon_003.gif","tiles/dragon_004.gif"],\
                     ["tiles/dragon_005.gif","tiles/dragon_006.gif","tiles/dragon_007.gif","tiles/dragon_008.gif"],\
                     ["tiles/dragon_009.gif","tiles/dragon_010.gif","tiles/dragon_011.gif","tiles/dragon_012.gif"],
                     ["tiles/dragon_013.gif","tiles/dragon_014.gif","tiles/dragon_015.gif","tiles/dragon_016.gif"]]    
    dragon_attack_tiles = [ ["tiles/dragon_attack_001.gif","tiles/dragon_attack_002.gif","tiles/dragon_attack_003.gif","tiles/dragon_attack_004.gif"],\
                     ["tiles/dragon_attack_005.gif","tiles/dragon_attack_006.gif","tiles/dragon_attack_007.gif","tiles/dragon_attack_008.gif"],\
                     ["tiles/dragon_attack_009.gif","tiles/dragon_attack_010.gif","tiles/dragon_attack_011.gif","tiles/dragon_attack_012.gif"],
                     ["tiles/dragon_attack_013.gif","tiles/dragon_attack_014.gif","tiles/dragon_attack_015.gif","tiles/dragon_attack_016.gif"]]

    minotaur_tiles = [ [ "tiles/minotaur_001.gif","tiles/minotaur_002.gif","tiles/minotaur_003.gif","tiles/minotaur_004.gif","tiles/minotaur_005.gif","tiles/minotaur_006.gif","tiles/minotaur_007.gif"],
                    [ "tiles/minotaur_008.gif","tiles/minotaur_009.gif","tiles/minotaur_010.gif","tiles/minotaur_011.gif","tiles/minotaur_012.gif","tiles/minotaur_013","tiles/minotaur_014"],
                    [ "tiles/minotaur_015.gif","tiles/minotaur_016.gif","tiles/minotaur_017.gif","tiles/minotaur_018.gif","tiles/minotaur_019.gif","tiles/minotaur_020","tiles/minotaur_021"],
                    [ "tiles/minotaur_022.gif","tiles/minotaur_023.gif","tiles/minotaur_024.gif","tiles/minotaur_025.gif","tiles/minotaur_026.gif","tiles/minotaur_027","tiles/minotaur_028"],
                    [ "tiles/minotaur_029.gif","tiles/minotaur_030.gif","tiles/minotaur_031.gif","tiles/minotaur_032.gif","tiles/minotaur_033.gif","tiles/minotaur_034","tiles/minotaur_035"],
                    [ "tiles/minotaur_036.gif","tiles/minotaur_037.gif","tiles/minotaur_038.gif","tiles/minotaur_039.gif","tiles/minotaur_040.gif","tiles/minotaur_041","tiles/minotaur_042"],
                    [ "tiles/minotaur_043.gif","tiles/minotaur_044.gif","tiles/minotaur_045.gif","tiles/minotaur_046.gif","tiles/minotaur_047.gif","tiles/minotaur_048","tiles/minotaur_049"]]
    minotaur_attack_tiles = [ [ "tiles/minotaur_attack001.gif","tiles/minotaur_attack002.gif","tiles/minotaur_attack003.gif","tiles/minotaur_attack004.gif","tiles/minotaur_attack005.gif","tiles/minotaur_attack006.gif","tiles/minotaur_attack007.gif"],
                    [ "tiles/minotaur_attack008.gif","tiles/minotaur_attack009.gif","tiles/minotaur_attack010.gif","tiles/minotaur_attack011.gif","tiles/minotaur_attack012.gif","tiles/minotaur_attack013","tiles/minotaur_attack014"],
                    [ "tiles/minotaur_attack015.gif","tiles/minotaur_attack016.gif","tiles/minotaur_attack017.gif","tiles/minotaur_attack018.gif","tiles/minotaur_attack019.gif","tiles/minotaur_attack020","tiles/minotaur_attack021"],
                    [ "tiles/minotaur_attack022.gif","tiles/minotaur_attack023.gif","tiles/minotaur_attack024.gif","tiles/minotaur_attack025.gif","tiles/minotaur_attack026.gif","tiles/minotaur_attack027","tiles/minotaur_attack028"],
                    [ "tiles/minotaur_attack029.gif","tiles/minotaur_attack030.gif","tiles/minotaur_attack031.gif","tiles/minotaur_attack032.gif","tiles/minotaur_attack033.gif","tiles/minotaur_attack034","tiles/minotaur_attack035"],
                    [ "tiles/minotaur_attack036.gif","tiles/minotaur_attack037.gif","tiles/minotaur_attack038.gif","tiles/minotaur_attack039.gif","tiles/minotaur_attack040.gif","tiles/minotaur_attack041","tiles/minotaur_attack042"],
                    [ "tiles/minotaur_attack043.gif","tiles/minotaur_attack044.gif","tiles/minotaur_attack045.gif","tiles/minotaur_attack046.gif","tiles/minotaur_attack047.gif","tiles/minotaur_attack048","tiles/minotaur_attack049"]]

    ape_tiles = [ [ "tiles/ape001.gif","tiles/ape002.gif","tiles/ape003.gif","tiles/ape004.gif","tiles/ape005.gif","tiles/ape006.gif","tiles/ape007.gif"],
                    [ "tiles/ape008.gif","tiles/ape009.gif","tiles/ape010.gif","tiles/ape011.gif","tiles/ape012.gif","tiles/ape013","tiles/ape014"],
                    [ "tiles/ape015.gif","tiles/ape016.gif","tiles/ape017.gif","tiles/ape018.gif","tiles/ape019.gif","tiles/ape020","tiles/ape021"],
                    [ "tiles/ape022.gif","tiles/ape023.gif","tiles/ape024.gif","tiles/ape025.gif","tiles/ape026.gif","tiles/ape027","tiles/ape028"],
                    [ "tiles/ape029.gif","tiles/ape030.gif","tiles/ape031.gif","tiles/ape032.gif","tiles/ape033.gif","tiles/ape034","tiles/ape035"],
                    [ "tiles/ape036.gif","tiles/ape037.gif","tiles/ape038.gif","tiles/ape039.gif","tiles/ape040.gif","tiles/ape041","tiles/ape042"],
                    [ "tiles/ape043.gif","tiles/ape044.gif","tiles/ape045.gif","tiles/ape046.gif","tiles/ape047.gif","tiles/ape048","tiles/ape049"]]
    ape_attack_tiles = [ [ "tiles/ape_attack001.gif","tiles/ape_attack002.gif","tiles/ape_attack003.gif","tiles/ape_attack004.gif","tiles/ape_attack005.gif","tiles/ape_attack006.gif","tiles/ape_attack007.gif"],
                    [ "tiles/ape_attack008.gif","tiles/ape_attack009.gif","tiles/ape_attack010.gif","tiles/ape_attack011.gif","tiles/ape_attack012.gif","tiles/ape_attack013","tiles/ape_attack014"],
                    [ "tiles/ape_attack015.gif","tiles/ape_attack016.gif","tiles/ape_attack017.gif","tiles/ape_attack018.gif","tiles/ape_attack019.gif","tiles/ape_attack020","tiles/ape_attack021"],
                    [ "tiles/ape_attack022.gif","tiles/ape_attack023.gif","tiles/ape_attack024.gif","tiles/ape_attack025.gif","tiles/ape_attack026.gif","tiles/ape_attack027","tiles/ape_attack028"],
                    [ "tiles/ape_attack029.gif","tiles/ape_attack030.gif","tiles/ape_attack031.gif","tiles/ape_attack032.gif","tiles/ape_attack033.gif","tiles/ape_attack034","tiles/ape_attack035"],
                    [ "tiles/ape_attack036.gif","tiles/ape_attack037.gif","tiles/ape_attack038.gif","tiles/ape_attack039.gif","tiles/ape_attack040.gif","tiles/ape_attack041","tiles/ape_attack042"],
                    [ "tiles/ape_attack043.gif","tiles/ape_attack044.gif","tiles/ape_attack045.gif","tiles/ape_attack046.gif","tiles/ape_attack047.gif","tiles/ape_attack048","tiles/ape_attack049"]]
                 
    pig_tiles = [ [ "tiles/pigmonster_001.gif","tiles/pigmonster_002.gif","tiles/pigmonster_003.gif","tiles/pigmonster_004.gif","tiles/pigmonster_005.gif","tiles/pigmonster_006.gif","tiles/pigmonster_007.gif"],
                    [ "tiles/pigmonster_008.gif","tiles/pigmonster_009.gif","tiles/pigmonster_010.gif","tiles/pigmonster_011.gif","tiles/pigmonster_012.gif","tiles/pigmonster_013","tiles/pigmonster_014"],
                    [ "tiles/pigmonster_015.gif","tiles/pigmonster_016.gif","tiles/pigmonster_017.gif","tiles/pigmonster_018.gif","tiles/pigmonster_019.gif","tiles/pigmonster_020","tiles/pigmonster_021"],
                    [ "tiles/pigmonster_022.gif","tiles/pigmonster_023.gif","tiles/pigmonster_024.gif","tiles/pigmonster_025.gif","tiles/pigmonster_026.gif","tiles/pigmonster_027","tiles/pigmonster_028"],
                    [ "tiles/pigmonster_029.gif","tiles/pigmonster_030.gif","tiles/pigmonster_031.gif","tiles/pigmonster_032.gif","tiles/pigmonster_033.gif","tiles/pigmonster_034","tiles/pigmonster_035"],
                    [ "tiles/pigmonster_036.gif","tiles/pigmonster_037.gif","tiles/pigmonster_038.gif","tiles/pigmonster_039.gif","tiles/pigmonster_040.gif","tiles/pigmonster_041","tiles/pigmonster_042"],
                    [ "tiles/pigmonster_043.gif","tiles/pigmonster_044.gif","tiles/pigmonster_045.gif","tiles/pigmonster_046.gif","tiles/pigmonster_047.gif","tiles/pigmonster_048","tiles/pigmonster_049"]]
    pig_attack_tiles = [ [ "tiles/pig_attack__001.gif","tiles/pig_attack__002.gif","tiles/pig_attack__003.gif","tiles/pig_attack__004.gif","tiles/pig_attack__005.gif","tiles/pig_attack__006.gif","tiles/pig_attack__007.gif"],
                    [ "tiles/pig_attack__008.gif","tiles/pig_attack__009.gif","tiles/pig_attack__010.gif","tiles/pig_attack__011.gif","tiles/pig_attack__012.gif","tiles/pig_attack__013","tiles/pig_attack__014"],
                    [ "tiles/pig_attack__015.gif","tiles/pig_attack__016.gif","tiles/pig_attack__017.gif","tiles/pig_attack__018.gif","tiles/pig_attack__019.gif","tiles/pig_attack__020","tiles/pig_attack__021"],
                    [ "tiles/pig_attack__022.gif","tiles/pig_attack__023.gif","tiles/pig_attack__024.gif","tiles/pig_attack__025.gif","tiles/pig_attack__026.gif","tiles/pig_attack__027","tiles/pig_attack__028"],
                    [ "tiles/pig_attack__029.gif","tiles/pig_attack__030.gif","tiles/pig_attack__031.gif","tiles/pig_attack__032.gif","tiles/pig_attack__033.gif","tiles/pig_attack__034","tiles/pig_attack__035"],
                    [ "tiles/pig_attack__036.gif","tiles/pig_attack__037.gif","tiles/pig_attack__038.gif","tiles/pig_attack__039.gif","tiles/pig_attack__040.gif","tiles/pig_attack__041","tiles/pig_attack__042"],
                    [ "tiles/pig_attack__043.gif","tiles/pig_attack__044.gif","tiles/pig_attack__045.gif","tiles/pig_attack__046.gif","tiles/pig_attack__047.gif","tiles/pig_attack__048","tiles/pig_attack__049"]]
                    
    wolf_tiles = [ [ "tiles/wolf_001.gif","tiles/wolf_002.gif","tiles/wolf_003.gif","tiles/wolf_004.gif"],
                    [ "tiles/wolf_005.gif","tiles/wolf_006.gif","tiles/wolf_007.gif","tiles/wolf_008.gif"],
                    [ "tiles/wolf_009.gif","tiles/wolf_010.gif","tiles/wolf_011.gif","tiles/wolf_012.gif"],
                    [ "tiles/wolf_013.gif","tiles/wolf_014.gif","tiles/wolf_015.gif","tiles/wolf_016.gif"]]
    wolf_attack_tiles = [ [ "tiles/wolf_attack001.gif","tiles/wolf_attack002.gif","tiles/wolf_attack003.gif","tiles/wolf_attack004.gif"],
                    [ "tiles/wolf_attack005.gif","tiles/wolf_attack006.gif","tiles/wolf_attack007.gif","tiles/wolf_attack008.gif"],
                    [ "tiles/wolf_attack009.gif","tiles/wolf_attack010.gif","tiles/wolf_attack011.gif","tiles/wolf_attack012.gif"],
                    [ "tiles/wolf_attack013.gif","tiles/wolf_attack014.gif","tiles/wolf_attack015.gif","tiles/wolf_attack016.gif"]]
    
    spider_tiles = [ [ "tiles/spider_001.gif","tiles/spider_002.gif","tiles/spider_003.gif","tiles/spider_004.gif"],
                    [ "tiles/spider_005.gif","tiles/spider_006.gif","tiles/spider_007.gif","tiles/spider_008.gif"],
                    [ "tiles/spider_009.gif","tiles/spider_010.gif","tiles/spider_011.gif","tiles/spider_012.gif"],
                    [ "tiles/spider_013.gif","tiles/spider_014.gif","tiles/spider_015.gif","tiles/spider_016.gif"]]
    spider_attack_tiles = [ [ "tiles/spider_attack001.gif","tiles/spider_attack002.gif","tiles/spider_attack003.gif","tiles/spider_attack004.gif"],
                    [ "tiles/spider_attack005.gif","tiles/spider_attack006.gif","tiles/spider_attack007.gif","tiles/spider_attack008.gif"],
                    [ "tiles/spider_attack009.gif","tiles/spider_attack010.gif","tiles/spider_attack011.gif","tiles/spider_attack012.gif"],
                    [ "tiles/spider_attack013.gif","tiles/spider_attack014.gif","tiles/spider_attack015.gif","tiles/spider_attack016.gif"]]

    skeleton_boss_tiles = [ [ "tiles/skeleton_boss001.gif","tiles/skeleton_boss002.gif","tiles/skeleton_boss003.gif","tiles/skeleton_boss004.gif"],
                    [ "tiles/skeleton_boss005.gif","tiles/skeleton_boss006.gif","tiles/skeleton_boss007.gif","tiles/skeleton_boss008.gif"],
                    [ "tiles/skeleton_boss009.gif","tiles/skeleton_boss010.gif","tiles/skeleton_boss011.gif","tiles/skeleton_boss012.gif"],
                    [ "tiles/skeleton_boss013.gif","tiles/skeleton_boss014.gif","tiles/skeleton_boss015.gif","tiles/skeleton_boss016.gif"]]
    skeleton_boss_attack_tiles = [ [ "tiles/skeleton_boss_attack001.gif","tiles/skeleton_boss_attack002.gif","tiles/skeleton_boss_attack003.gif","tiles/skeleton_boss_attack004.gif"],
                    [ "tiles/skeleton_boss_attack005.gif","tiles/skeleton_boss_attack006.gif","tiles/skeleton_boss_attack007.gif","tiles/skeleton_boss_attack008.gif"],
                    [ "tiles/skeleton_boss_attack009.gif","tiles/skeleton_boss_attack010.gif","tiles/skeleton_boss_attack011.gif","tiles/skeleton_boss_attack012.gif"],
                    [ "tiles/skeleton_boss_attack013.gif","tiles/skeleton_boss_attack014.gif","tiles/skeleton_boss_attack015.gif","tiles/skeleton_boss_attack016.gif"]]

    darklord_tiles =[ [ "tiles/darklord_001.gif","tiles/darklord_002.gif","tiles/darklord_003.gif","tiles/darklord_004.gif","tiles/darklord_005.gif","tiles/darklord_006.gif","tiles/darklord_007.gif","tiles/darklord_008.gif"],
                     [ "tiles/darklord_009.gif","tiles/darklord_010.gif","tiles/darklord_011.gif","tiles/darklord_012.gif","tiles/darklord_013.gif","tiles/darklord_014.gif","tiles/darklord_015.gif","tiles/darklord_016.gif"],
                     ["tiles/darklord_017.gif","tiles/darklord_018.gif","tiles/darklord_018.gif","tiles/darklord_020.gif","tiles/darklord_021.gif","tiles/darklord_022.gif","tiles/darklord_023.gif","tiles/darklord_024.gif"],
                     ["tiles/darklord_025.gif","tiles/darklord_026.gif","tiles/darklord_027.gif","tiles/darklord_028.gif","tiles/darklord_029.gif","tiles/darklord_030.gif","tiles/darklord_031.gif","tiles/darklord_016.gif"],
                     ["tiles/darklord_032.gif","tiles/darklord_033.gif","tiles/darklord_034.gif","tiles/darklord_035.gif","tiles/darklord_036.gif","tiles/darklord_037.gif","tiles/darklord_038.gif","tiles/darklord_039.gif"],
                     ["tiles/darklord_040.gif","tiles/darklord_041.gif","tiles/darklord_042.gif","tiles/darklord_043.gif","tiles/darklord_044.gif","tiles/darklord_045.gif","tiles/darklord_046.gif","tiles/darklord_047.gif"],
                     ["tiles/darklord_048.gif","tiles/darklord_049.gif","tiles/darklord_050.gif","tiles/darklord_051.gif","tiles/darklord_052.gif","tiles/darklord_053.gif","tiles/darklord_054.gif","tiles/darklord_055.gif"],
                     ["tiles/darklord_056.gif","tiles/darklord_057.gif","tiles/darklord_058.gif","tiles/darklord_059.gif","tiles/darklord_060.gif","tiles/darklord_061.gif","tiles/darklord_062.gif","tiles/darklord_063.gif"]]
    darklord_attack_tiles =[ [ "tiles/darklord_attack_001.gif","tiles/darklord_attack_002.gif","tiles/darklord_attack_003.gif","tiles/darklord_attack_004.gif","tiles/darklord_attack_005.gif","tiles/darklord_attack_006.gif","tiles/darklord_attack_007.gif","tiles/darklord_attack_008.gif"],
                     [ "tiles/darklord_attack_009.gif","tiles/darklord_attack_010.gif","tiles/darklord_attack_011.gif","tiles/darklord_attack_012.gif","tiles/darklord_attack_013.gif","tiles/darklord_attack_014.gif","tiles/darklord_attack_015.gif","tiles/darklord_attack_016.gif"],
                     ["tiles/darklord_attack_017.gif","tiles/darklord_attack_018.gif","tiles/darklord_attack_018.gif","tiles/darklord_attack_020.gif","tiles/darklord_attack_021.gif","tiles/darklord_attack_022.gif","tiles/darklord_attack_023.gif","tiles/darklord_attack_024.gif"],
                     ["tiles/darklord_attack_025.gif","tiles/darklord_attack_026.gif","tiles/darklord_attack_027.gif","tiles/darklord_attack_028.gif","tiles/darklord_attack_029.gif","tiles/darklord_attack_030.gif","tiles/darklord_attack_031.gif","tiles/darklord_attack_016.gif"],
                     ["tiles/darklord_attack_032.gif","tiles/darklord_attack_033.gif","tiles/darklord_attack_034.gif","tiles/darklord_attack_035.gif","tiles/darklord_attack_036.gif","tiles/darklord_attack_037.gif","tiles/darklord_attack_038.gif","tiles/darklord_attack_039.gif"],
                     ["tiles/darklord_attack_040.gif","tiles/darklord_attack_041.gif","tiles/darklord_attack_042.gif","tiles/darklord_attack_043.gif","tiles/darklord_attack_044.gif","tiles/darklord_attack_045.gif","tiles/darklord_attack_046.gif","tiles/darklord_attack_047.gif"],
                     ["tiles/darklord_attack_048.gif","tiles/darklord_attack_049.gif","tiles/darklord_attack_050.gif","tiles/darklord_attack_051.gif","tiles/darklord_attack_052.gif","tiles/darklord_attack_053.gif","tiles/darklord_attack_054.gif","tiles/darklord_attack_055.gif"],
                     ["tiles/darklord_attack_056.gif","tiles/darklord_attack_057.gif","tiles/darklord_attack_058.gif","tiles/darklord_attack_059.gif","tiles/darklord_attack_060.gif","tiles/darklord_attack_061.gif","tiles/darklord_attack_062.gif","tiles/darklord_attack_063.gif"]]
    
                      
    #              Tile         Attack tile         Stamina Evil MoveOdds   GenOdds Wait Damage Allow Y flip
    
    npc_types = [[ goblin_tiles,goblin_attack_tiles,  1,     2,   4,         4,      0.20,   1, True],
                 [ ork_tiles,   ork_attack_tiles,     2,     2,   2,         4,      0.30,   1, True],
                 [ ogre_tiles,  ogre_attack_tiles,    1,     2,   3,         5,      0.40,   2, True],
                 [ troll_tiles, troll_attack_tiles,   3,     3,   3,         2,      0.30,   3, True],
                 [ sk_tiles,    sk_attack_tiles,      2,     1,   1,         3,      0.20,   1, True],
                 [ zombie_tiles,zombie_attack_tiles,  1,     1,   2,         3,      0.20,   1, True],
                 [ demon_tiles, demon_attack_tiles,   2,     1,   2,         3,      0.20,   2, True]]
    
    boss_npc_types = [[ skeleton_boss_tiles,skeleton_boss_attack_tiles,20,  6,   3,   4,      0.20,   5, False],
                      [ dragon_tiles,dragon_attack_tiles,    3,   5,   2,   4,      0.20,   25,  False],
                      [ wolf_tiles, wolf_attack_tiles,       2,   2,   2,   3,      0.20,   15,  False],
                      [ spider_tiles,spider_attack_tiles,    2,   2,   2,   3,      0.20,   20,  False],                     
                      [ minotaur_tiles,minotaur_attack_tiles,5,   6,   3,   4,      0.20,   5,  False],
                      [ ape_tiles,ape_attack_tiles,          5,   7,   4,   4,      0.20,   10,  False],
                      [ pig_tiles,pig_attack_tiles,          5,   8,   5,   4,      0.20,   15,  False],
                      [ darklord_tiles,darklord_attack_tiles,6,  10,   5,   4,      0.10,   50,  False],
                      ]
                      


    #
    # NPC constructor
    #
    def __init__(self,npc):        
        self.which_way_facing=0
        self.which_way_moving=0
        
        while 1:
            # Get location of NPC

            line=npc[self.NPC_TILE]
            
            self.x=random.randint(1,int(Game.w/Tile.TILE_X_SIZE)-1)
            self.y=random.randint(1,int(Game.h/Tile.TILE_Y_SIZE)-1)

            # fix y and y if out of bounds
            
            if(self.x > (Game.h/Tile.TILE_X_SIZE)):
               self.x -= len(line)-1

            if(self.y > (Game.h/Tile.TILE_Y_SIZE)):
               self.y -= len(line)
   
            # If NPC location OK
            
            if Game.check_if_moveable(self.x,self.y) == 0:
                break

        # Intialize NPC data
        
        self.npc_tiles=npc[self.NPC_TILE]
        self.attack_tiles=npc[self.NPC_ATTACK_TILE]
        self.stamina=npc[self.NPC_STAMINA]
        self.evil=npc[self.NPC_EVIL]
        self.movemodds=npc[self.NPC_MOVEODDS]*Game.CurrentStage
        self.genodds=npc[self.NPC_GENODDS]
        self.move_wait=npc[self.NPC_MOVEWAIT]
        self.attack_damage=npc[self.NPC_ATTACK_DAMAGE]*Game.CurrentStage        
        self.tick_count=int(time.perf_counter())+self.move_wait
        self.no_y_flip=npc[self.NPC_NO_Y_FLIP]
        
        targetxy=int(self.y*((Game.w/Tile.TILE_Y_SIZE)+1))+self.y   
        self.DrawNPC_Sprite(self.npc_tiles,self.x,self.y)             # draw sprite

    def CheckMoveableNPC(self,x,y):
        myx=self.x
        myy=self.y
        
        for y_list in self.npc_tiles:
             savex=myx
             
             for x_list in y_list:                
                if((myx == x) and (myy == y)):                
                   return -1
                
                myx += 1

             myx=savex
             
             myy += 1
                   
        return 0

    def MoveNPC_Toward_Player(self):       
        
        if time.perf_counter() < self.tick_count:
            return
        
        self.tick_count=time.perf_counter()+self.move_wait

        # if npc is next to the player, attack

        for (x,y) in (Player.player_x,Player.player_y+1),(Player.player_x,Player.player_y-1),(Player.player_x+1,Player.player_y),(Player.player_x-1,Player.player_y):          
          if  self.x == x and self.y == y:
            if random.randint(0,self.evil) == self.evil:                        
                                      
                # redraw sprite to face player
    
                   if Player.player_x > self.x:
                     self.which_way_facing=self.FACING_WEST
                   else:
                     self.which_way_facing=self.FACING_EAST

                   if self.no_y_flip == False:
                       if Player.player_y > self.y:
                         self.which_way_facing=self.FACING_NORTH
                       else:
                         self.which_way_facing=self.FACING_SOUTH
                         
                   self.DrawNPC_Sprite(self.attack_tiles,self.x,self.y)              # draw sprite
    
                   Player.hit(self.attack_damage*self.evil/Player.level)

            return
            
        # move otherwise
        
        if Player.player_y < self.y:
                if (self.CheckMoveableNPC(Player.player_x,Player.player_y-1) == -1):
                    return
                
                if (Game.check_if_moveable(self.x,self.y-1) == 0):
                   
                    #print("NPC move north")
                    self.MoveNPC(self.WHICH_WAY_NORTH)
                    return
                elif (Game.check_if_moveable(self.x-1,self.y) == 0):
                    #print("NPC move north")
                    self.MoveNPC(self.WHICH_WAY_EAST)
                    return
                elif (Game.check_if_moveable(self.x+1,self.y) == 0):
                    #print("NPC move north")
                    self.MoveNPC(self.WHICH_WAY_WEST)
                    return
                else:
                    self.MoveNPC(self.WHICH_WAY_SOUTH)
                    return
        elif Player.player_y > self.y:
                if (self.CheckMoveableNPC(Player.player_x,Player.player_y+1) == -1):
                    return
                
                if (Game.check_if_moveable(self.x,self.y+1) == 0):
                    #print("NPC move south")
                    self.MoveNPC(self.WHICH_WAY_SOUTH)
                    return
                elif (Game.check_if_moveable(self.x-1,self.y) == 0):
                    self.MoveNPC(self.WHICH_WAY_EAST)
                    return
                elif (Game.check_if_moveable(self.x+1,self.y) == 0):
                    self.MoveNPC(self.WHICH_WAY_WEST)
                    return
                else:
                    self.MoveNPC(self.WHICH_WAY_SOUTH)
                    return
 
        elif Player.player_x < self.x:
                if (self.CheckMoveableNPC(Player.player_x-1,Player.player_y) == -1):
                    return
                
                if (Game.check_if_moveable(self.x-1,self.y) == 0):
                    #print("NPC move west")
                    self.MoveNPC(self.WHICH_WAY_WEST)
                    return
                elif (Game.check_if_moveable(self.x,self.y-1) == 0):
                    self.MoveNPC(self.WHICH_WAY_SOUTH)
                    return
                elif (Game.check_if_moveable(self.x,self.y+1) == 0):
                    self.MoveNPC(self.WHICH_WAY_NORTH)
                    return
                else:
                    self.MoveNPC(self.WHICH_WAY_EAST)
                    return
        elif Player.player_x > self.x:
                if (self.CheckMoveableNPC(Player.player_x+1,Player.player_y-1) == -1):
                    return
                
                if (Game.check_if_moveable(self.x+1,self.y) == 0):
                    #print("NPC move east")
                    self.MoveNPC(self.WHICH_WAY_EAST)
                    return
                elif (Game.check_if_moveable(self.x,self.y-1) == 0):
                    self.MoveNPC(self.WHICH_WAY_SOUTH)
                    return
                elif (Game.check_if_moveable(self.x,self.y+1) == 0):
                    self.MoveNPC(self.WHICH_WAY_NORTH)
                    return
                else:
                    self.MoveNPC(self.WHICH_WAY_WEST)
                    return
        
    # Move NPC
    #
    def MoveNPC(self,which_way):
        ways = [ "","North","South","East","West" ]

        # Check if NPC is colliding with another NPC
        
        for n in Game.npcs:
                if n != self:
                    npc_x_length=0
                    npc_y_length=0
                
                    for tile_line in self.npc_tiles:
                        if len(tile_line) > npc_x_length:     # get x size of NPC
                            npc_x_length=len(tile_line)

                        npc_y_length += 1
                    

                    if which_way == self.WHICH_WAY_NORTH:
                        if (((self.x >= n.x) and (self.x <= (n.x+npc_x_length)))) and (((self.y-1 >= n.y) and (self.y <= (n.y+npc_y_length)))):                     
                             return -1

                    if which_way == self.WHICH_WAY_SOUTH:
                        if (((self.x >= n.x) and (self.x <= (n.x+npc_x_length)))) and (((self.y+1 >= n.y) and (self.y <= (n.y+npc_y_length)))):                     
                             return -1

                    if which_way == self.WHICH_WAY_EAST:
                        if (((self.x-1 >= n.x) and (self.x <= (n.x+npc_x_length)))) and (((self.y >= n.y) and (self.y <= (n.y+npc_y_length)))):                     
                             return -1

                    if which_way == self.WHICH_WAY_WEST:
                        if (((self.x+1 >= n.x) and (self.x <= (n.x+npc_x_length)))) and (((self.y >= n.y) and (self.y <= (n.y+npc_y_length)))):                     
                             return -1
                    
                        
        print("Move "+ways[which_way]+"=",self.x,self.y)
        self.restore_sprite_background(self.npc_tiles,self.x,self.y)
        
        if which_way == self.WHICH_WAY_NORTH:
            if self.y > 1:               
                 self.y -= 1
                 self.which_way_facing=self.FACING_NORTH               
        elif which_way == self.WHICH_WAY_SOUTH:
            if self.y < (Game.h-1):                
                 self.y += 1
                 self.which_way_facing=self.FACING_SOUTH                 
             
                 
        elif which_way == self.WHICH_WAY_EAST:
            if self.x < (Game.w/Tile.TILE_X_SIZE)-1:
                 self.x += 1
                 self.which_way_facing=self.FACING_EAST
            
        elif which_way == self.WHICH_WAY_WEST:
            if self.x > 0:              
                 self.x -= 1
                 self.which_way_facing=self.FACING_WEST                

        self.restore_sprite_background(self.npc_tiles,self.x,self.y)
        self.DrawNPC_Sprite(self.npc_tiles,self.x,self.y)              # draw sprite     
     
                    
    #
    # Restore sprite background
    #
    def restore_sprite_background(self,sprite,x,y):
        myx=x
        myy=y
        
        for y_list in sprite:
             savex=myx
             
             for x_list in y_list:                
                targetxy=int(myy*((Game.w/Tile.TILE_Y_SIZE)))+myx

                #print(myx,myy,targetxy)
                
                Game.blockimages[targetxy].RestoreTileImage()
                
                myx += 1

             myx=savex
             
             myy += 1
             
    def DestroyNPC(self):
        self.restore_sprite_background(self.npc_tiles,self.x,self.y)
                 
        del(self)
             
#
# draw npc sprite

    def DrawNPC_Sprite(self,sprite,x,y):    
     
     if self.which_way_facing == self.FACING_NORTH:
        
        for x_list in sprite:
            savex=x

            for y_list in x_list:
                targetxy=int(y*((Game.w/Tile.TILE_Y_SIZE)))+x
	
                self.tempimage=PhotoImage(file=y_list)                
                Tile.copy_image(self.tempimage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)
                x += 1
            
            x=savex
            y += 1
                 
     elif self.which_way_facing == self.FACING_SOUTH:
        ypos=0

        ss=copy.deepcopy(sprite)
        ss.reverse()

        for y_list in ss:
            savex=x
            
            for x_list in y_list:

                targetxy=int(y*((Game.w/Tile.TILE_Y_SIZE)))+x
                               
                self.tempimage=PhotoImage(file=x_list)                
                Tile.flip_image_y(self.tempimage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)                
                x += 1
            
            x=savex 
            y += 1
            ypos -= 1
             
     elif self.which_way_facing == self.FACING_EAST:
       if self.no_y_flip == True:    
        savey=y

        ss=copy.deepcopy(sprite)
        ss.reverse()
        
        for x_list in ss:
            for y_list in x_list:
                targetxy=int(y*((Game.w/Tile.TILE_Y_SIZE)))+x
                              
                self.tempimage=PhotoImage(file=y_list)                
                Tile.rotate_clockwise_90degrees(self.tempimage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)
                y += 1
            
            y=savey
            x += 1           

     elif self.which_way_facing == self.FACING_WEST:
       if self.no_y_flip == True:
        savey=y
   
        for x_list in sprite:
            for y_list in x_list:
                targetxy=int(y*((Game.w/Tile.TILE_Y_SIZE)))+x
                              
                self.tempimage=PhotoImage(file=y_list)                
                Tile.rotate_anticlockwise_90degrees(self.tempimage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)
                y += 1
            
            y=savey
            x += 1           

 
    def RestoreAfterAttack(self):
        self.DrawNPC_Sprite(self.npc_tiles,self.x,self.y)              # draw sprite

    def Invert_NPC_Sprite(sprite,x,y):    
        for x_list in sprite:
            savex=x

            for y_list in x_list:
                targetxy=int(y*((Game.w/Tile.TILE_Y_SIZE)))+x
	
                tempimage=PhotoImage(file=y_list)                
                Tile.invert_image(tempimage,Tile.TILE_X_SIZE,Tile.TILE_Y_SIZE,Game.blockimages[targetxy].image)
                x += 1
            
            x=savex
            y += 1

#
# Midi class
#
class Midi:
 MusicEnabled=True # MIDI
 MusicPossible=True
 	
 File=None
 midifiles = ["midi/boarshead.mid","midi/ending.mid","midi/patapan.mid","midi/three_ravens.mid","midi/wassail.mid" ]
 bossmidifile="midi/battlefield.mid"
 midichunksize=1
 PlayChunkCount=0
 
 #
 # Play random MIDI file
 #
 def PlayRandomMidi():
     Midi.StartMidiPlay(Midi.midifiles[random.randint(0,len(Midi.midifiles)-1)])

 #
 # Play MIDI file
 #
 def StartMidiPlay(filename):
   try:
                names=mido.get_output_names()               # get list of MIDI output devices
   except:
                print("MIDI: Can't find devices")
                return(-1)

   try:
                Midi.output = mido.open_output(names[0])    # open MIDI output device
   except:
                print("MIDI: Can't open output device")
                return(-1)

   Midi.File=filename
   
   Midi.mid=MidiFile(filename)                          # open midi
  
   Midi.mes=Midi.mid.play()

   Midi.midi_iter=iter(Midi.mes)
   
 def PlayNextPartOfMidiFile():
        Midi.PlayChunkCount += 1
        
        if Midi.PlayChunkCount < 10:
            return(0)
    
        for count in range(0,Midi.midichunksize):
                message=next(Midi.midi_iter)            # get next midi
                
                print(message)
                Midi.output.send(message)        

        return(0)

#
# End MIDI play
#
 def MidiEnd():
     Midi.output.close()
     
#
# toggle music
#
 def ToggleMusic(self):     
     if Midi.MusicEnabled == True:                # if enabled, disable sound
       Midi.MusicEnabled=False

       self.OptionsMenu.entryconfig(2,label="Enable music")
     else:       
       Midi.MusicEnabled=True                      # if disabled, enable sound

       self.OptionsMenu.entryconfig(2,label="Disable music")

#
# Help class
#
class Help:
    #
    # Display documentation
    #
    def help():        
          documentation="readme.txt"
          documentation=os.path.join(os.getcwd(),documentation)

          os.startfile(documentation, 'open')

   #
   # Display about dialog
   #
    def about():
          messagebox.showinfo("About","Dungeon Doom (c) Matthew Boote 2023")

#
# Main function
#

os.chdir(".")

Game.CreateWindow(Game)                         # create window
Game()                                   # create new game

