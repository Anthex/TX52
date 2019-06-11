import tkinter as tk  
from PIL import Image,ImageTk,ImageDraw, ImageFont
import sys

def selectPosition(existingFPs = []):
    coord = []
    root = tk.Tk()  
    root.geometry("1406x472")
    root.title("display image")  
    root.config(cursor="tcross")
    im=Image.open("plan2.png")  
    im = im.resize((1406,472),Image.ANTIALIAS)

    fnt = ImageFont.truetype('arial.ttf', 20)

    if existingFPs:
        draw = ImageDraw.Draw(im)
        for FP in existingFPs:
            draw.ellipse([FP.X*8.35+162-5,FP.Y*8.35+87-5,FP.X*8.35+162+5,FP.Y*8.35+87+5], fill='#0099ff', outline="#000000")
            draw.text((FP.X*8.35+162+10,FP.Y*8.35+87+10), str(FP.ID), font=fnt, fill="#0099ff", outline="#000000")
        del draw

    photo=ImageTk.PhotoImage(im)  
    cv = tk.Canvas(scrollregion=(0,0,500,500))  
    cv.pack(side='top', fill='both', expand='yes')  
    cv.create_image(0, 0, image=photo, anchor='nw')  

    def click(event):
        x, y = round((event.x - 162)/8.35,2), round((event.y - 87)/8.35,2)
        #print('{}, {}'.format(x, y))
        coord.append(x)
        coord.append(y)
        root.destroy()
        sys.stdout.flush()

    root.bind('<Button-1>', click)
    root.mainloop()
    return coord


