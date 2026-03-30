######################   
'''
Horror Movie Night Bingo Card Generator V.6.2

-fixed no lucky card bug
-added gurantee plus on bad and neutral combos
-added chance for evil tile
-cleaned up some tiles
-cleans up some backgrounds
'''


######################   

import glob
import os
import random
import shutil

from PIL import Image, ImageDraw, ImageFont
import PIL.ImageOps


import numpy as np

######################   
'''
Luck Functions
'''
###################### 

def assaign_lucky_star(luck, bounds):
    star = 'none'
    if  luck < bounds[0]:
        star = 'poopstar'
    if bounds[1] < luck <= bounds[2]:
        star = 'lillucky'
    if bounds[2] < luck <= bounds[3]:
        star = 'medlucky'
    if luck > bounds[3]:
        star = 'biglucky'
    return(star)

def chance_for_tip_over(): # small chance to tip luck total to next level 
    tips = [-2, -1, 0, 1, 2]
    odds = [.5, 1, 7, 1, .5]
    luck = random.choices(tips, weights = odds)[0]
    return(luck)

def difficulty_hold():
    diagnals_tiles = [0, 4, 6, 8, 16, 18, 20, 24] # non-variable
    easy_pics = ['G', 'S', 1, 5, 9, 11, 13, 16, 24, 25] # change based on stats
    hard_pics = ['B', 'N', 3, 6, 10, 12, 21] # change based on stats
    return (diagnals_tiles, easy_pics, hard_pics)

def luck_from_background(avg, diffiulty):
    luck = avg-int(diffiulty)
    if luck < -4: # caps the total luck
        luck = -4
    if luck > 4:
        luck = 4
    return (luck)

def luck_from_combos(in_list): 
    h, b, m, s = luck_hold()
    X = in_list.count('G')
    Y = in_list.count('B') + in_list.count('N')
    luck = (X * m) + (Y * -b)
    return(luck)

def luck_from_events(in_list):
    luck = 0
    h, b, m, s = luck_hold()
    X = in_list.count(1)
    if X > 1:
        luck += h
    if X < 1:
        luck -= h
    Y = in_list.count(89)
    luck += Y * m 
    return(luck)

def luck_from_tile_difficulty(order, combos):
    positive = ['S', 'G']
    negative = ['B', 'N']
    luck = 0
    h, b, m, s = luck_hold()
    diagnals, easy, hard = difficulty_hold()
    start = 0
    while start < len(order):
        num = order[start]
        bon = combos[start]
        if num in hard and bon in positive:
            luck += m
        if num in hard and bon in negative:
            luck -= b
        start += 1
    return(luck)

def luck_from_tile_location(order):
    luck = 0
    h, b, m, s = luck_hold()
    diagnals, easy, hard = difficulty_hold()
    for i, value in enumerate(order):
        if i == 12 and value in easy: # easy middle
            luck += m
        if i == 12 and value in hard: # hard middle
            luck -= b       
        if i == 12 and value == 1: # free space center
            luck += b
        if i in diagnals and value in easy:
            luck += s
        if i in diagnals and value in hard:
            luck -= m
    return(luck)

def luck_hold():
    huge = 1000
    big = 7
    moderate = 3.5
    small = 1.5
    return(huge, big, moderate, small)

def total_luck(order, combos, bg_avg, bg_diff):
    one = luck_from_combos(combos)
    two = luck_from_tile_location(order)
    three = luck_from_tile_location(combos)
    four = luck_from_tile_difficulty(order, combos)
    five = luck_from_events(order)
    six = luck_from_background(bg_avg, bg_diff)
    seven = chance_for_tip_over()
    all_lucks = [one, two, three, four, five, six, seven]
    total = sum(all_lucks)
    return(total)

######################   
'''
Random Choice Functions
'''
######################

def assaign_plus_tiles(path, files, bonuses, luck, bounds):
    num = chance_for_plus(luck, bounds)
    tiles = random.sample(range(0, 24), num)
    count = 0
    while count < len(bonuses):
        bonus = bonuses[count]
        if bonus == "B" or bonus == "N":
            if count not in tiles:
                tiles.append(count)
        count += 1
    add_pluses(path, files, tiles)
    return

def chance_for_plus(luck, bounds):
    choices = [1, 2, 3]
    if  luck < bounds[0]:
        choices = [0, 1, 2]
    if bounds[1] < luck <= bounds[2]:
        choices = [2, 3, 4]
    if bounds[2] < luck <= bounds[3]:
        choices = [3, 4, 5]
    if luck > bounds[3]:
        choices = [5, 6, 7]
    if bounds[0] == -1000:
        choices = [0, 0, 0]
    pluses = random.choices(choices, weights = [1, 3, 1])[0]
    return(pluses)

def chance_for_duplicate_tile(order):
    flip = random.randint(1, 50)
    if flip == 1:
        temp = order.copy() # duplicates list so 1 and 89 can be removed
        while 1 in temp: temp.remove(1) # prevents free space from being removed       
        while 89 in temp: temp.remove(89) # old extra tiles
        to_replace = random.choice(temp)
        temp.remove(to_replace)
        replace = random.choice(temp)
        loc = order.index(to_replace)
        order[loc] = replace
    return(order)

def chance_for_old_tile(order): # add complete tile from extras
    flip = random.randint(1, 25)
    if flip == 1:
        replace = random.randint(2, 25) # 2 skips freespace
        loc = order.index(replace)
        order[loc] = 89 # replaces random tiles blast from past holder
    return(order)

def chance_for_combo(order, odds):
    soda_tile = 9999
    if odds[0] != 0:
        soda_tile = random.randint(2, 25) # 2 skips freespace
    choices = ['G', 'N', 'B', '_'] # G = Good Combo, N = Neutral Combo, B = Bad Combo
    combos = random.choices(choices, weights = odds, k=25)
    for i, tile in enumerate(order):
        if tile == soda_tile:
            combos[i] = 'S'
        if tile == 1:
            combos[i] = '_'
    return(combos)

def chance_for_mega_lucky(order):
    flip = random.randint(1, 500)
    if flip == 1:
        while order[-1] == 1: #if last tiles is free space shuffle
            random.shuffle(order)
        order[-1] = 1 # replace last tile with a free space
    if flip == 500:
        loc = order.index(1)
        order[loc] = 89 # replace freespace with extra
    return(order)

def choose_background(info):
    if info[0] == 0:
        return[0, 0, 0, 0]
    else:   
        bg_choice = random.choice(info[1])
        image, shape, diffiulty, name = background_format(bg_choice)
        return [image, shape, diffiulty, name]

def choose_crop():
    #0 crop [X1,Y1,X2,Y2], 1 paste, 2 line
    choices = list(range(13))
    odds =  [3, 3, 3, 3, 1, 1, 1, 1, 1, 1, .5, .5, .5]
    choice = random.choices(choices, weights = odds)[0]
    #choice = 10 # for bug testing
    if choice < 10:
        if choice == 0: # bottom horiztonal w/ reverse chance
            one = [(0, 260, 232, 520), (0, 260), (0, 260, 475, 260)]
            two = [(232, 260, 475, 520), (232, 260), (0, 0, 0, 0)]
        if choice == 1: # top horiztonal w/ reverse chance
            one = [(0, 0, 232, 260), (0, 0), (0, 260, 475, 260)]
            two = [(232, 0, 475, 260), (232, 0), (0, 0, 0, 0)]
        if choice == 2: # right vertical w/ reverse chance
            one = [(237, 0, 475, 260), (237, 0), (237, 0, 237, 520)]
            two = [(237, 260, 475, 520), (237, 260), (0, 0, 0, 0)]
        if choice == 3: # left vertical w/ reverse chance
            one = [(0, 0, 237, 260), (0, 0), (237, 0, 237, 520)]
            two = [(0, 260, 237, 520), (0, 260), (0, 0, 0, 0)]
        if choice == 4: # vertical sides
            one = [(0, 0, 158, 520), (0, 0), (154, 0, 154, 520)]
            two = [(316, 0, 475, 520), (316, 0), (316, 0, 316, 520)]
        if choice == 5: # vertical middle
            one = [(158, 0, 330, 520), (158, 0), (154, 0, 154, 520)]
            two = [(0, 0, 0, 0), (0, 0), (328, 0, 328, 520)]
        if choice == 6: # left kiddy corner
            one = [(0, 0, 237, 260), (0, 0), (237, 0, 237, 520)]
            two = [(237, 260, 475, 520), (237, 260), (0, 260, 475, 260)]
        if choice == 7: # right kiddy corner
            one = [(237, 0, 475, 260), (237, 0), (237, 0, 237, 520)]
            two = [(0, 260, 237, 520), (0, 260), (0, 260, 475, 260)]
        if choice == 8: # hotiztonal sides
            one = [(0, 0, 475, 173), (0, 0), (0, 173, 475, 173)]
            two = [(0, 347, 475, 520), (0, 347), (0, 347, 475, 347)]
        if choice == 9: # hotiztonal middle
            one = [(0, 173, 475, 347), (0, 173), (0, 173, 475, 173)]
            two = [(0, 0, 0, 0), (0, 0), (0, 347, 475, 347)]
        return (2, [one, two])
    if choice > 9:
        if choice == 10: # inside box w/ vertical reverse chance
            one = [(88, 95, 387, 260), (88, 95), (89, 96, 386, 96)]
            two = [(88, 260, 387, 425), (88, 260), (89, 96, 89, 424)]
            three = [(0, 0, 0, 0), (0, 0), (89, 425, 386, 424)]
            four = [(0, 0, 0, 0), (0, 0), (386, 96, 386, 424)]
        if choice == 11: # inside box w/ horizontal reverse chance
            one = [(88, 95, 232, 425), (88, 95), (89, 96, 386, 96)]
            two = [(232, 95, 387, 425), (232, 95), (89, 96, 89, 424)]
            three = [(0, 0, 0, 0), (0, 0), (89, 425, 386, 424)]
            four = [(0, 0, 0, 0), (0, 0), (386, 96, 386, 424)]
        if choice == 12: # inside box
            one = [(0, 0, 475, 95), (0, 0), (89, 96, 386, 96)]
            two = [(0, 0, 88, 520), (0, 0), (89, 96, 89, 424)]
            three = [(0, 425, 475, 520), (0, 425), (89, 425, 386, 424)]
            four = [(387, 0, 475, 520), (387, 0), (386, 96, 386, 424)]
        return (4, [one, two, three, four])

def image_flip(num, var):
    try:
        choice = random.choice(var)
        out = str(num) + choice
    except:
        out = str(num)
    return (out)

def order_tiles(odds):
    order = random.sample(range(1, 26), 25)
    if odds != 0:
        order = chance_for_mega_lucky(order)
        order = chance_for_old_tile(order)
        order = chance_for_duplicate_tile(order)
    random.shuffle(order) # an extra shuffle just because
    return(order)

def random_images(folder_path, odds, var, garunteed, og_list):
    combos_list =  og_list.copy()
    imagelist = []
    base_order = order_tiles(odds)
    combos = chance_for_combo(base_order, odds)
    for i, tile in enumerate(base_order):
        combo =  combos[i]
        if tile == 89:
            new_tile = random.choice(combos_list)
            base = image_flip(new_tile, var)
            combos_list.remove(new_tile)
            move_to_temp(folder_path, base, 'extras/', str(100 + i), odds)
            base = str(100 + i)
            path, choice = check_for_combo(folder_path, base, combo, var, garunteed, combos_list)
            imagelist.append(path)
            if choice != '':
                combos_list.remove(choice)
        if tile != 89:
            base = image_flip(tile, var)
            move_to_temp(folder_path, base, 'tiles/', base, odds)
            path, choice = check_for_combo(folder_path, base, combo, var, garunteed, combos_list)
            imagelist.append(path)
            if choice != '':
                combos_list.remove(choice)
    return(imagelist, base_order, combos)

def check_for_combo(folder_path, base, combo_type, var, garunteed, combos_list):
    if combo_type == 'S':
        pick = random.choice(garunteed)
        combo_tile = image_flip(pick, var)
        out_path = combo_color_picker(folder_path, base, combo_tile, combo_type, 'garunteed/')
        choice = ''
    not_garunteed = ['G','N','B']
    if combo_type in not_garunteed:
        choice = random.choice(combos_list)
        combo_tile = image_flip(choice, var)
        out_path = combo_color_picker(folder_path, base, combo_tile, combo_type, 'extras/')
    if combo_type == '_':
        out_path = path_set(folder_path, base, 'temp/')
        choice = ''
    return(out_path, choice)

######################   
'''
Image Functions
'''
###################### 

def add_pluses(path, files, tiles):
    symbol_path = path_set(path, 'plus', 'lucky/')
    symbol = Image.open(symbol_path)
    symbol = symbol.resize((115, 115))
    for i, image in enumerate(files):
        if i in tiles:
            main_pic = Image.open(image)
            x = random.randint(10, 355)
            y = random.randint(10, 400)
            main_pic.paste(symbol, (x,y), mask=symbol)
            #main_pic.show()
            main_pic = main_pic.save(image)
    return

def add_background_info(path, image, draw, cols, size, title, shape, font_name):
    shape_path = path_set(path, shape, 'over/shape/')
    shape_image = Image.open(shape_path)
    font = ImageFont.truetype(font=font_name, size=50)
    left, top, right, bottom = font.getbbox(title)
    draw.text(((cols*size)/2,1325), title, fill = (0,0,0), font=font, anchor="mm")
    newsize = (45, 45)
    shape_image = shape_image.resize(newsize)
    shape_place = int((cols*size)/2 + (right/2) + 25)
    image.paste(shape_image, (shape_place,1305), mask=shape_image)
    return(image)

def add_background_shape(folder_path, image, draw, cols, size, info, font_name):
    bg = info[0]
    shape = info[1]
    title = info[3]
    if bg == 0:
        return(image)
    else:
        bg_path = path_set(folder_path, bg, 'over/background/')
        background_image = Image.open(bg_path)
        image.paste(background_image, (0,0), mask=background_image)
        outimage = add_background_info(folder_path, image, draw, cols, size, title, shape, font_name)
        return(outimage)

def add_lucky_star(folder_path, card, star):
    star_path = path_set(folder_path, star, 'lucky/')
    luckystar = Image.open(star_path)
    luckystar = luckystar.resize((125, 125))
    card.paste(luckystar, (0,0), mask=luckystar)
    return(card)

def combo_color_picker(folder_path, base, combo_tile, combo, name):
    try:
        if combo == 'G' or 'S':
            path = create_combo_tile(folder_path, base, combo_tile, name, (4, 217, 255))
        if combo == 'N':
            path = create_combo_tile(folder_path, base, combo_tile, name, (57, 255, 20))
        if combo == 'B':
            path = create_combo_tile(folder_path, base, combo_tile, name, (247, 33, 25))
    except:
        print('something went wrong')
        path = path_set(folder_path, base, 'temp/')
    return(path)
    
def create_combo_tile(folder_path, base, combo, name, color):
    output = base + combo
    main_pic_path = path_set(folder_path, base, 'temp/')
    combo_pic_path = path_set(folder_path, combo, name)
    main_pic = Image.open(main_pic_path)
    combo_pic = Image.open(combo_pic_path)
    counters, data = choose_crop()
    start = 0
    while start < counters:
        crop_shape = data[start][0]
        paste_shape = data[start][1]
        cropped = combo_pic.crop(crop_shape)
        cropped = image_flips(cropped)
        flip = random.randint(1, 15)
        if flip == 1:        
            main_pic.paste(cropped, (paste_shape), mask=cropped) # Will make trasnpartent
        else:
            Image.Image.paste(main_pic, cropped, (paste_shape))
        draw = ImageDraw.Draw(main_pic)
        start += 1
    count = 0
    while count < counters:
        draw.line(xy=data[count][2], fill = color, width = 6)
        count += 1
    #main_pic.show()
    output_path = path_set(folder_path, output, 'temp/')
    main_pic = main_pic.save(output_path)
    return(output_path)

def create_evil_tile(source_path, destination_path):
    image = Image.open(source_path)
    r,g,b,a = image.split()
    rgb_image = Image.merge('RGB', (r,g,b))
    #inverted_image = PIL.ImageOps.invert(rgb_image)
    flip = random.randint(0, 255)
    inverted_image = PIL.ImageOps.solarize(rgb_image, threshold=flip)
    r2,g2,b2 = inverted_image.split()
    final_transparent_image = Image.merge('RGBA', (r2,g2,b2,a))
    flipped_image = PIL.ImageOps.mirror(final_transparent_image)
    flipped_image.save(destination_path)

def draw_bingo_card(folder_path, title_info, size, images, bkgnd_info):
    title = title_info[0]
    font = title_info[1]
    font_name = title_info[2]
    rows = int(5)
    cols = int(5)
    base_image = Image.new('RGB', (cols*size+50, rows*size+100), (255,255,255))
    draw = ImageDraw.Draw(base_image)
    base_image = add_background_shape(folder_path, base_image, draw, cols, size, bkgnd_info, font_name)
    i = 0
    for y in range(rows):
        if i >= len(images):
            break
        y *= size
        for x in range(cols):
            x *= size
            img = images[i]
            base_image.paste(img, (x+25, y+50, x+size+25, y+size+50), mask=img)
            i += 1     
    draw.text(((cols*size+50)/2,25), title, fill = (0,0,0), font=font, anchor="mm") # draw card title
    draw_table(draw, 25, 50, rows, cols, size) # draw table  
    return (base_image)

def draw_table(draw, posx, posy, rows, cols, size):
    for y in range(rows+1):
        draw.line(((posx,posy+y*size),(posx+cols*size,posy+y*size)),fill='black',width=7)
    for x in range(cols+1):
        draw.line(((posx+x*size,posy),(posx+x*size,posy+rows*size)),fill='black',width=7)

def image_flips(image):
    flips = random.choices(['A', 'B','C'], weights = [150, 10, 5], k=2)
    for flip in flips:
        if flip == 'B':
            image = image.transpose(method=Image.FLIP_LEFT_RIGHT)
        if flip == 'C':
            image = image.transpose(method=Image.FLIP_TOP_BOTTOM)
    return(image)

def open_images(paths):
    size = int(250)
    images = [Image.open(name).resize((size, size)) for name in paths]
    return(images, size)

######################   
'''
Processsing Functions
'''
###################### 

def assaign_bounds(odds): # boundaries for determining how lucky a card is
    bottom = 0
    lower = odds
    upper = odds * 2
    top = 500
    return [bottom, lower, upper, top]

def background_format(image):
    image = image.rstrip('.png')
    parts = image.split('_')
    shape =  parts[0]
    diffiulty = parts[1]
    name = shape.replace('-', ' ')
    name = name.upper()
    return (image, shape, diffiulty, name)

def background_preprocessor(path):
    shapes = os.listdir(path + '/pic/over/background/')
    difficulty_list = []
    for shape in shapes:
        bg, shape, diffiulty, name = background_format(shape)
        difficulty_list.append(int(diffiulty))
    try:
        avg = int(sum(difficulty_list) / len(difficulty_list))
    except:
        return((0, []))
    return((avg, shapes))

def card_generator(stop, data):
    path, title, var, odds, bounds, bkgnd_info, garun, extra_info = split_process_data(data)
    start = 0
    card_numbers = random.sample(range(100 + stop), stop)
    lucky_values = []
    remove(f'output/*')
    while start < stop:
        card_name = card_numbers[start]
        filenames, order, bonuses = random_images(path, odds, var, garun, extra_info)
        bg_choice = choose_background(bkgnd_info)
        luck = total_luck(order, bonuses, bkgnd_info[0], bg_choice[2])
        star = assaign_lucky_star(luck, bounds)
        assaign_plus_tiles(path, filenames, bonuses, luck, bounds)
        images, size = open_images(filenames)
        card = draw_bingo_card(path, title, size, images, bg_choice)
        card = add_lucky_star(path, card, star)
        card.save(f'output/card_{card_name}.jpg')
        lucky_values.append(luck)
        remove(f'pic/temp/*')
        start += 1
    return(start, lucky_values)

def determine_odds(probablity):
    GCC = probablity / 100 # good combo chance
    NCC = GCC * 0.03846 # 1:25 is neutral combo chance
    BCC = GCC * 0.03846 # 1:25 is bad combo chance
    no_combo = 1 - GCC -  BCC - NCC
    odds = [GCC, NCC, BCC, no_combo]
    return(odds)

def extras_format(image):
    name = image.rstrip('.png')
    number = name[:-1]
    return (number)

def extras_preprocessor(path, name):
    extras = os.listdir(path + name)
    extras_list = []
    for extra in extras:
        number = extras_format(extra)
        extras_list.append(number)
    unique_list = list(set(extras_list)) 
    return(unique_list)

def find_font_size(path, title):
    fonts = os.listdir(path + '/font/')
    font_name =  'font/' + fonts[0]
    size = 50
    check = False
    while check == False:
        font = ImageFont.truetype(font=font_name, size=size)
        left, top, right, bottom = font.getbbox(title)
        if right > 1290:
            size -= 2 # make font 2 points smaller every time the title is bigger than the card
        else:
            check = True
    return(font, font_name)

def find_variants(path, name):
    tiles = os.listdir(path + name)
    variants = []
    for tile in tiles:
        name = tile.rstrip('.png')
        letter = name[-1]
        variants.append(letter)
    unique_list = list(set(variants))
    return(unique_list)

def move_to_temp(path, in_name, start_path, out_name, odds):
    source_path = path_set(path, in_name, start_path)
    destination_path = path_set(path, out_name, 'temp/')
    flip = random.randint(1, 45)
    if flip == 1 and odds[0] != 0 and in_name != "1A" and in_name != "1B":
        create_evil_tile(source_path, destination_path)
    else:   
        shutil.copy(source_path, destination_path)

def path_set(project_path, name, folder):
    path = project_path + '/pic/' + folder + name + ".png"
    return(path)

def remove(this):
    files = glob.glob(this)
    for f in files:
        os.remove(f)

def split_process_data(data):
    path = data[0]
    title = data[1]
    var = data[2]
    odds = data[3]
    bounds = data[4]
    bkgnd_info = data[5]
    garun = data[6] # path to garuenteed tiles
    extra_info = data[7]
    return (path, title, var, odds, bounds, bkgnd_info, garun, extra_info)

def start_processor(advanced, blurb, prob):
    project_path = os.path.dirname(os.path.abspath(__file__))
    title =  title_maker(project_path, blurb)
    variants = find_variants(project_path, '/pic/tiles/')
    if advanced == False:
        odds = [0, 0, 0, 1]
        bounds = [-1000, 1000, 1000, 1000]
        bg_options = [0, [], []]
        garunteed = []
        extras = []
    if advanced == True:
        odds = determine_odds(prob)
        bounds = assaign_bounds(odds[0]*100)
        bg_options = background_preprocessor(project_path)
        garunteed = extras_preprocessor(project_path, '/pic/garunteed/')
        extras = extras_preprocessor(project_path, '/pic/extras/')
    processes = [project_path, title, variants, odds, bounds, bg_options, garunteed, extras]
    return(processes)

def title_maker(path, blurb):
    folders = os.listdir(path + '/watch/')
    movies = []
    for folder in folders:
        caps = folder.upper()
        parts = caps.split('..')
        if len (parts) == 1:
            movie = caps.split(' (')[0]
        else:
            movie = parts[1].split(' (')[0]
        movies.append(movie)
    title = ''
    for movie in movies:
            title = title + " & " + movie
    title = title[3:] # Remove first &
    if len(blurb) > 0:
        title = blurb + ' ' +  title
    font, font_name = find_font_size(path, title)
    return([title, font, font_name])

######################

# random number of possible find more tiles


#look at periods in 


def run():
    Extra_Title_Blurb = ""
    
    Cards = 4 # how many cards to generate
    Complex_Mode_On = True
    Combo_Probability = 15
    
    data = start_processor(Complex_Mode_On, Extra_Title_Blurb, Combo_Probability)
    while True:
        start, lucky_values = card_generator(Cards, data)
        if max(lucky_values) > data[3][0] * 100 + 1 or Complex_Mode_On == False: # if luck is on garunteees at least one lucky card
            break
    print('complete')
run()

#": on extra title

# reverse on extras