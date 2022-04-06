
'''
format minutes to hours and minutes
'''
import  math

def format_minutes(minutes) -> str:
    '''
    format minutes to hours and minutes
    '''
    v = f'{math.floor(minutes/60)}'

    if v == "1":
        v += "hr "
    else:
        v += "hrs "

    if minutes%60 != 0 :
        v += f' {minutes%60}'

        if minutes%60 == 1:
            v += "min"
        else:
             v += "mins"

    return v