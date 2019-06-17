import tkinter as tk  
from PIL import Image,ImageTk,ImageDraw, ImageFont, ImageColor 
import sys
import math


def selectPosition(existingFPs = []):
    coord = []
    root = tk.Tk()  
    root.geometry("1406x472")
    root.title("display image")  
    root.config(cursor="tcross")
    im=Image.open("plan2.png")  
    im = im.resize((1406,472),Image.ANTIALIAS)

    draw = ImageDraw.Draw(im)
    fnt = ImageFont.truetype('arial.ttf', 20)

    if existingFPs:
        for FP in existingFPs:
            #draw.ellipse([FP.X*8.35+162-5,FP.Y*8.35+87-5,FP.X*8.35+162+5,FP.Y*8.35+87+5], fill='rgb({},{},{})'.format(int(abs((FP.vec.RSSI1))), int(abs(FP.vec.RSSI2)), int(abs(FP.vec.RSSI3))), outline="#000000")
            draw.ellipse([FP.X*8.35+162-5,FP.Y*8.35+87-5,FP.X*8.35+162+5,FP.Y*8.35+87+5], fill='#0099ff', outline="#000000")
            draw.text((FP.X*8.35+162+5,FP.Y*8.35+87+5), str(FP.ID), font=fnt, fill="#0099ff", outline="#000000")
            """
            fnt = ImageFont.truetype('arial.ttf', 15)
            draw.text((FP.X*8.35+162+10,FP.Y*8.35+87-10), FP.toString(), font=fnt, fill="#0099ff", outline="#000000")
            """

    photo=ImageTk.PhotoImage(im)  
    cv = tk.Canvas()  
    cv.pack(side='top', fill='both', expand='yes')  
    cv.create_image(0, 0, image=photo, anchor='nw')  

    def click(event):
        x, y = round((event.x - 162)/8.35,2), round((event.y - 87)/8.35,2)
        #print('{}, {}'.format(x, y))
        coord.append(x)
        coord.append(y)
        root.destroy()
        sys.stdout.flush()

    """
    def hover(event):
        x, y = round((event.x - 162)/8.35,2), round((event.y - 87)/8.35,2)
        if existingFPs:
            for fp in existingFPs:
                #draw.ellipse([FP.X*8.35+162-5,FP.Y*8.35+87-5,FP.X*8.35+162+5,FP.Y*8.35+87+5], fill='#00ff00', outline="#000000")
                #draw.text((FP.X*8.35+162+5,FP.Y*8.35+87+5), str(FP.ID), font=fnt, fill="#0099ff", outline="#000000")
                if abs((event.x - 162)/8.35 - fp.X) < 10 and abs((event.y - 87)/8.35 - fp.Y) < 10:
                    draw.text((fp.X*8.35+162+5,fp.Y*8.35+87+5), str("aaaaa"), font=fnt, fill="#0099ff", outline="#000000")

        photo=ImageTk.PhotoImage(im)  
        #cv.delete("all")
        cv.create_image(0, 0, image=photo, anchor='nw')  
        cv.update() 

        sys.stdout.flush()
    """

    root.bind('<Button-1>', click)
    #root.bind('<Motion>', hover)

    root.mainloop()
    del draw
    return coord


def showLocation(existingFPs, Neighbours, location):
    root = tk.Tk()  
    root.geometry("1406x472")
    root.title("display image")  
    root.config(cursor="tcross")
    im=Image.open("plan2.png")  
    im = im.resize((1406,472),Image.ANTIALIAS)
    draw = ImageDraw.Draw(im)
    fnt = ImageFont.truetype('arial.ttf', 20)


    for FP in existingFPs:
            #draw.ellipse([FP.X*8.35+162-5,FP.Y*8.35+87-5,FP.X*8.35+162+5,FP.Y*8.35+87+5], fill='rgb({},{},{})'.format(int(abs((FP.vec.RSSI1))), int(abs(FP.vec.RSSI2)), int(abs(FP.vec.RSSI3))), outline="#000000")
            draw.ellipse([FP.X*8.35+162-5,FP.Y*8.35+87-5,FP.X*8.35+162+5,FP.Y*8.35+87+5], fill='#0099ff', outline="#000000")
            draw.text((FP.X*8.35+162+5,FP.Y*8.35+87+5), str(FP.ID), font=fnt, fill="#0099ff", outline="#000000")

    for FP in Neighbours:
            X,Y=FP.X*8.35+162,FP.Y*8.35+87
            #draw.ellipse([FP.X*8.35+162-5,FP.Y*8.35+87-5,FP.X*8.35+162+5,FP.Y*8.35+87+5], fill='rgb({},{},{})'.format(int(abs((FP.vec.RSSI1))), int(abs(FP.vec.RSSI2)), int(abs(FP.vec.RSSI3))), outline="#000000")
            draw.line([X,Y,location[0]*8.35+162, location[1]*8.35+87],fill='#ff0000')
            draw.ellipse([X-5,Y-5,X+5,Y+5], fill='#ff0000', outline="#000000")
            draw.ellipse([location[0]*8.35+162-5, location[1]*8.35+87-5,location[0]*8.35+162+5, location[1]*8.35+87+5],fill='#00ffaa', outline="#000000")
           
    def click(event):
        root.destroy()

    photo=ImageTk.PhotoImage(im)  
    cv = tk.Canvas()  
    cv.pack(side='top', fill='both', expand='yes')  
    cv.create_image(0, 0, image=photo, anchor='nw')  

    root.bind('<Button-1>', click)
    root.mainloop()
    del draw