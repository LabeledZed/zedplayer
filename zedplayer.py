import sys
import os
import eyed3
from tkinter import *
from tkinter.messagebox import showerror
from contextlib import redirect_stdout
from datetime import timedelta
import subprocess

with redirect_stdout(open(os.devnull, "w")):
    import pygame

playlist = []
if getattr(sys, 'frozen', False):
    truepath = os.path.dirname(sys.executable)
    try:
        for i in range(len(sys.argv) - 1):
            playlist.append(sys.argv[i+1])
    except IndexError:
        showerror("No attributes",
                  "ZedPlayer has launched without attributes, therefore has nothing to play and will now exit.")
        sys.exit()
else:
    truepath = os.getcwd()
    playlist.append(r"D:\Data\Audio\ATK Songs\Grindo, Anon, Mando - Dealers, Preza 2.mp3")
    playlist.append(r"D:\Data\Audio\ATK Songs\Grindo, Lil Boxakos - Nigga 2.mp3")
    playlist.append(r"D:\Data\Audio\ATK Songs\Grindo, Anon - Den Kanoume Xares.mp3")

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

try:
    win.iconbitmap(sys._MEIPASS + "\\incl\\zedplayer.ico")
    titleimg = PhotoImage(file=sys._MEIPASS + "\\incl\\zedplayer.png")
except AttributeError:
    win.iconbitmap(os.getcwd() + "\\incl\\zedplayer.ico")
    titleimg = PhotoImage(file=os.getcwd() + "\\incl\\zedplayer.png")
win.resizable(False, False)
win.protocol("WM_DELETE_WINDOW", lambda: sys.exit())

dvar = DoubleVar()
vvar = IntVar()
trackend = 0

imglbl = Label(win, image=titleimg, bg="#1a1a1a")
playing = Label(win, text="(window not initialized)\n", font="Consolas 12", fg="#ff0000", bg="#1a1a1a")

btnsize = 24
playbtn = Button(win, text="⏸", font=("Arial", btnsize),
                 bg="#247083", fg="#ffffff", activebackground="#37abc8", activeforeground="#1a1a1a")
stopbtn = Button(win, text="⏹", font=("Arial", btnsize),
                 bg="#247083", fg="#ffffff", activebackground="#37abc8", activeforeground="#1a1a1a")
replaybtn = Button(win, text="⏭", font=("Arial", btnsize),
                   bg="#247083", fg="#ffffff", activebackground="#37abc8", activeforeground="#1a1a1a")
elapse = Scale(win, variable=dvar, from_=0, to=trackend, orient=HORIZONTAL, showvalue=FALSE,
               troughcolor="#1a1a1a", bg="#ffffff", border=0)
elapsestr = Label(win, font="Consolas 9", fg="#ffffff", bg="#1a1a1a")
volume = Scale(win, variable=vvar, from_=100, to=0, orient=VERTICAL, font="Consolas 8",
               troughcolor="#1a1a1a", bg="#247083", fg="#ffffff", border=0)

imglbl.grid(column=0, row=0, columnspan=3)
playing.grid(column=0, row=1, columnspan=3)
stopbtn.grid(column=0, row=2)
playbtn.grid(column=1, row=2)
replaybtn.grid(column=2, row=2)
elapse.grid(column=0, row=3, columnspan=3)
elapsestr.grid(column=3, row=3, columnspan=1)
volume.grid(column=3, row=0, rowspan=3)

pygame.mixer.init()
mixer = pygame.mixer.music
musiccontrols = 0

oldset = round((mixer.get_pos() / 1000) + 1)
offset = 0
canRun = False
canNotRepeat = True


def mplay():
    global musiccontrols, trackend
    if elapse.get() == round(trackend):
        mstop()
    if musiccontrols == 1:
        playbtn.configure(text="⏸")
        mixer.unpause()
        musiccontrols = 0
    elif musiccontrols == 0:
        playbtn.configure(text="▶")
        mixer.pause()
        musiccontrols = 1
    else:
        playbtn.configure(text="⏸")
        mixer.play()
        musiccontrols = 0


def mstop():
    global musiccontrols, offset
    offset = 0
    mixer.stop()
    musiccontrols = 3


def mseek():
    global offset, playlist, trackend, song, playingstr, canNotRepeat
    offset = 0
    try:
        mixer.queue(playlist[0])
        if elapse.get() == round(trackend):
            mstop()
            mixer.play()
        else:
            mixer.set_pos(trackend)
        try:
            song = eyed3.load(playlist[0]).tag
        except AttributeError:
            song = ""
        if not playlist[0] == "":
            trackend = pygame.mixer.Sound(playlist[0]).get_length()
            playingstr = os.path.basename(playlist[0]).replace(".mp3", "").replace(".wav", "")
            try:
                if song.title is None:
                    pass
                else:
                    if song.artist is None:
                        playingstr = song.title
                    else:
                        if song.album is None:
                            # noinspection PyUnresolvedReferences
                            playingstr = song.title + "\nBy: " + song.artist
                        else:
                            # noinspection PyUnresolvedReferences
                            playingstr = song.title + "\nBy: " + song.artist + "\nIn: " + song.album
            except AttributeError:
                pass
            playing.configure(text="Now playing: " + playingstr + "\n", fg="#ffffff")
            setsizes()
            playlist.pop(0)
    except IndexError:
        canNotRepeat = False
        mixer.play()


try:
    song = eyed3.load(playlist[0]).tag
except AttributeError:
    song = ""

if not playlist[0] == "":
    trackend = pygame.mixer.Sound(playlist[0]).get_length()
    playingstr = os.path.basename(playlist[0]).replace(".mp3", "").replace(".wav", "")
    try:
        if song.title is not None:
            if song.artist is None:
                playingstr = song.title
            else:
                if song.album is None:
                    # noinspection PyUnresolvedReferences
                    playingstr = song.title + "\nBy: " + song.artist
                else:
                    # noinspection PyUnresolvedReferences
                    playingstr = song.title + "\nBy: " + song.artist + "\nIn: " + song.album
    except AttributeError:
        pass

    playing.configure(text="Now playing: " + playingstr + "\n", fg="#ffffff")
    mixer.load(playlist[0])
    playbtn.configure(command=mplay)
    stopbtn.configure(command=mstop)
    replaybtn.configure(command=mseek)
    playlist.pop(0)


def setsizes():
    global mixer, canRun
    elapse.config(length=win.winfo_width() - elapsestr.winfo_width() - 8, to=trackend)
    if not canRun:
        volume.configure(length=win.winfo_height() - 32)
        volume.set(int(open(os.getenv('APPDATA') + "\\ZedPlayer\\volume.info", "r").read().strip()))
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.call("taskkill /f /pid " + open(os.getenv('APPDATA') + "\\ZedPlayer\\pid.old", "r").read().strip(),
                        startupinfo=si)
        with redirect_stdout(open(os.getenv('APPDATA') + "\\ZedPlayer\\pid.old", "w")):
            print(os.getpid())
        canRun = True
        mixer.play()


def volumeadj(event):
    with redirect_stdout(open(os.devnull, "w")):
        print(event)
    mixer.set_volume(volume.get() / 100)
    with redirect_stdout(open(os.getenv('APPDATA') + "\\ZedPlayer\\volume.info", "w")):
        print(volume.get())


def infloop():
    global trackend, oldset, offset, canRun, canNotRepeat
    if elapse.get() == round(trackend):
        if canNotRepeat:
            mseek()
        else:
            mstop()
            mplay()
    elapsestr.configure(text=str(timedelta(seconds=elapse.get())).split(".")[0])
    if not oldset == elapse.get() and not elapse.get() == round(trackend) and canRun:
        mixer.set_pos(elapse.get())
        offset += elapse.get() - oldset
    oldset = round(mixer.get_pos() / 1000, 0) + offset
    elapse.set((mixer.get_pos() / 1000) + offset)
    win.after(1000, infloop)


def forw(event):
    global offset, trackend
    with redirect_stdout(open(os.devnull, "w")):
        print(event)
    if elapse.get() < trackend - 5:
        mixer.set_pos(elapse.get() + 5)
        offset += 5


def backw(event):
    global offset
    with redirect_stdout(open(os.devnull, "w")):
        print(event)
    if elapse.get() > 5:
        mixer.set_pos(elapse.get() - 5)
        offset -= 5


def downw(event):
    with redirect_stdout(open(os.devnull, "w")):
        print(event)
    if not volume.get() < 5:
        volume.set(volume.get() - 5)


def upw(event):
    with redirect_stdout(open(os.devnull, "w")):
        print(event)
    if not volume.get() > 95:
        volume.set(volume.get() + 5)


def onrw(event):
    global canNotRepeat
    with redirect_stdout(open(os.devnull, "w")):
        print(event)
    if canNotRepeat:
        canNotRepeat = False
        playing.configure(text="Now playing: " + playingstr + "\n🔁", fg="#ffffff")
    else:
        canNotRepeat = True
        playing.configure(text="Now playing: " + playingstr + "\n", fg="#ffffff")


def onspace(event):
    with redirect_stdout(open(os.devnull, "w")):
        print(event)
    mplay()


win.bind("<space>", onspace)
win.bind("<Left>", backw)
win.bind("<Right>", forw)
win.bind("<Up>", upw)
win.bind("<Down>", downw)
win.bind("r", onrw)

if not os.path.isdir(os.getenv('APPDATA') + "\\ZedPlayer"):
    os.mkdir(os.getenv('APPDATA') + "\\ZedPlayer")
if not os.path.isfile(os.getenv('APPDATA') + "\\ZedPlayer\\volume.info"):
    with redirect_stdout(open(os.getenv('APPDATA') + "\\ZedPlayer\\volume.info", "x")):
        print("100")
if not os.path.isfile(os.getenv('APPDATA') + "\\ZedPlayer\\pid.old"):
    open(os.getenv('APPDATA') + "\\ZedPlayer\\pid.old", "x")

win.after(500, setsizes)
volume.configure(command=volumeadj)
infloop()
win.focus()
win.mainloop()
