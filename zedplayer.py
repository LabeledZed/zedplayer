import sys
import os
import eyed3
from tkinter import *
from contextlib import redirect_stdout
import datetime

with redirect_stdout(open(os.devnull, "w")):
    import pygame

if getattr(sys, 'frozen', False):
    truepath = os.path.dirname(sys.executable)
    try:
        soundfile = sys.argv[1]
    except IndexError:
        soundfile = ""
else:
    truepath = os.getcwd()
    soundfile = r"D:\Data\Audio\ATK Songs\ATK - Preza.mp3"

win = Tk()


def center(query):
    query.update_idletasks()
    windowsize = tuple(int(_) for _ in query.geometry().split('+')[0].split('x'))
    x = win.winfo_screenwidth() / 2 - windowsize[0] / 2
    y = win.winfo_screenheight() / 2 - windowsize[1] / 2
    query.geometry("+%d+%d" % (x - 100, y - 100))


center(win)
win.configure(bg="#1a1a1a")
win.title("ZedPlayer Alpha")
win.resizable(False, False)
win.protocol("WM_DELETE_WINDOW", lambda: sys.exit())

dvar = DoubleVar()
vvar = IntVar()
trackend = 0

title = Label(win, text="ZedPlayer", font="Consolas 21 bold underline", fg="#2c89a0", bg="#1a1a1a")
playing = Label(win, text="(window not initialized)\n", font="Consolas 12", fg="#ff0000", bg="#1a1a1a")

btnsize = 24
playbtn = Button(win, text="⏯", font=("Arial", btnsize),
                 bg="#247083", fg="#ffffff", activebackground="#37abc8", activeforeground="#1a1a1a")
stopbtn = Button(win, text="⏹", font=("Arial", btnsize),
                 bg="#247083", fg="#ffffff", activebackground="#37abc8", activeforeground="#1a1a1a")
replaybtn = Button(win, text="⏮", font=("Arial", btnsize),
                   bg="#247083", fg="#ffffff", activebackground="#37abc8", activeforeground="#1a1a1a")
elapse = Scale(win, variable=dvar, from_=0, to=trackend, orient=HORIZONTAL, showvalue=FALSE,
               troughcolor="#1a1a1a", bg="#ffffff", border=0)
elapsestr = Label(win, font="Consolas 9", fg="#ffffff", bg="#1a1a1a")
volume = Scale(win, variable=vvar, from_=100, to=0, orient=VERTICAL, font="Consolas 8",
               troughcolor="#1a1a1a", bg="#247083", fg="#ffffff", border=0)

title.grid(column=0, row=0, columnspan=3)
playing.grid(column=0, row=1, columnspan=3)
stopbtn.grid(column=0, row=2)
playbtn.grid(column=1, row=2)
replaybtn.grid(column=2, row=2)
elapse.grid(column=0, row=4, columnspan=3)
elapsestr.grid(column=3, row=4, columnspan=1)
volume.grid(column=3, row=0, rowspan=4)

pygame.mixer.init()
mixer = pygame.mixer.music
musiccontrols = 0
try:
    song = eyed3.load(soundfile).tag
except AttributeError:
    song = ""


def mplay():
    global musiccontrols, trackend
    if musiccontrols == 1:
        mixer.unpause()
        musiccontrols = 0
    elif musiccontrols == 0:
        mixer.pause()
        musiccontrols = 1
    else:
        mixer.play()
        musiccontrols = 0


def mstop():
    global musiccontrols
    mixer.stop()
    musiccontrols = 3


def mseek():
    mixer.set_pos(0)


def onspace(event):
    with redirect_stdout(open(os.devnull, "w")):
        print(event)
    mplay()


win.bind("<space>", onspace)

if not soundfile == "":
    trackend = pygame.mixer.Sound(soundfile).get_length()
    playingstr = os.path.basename(soundfile).replace(".mp3", "").replace(".wav", "")
    try:
        if song.title == "":
            pass
        else:
            if song.artist == "":
                playingstr = song.title
            else:
                if song.album == "":
                    playingstr = str(song.title) + "\nBy: " + song.artist
                else:
                    playingstr = str(song.title) + "\nBy: " + song.artist + "\nIn: " + song.album
    except AttributeError:
        pass

    mixer.load(soundfile)
    playing.configure(text="Now playing: " + playingstr + "\n", fg="#ffffff")
    playbtn.configure(command=mplay)
    stopbtn.configure(command=mstop)
    replaybtn.configure(command=mseek)
    mixer.play()

else:
    playing.configure(text="Error: No file opened\n")


oldset = round((mixer.get_pos() / 1000) + 1)
offset = 0
volume.set(round(mixer.get_volume()) * 100)


def volumeadj(event):
    with redirect_stdout(open(os.devnull, "w")):
        print(event)
    mixer.set_volume(volume.get() / 100)


def infloop():
    global trackend, oldset, offset
    elapsestr.configure(text=str(datetime.timedelta(seconds=elapse.get())).split(".")[0])
    if not oldset == elapse.get():
        mixer.set_pos(elapse.get())
        offset += elapse.get() - oldset
    oldset = round(mixer.get_pos() / 1000, 0) + offset
    elapse.set((mixer.get_pos() / 1000) + offset)
    win.after(1000, infloop)


def setsizes():
    elapse.config(length=win.winfo_width() - elapsestr.winfo_width() - 8, to=trackend)
    volume.configure(length=win.winfo_height() - 32)


win.after(500, setsizes)
volume.configure(command=volumeadj)
infloop()
win.focus()
win.mainloop()
