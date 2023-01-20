import random

#get a random color in hex format
def get_random_hex_color():
   
    return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

def get_color_by_group(group_size:int, player_number:int):
    '''
    return a color and namy by group number
    '''    

    label = ""
    color = ""

    if player_number % group_size == 0:
        label = "Blue"
        color = "#6495ED"
    elif player_number % group_size == 1:
        label = "Orange"
        color = "#FF8C00"
    elif player_number % group_size == 2:
        label = "Purple"
        color = "#800080"
    elif player_number % group_size == 3:
        label = "Gold"
        color = "#FFD700"    

    return {"label":label, "color":color}
