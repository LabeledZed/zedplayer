from datetime import datetime
import sys
import time
import os
import eyed3
import random
from tkinter import *
from tkinter.messagebox import showerror
from tkinter.ttk import Combobox
from contextlib import redirect_stdout
from datetime import timedelta
import subprocess
from threading import Thread
import cv2
from pygrabber.dshow_graph import FilterGraph

import pypresence.exceptions
from pypresence import Presence

with redirect_stdout(open(os.devnull, "w")):
    import pygame

playlist = []
if getattr(sys, 'frozen', False):
    truepath = os.path.dirname(sys.executable)
    for i in range(len(sys.argv) - 1):
        playlist.append(sys.argv[i + 1])
else:
    truepath = os.getcwd()
    playlist.append(r"D:\Data\Audio\duKYS Songs\duKYS - duKYS von Zarovich.mp3")

win = Tk()


def center(query):
    query.update_idletasks()
    windowsize = tuple(int(_) for _ in query.geometry().split('+')[0].split('x'))
    x = win.winfo_screenwidth() / 2 - windowsize[0] / 2
    y = win.winfo_screenheight() / 2 - windowsize[1] / 2
    query.geometry("+%d+%d" % (x - 100, y - 100))


center(win)
win.configure(bg="#1a1a1a")
isLooping = True
pausestate = False
hasdiscord = False
hasChangedTrack = False

if not os.path.isdir(os.getenv('APPDATA') + "\\ZedPlayer"):
    os.mkdir(os.getenv('APPDATA') + "\\ZedPlayer")
if os.path.isfile(os.getenv('APPDATA') + "\\ZedPlayer\\usecam.pass"):
    canUseCamera = True
else:
    canUseCamera = False
if os.path.isfile(os.getenv('APPDATA') + "\\ZedPlayer\\showcam.pass"):
    showCamWindow = True
else:
    showCamWindow = False

camport = int()
epoch, tempepoch = int(time.time()), 0
version = "v8-dev"
win.title("ZedPlayer " + version)
reactdir = os.getenv('APPDATA') + "\\ZedPlayer\\ZedPlayer Reactions"
if not os.path.isdir(reactdir):
    os.mkdir(reactdir)


def richpresence():
    global pausestate, playingstr, epoch, isLooping, hasdiscord
    time.sleep(0.00001)
    try:
        rpc = Presence(1094371000029806592)
        hasdiscord = True
        rpc.connect()
        print("RPC Connected")
    except pypresence.exceptions.DiscordNotFound:
        rpc = None
        hasdiscord = False
    if hasdiscord:
        while isLooping and hasdiscord:
            if pausestate:
                if "\nIn:" not in playingstr and "\nBy:" not in playingstr:
                    rpc.update(details="Listening to: " + playingstr.split("\n")[0],
                               large_image='zedplayer',
                               small_image='zedplayerpause',
                               small_text=version)
                elif "\nIn:" in playingstr:
                    rpc.update(details="Listening to: " + playingstr.split("\n")[0],
                               state="By: " + playingstr.split("By: ")[1].split("\n")[0],
                               large_image='zedplayer',
                               small_image='zedplayerpause',
                               large_text="In: " + playingstr.split("In: ")[1].split("\n")[0],
                               small_text=version)
                elif "\nBy:" in playingstr:
                    rpc.update(details="Listening to: " + playingstr.split("\n")[0],
                               state="By: " + playingstr.split("By: ")[1].split("\n")[0],
                               large_image='zedplayer',
                               small_image='zedplayerpause',
                               small_text=version)
            else:
                if "\nIn:" not in playingstr and "\nBy:" not in playingstr:
                    rpc.update(details="Listening to: " + playingstr.split("\n")[0],
                               large_image='zedplayer',
                               small_image='zedplayerplay',
                               start=epoch - offset, end=epoch + trackend - offset,
                               small_text=version)
                elif "\nIn:" in playingstr:
                    rpc.update(details="Listening to: " + playingstr.split("\n")[0],
                               state="By: " + playingstr.split("By: ")[1].split("\n")[0],
                               large_image='zedplayer',
                               small_image='zedplayerplay',
                               large_text="In: " + playingstr.split("In: ")[1].split("\n")[0],
                               start=epoch - offset, end=epoch + trackend - offset,
                               small_text=version)
                elif "\nBy:" in playingstr:
                    rpc.update(details="Listening to: " + playingstr.split("\n")[0],
                               state="By: " + playingstr.split("By: ")[1].split("\n")[0],
                               large_image='zedplayer',
                               small_image='zedplayerplay',
                               start=epoch - offset, end=epoch + trackend - offset,
                               small_text=version)
    rpc.close()


def appexit():
    global isLooping
    isLooping = False
    pygame.mixer.quit()
    win.destroy()
    os._exit(0)


try:
    win.iconbitmap(sys._MEIPASS + "\\incl\\zedplayer.ico")
    titleimg = PhotoImage(file=sys._MEIPASS + "\\incl\\zedplayer.png")
except AttributeError:
    win.iconbitmap(os.getcwd() + "\\incl\\zedplayer.ico")
    titleimg = PhotoImage(file=os.getcwd() + "\\incl\\zedplayer.png")
win.resizable(False, False)
win.protocol("WM_DELETE_WINDOW", appexit)

dvar = DoubleVar()
vvar = IntVar()
trackend = 0

imglbl = Label(win, image=titleimg, bg="#1a1a1a")
playing = Label(win, text="(window not initialized)\n", font="Consolas 12", fg="#ff0000", bg="#1a1a1a")

btnsize = 21
playbtn = Button(win, text="⏸", font=("Arial", btnsize),
                 bg="#247083", fg="#ffffff", activebackground="#37abc8", activeforeground="#1a1a1a")
stopbtn = Button(win, text="⏹", font=("Arial", btnsize),
                 bg="#247083", fg="#ffffff", activebackground="#37abc8", activeforeground="#1a1a1a")
replaybtn = Button(win, text="⏭", font=("Arial", btnsize),
                   bg="#247083", fg="#ffffff", activebackground="#37abc8", activeforeground="#1a1a1a")
settingsbtn = Button(win, text="⚙", font=("Arial", btnsize),
                     bg="#247083", fg="#ffffff", activebackground="#37abc8", activeforeground="#1a1a1a")
elapse = Scale(win, variable=dvar, from_=0, to=trackend, orient=HORIZONTAL, showvalue=FALSE,
               troughcolor="#1a1a1a", bg="#ffffff", border=0)
elapsestr = Label(win, font="Consolas 9", fg="#ffffff", bg="#1a1a1a")
volume = Scale(win, variable=vvar, from_=100, to=0, orient=VERTICAL, font="Consolas 8",
               troughcolor="#1a1a1a", bg="#247083", fg="#ffffff", border=0)

imglbl.grid(column=0, row=0, columnspan=4)
playing.grid(column=0, row=1, columnspan=4)
stopbtn.grid(column=0, row=2)
playbtn.grid(column=1, row=2)
replaybtn.grid(column=2, row=2)
settingsbtn.grid(column=3, row=2)
elapse.grid(column=0, row=3, columnspan=4)
elapsestr.grid(column=4, row=3, columnspan=1)
volume.grid(column=4, row=0, rowspan=3)

pygame.mixer.init()
mixer = pygame.mixer.music
mixer.set_volume(0)
musiccontrols = 0

offset = 0
canRun = False
canNotRepeat = True
canSeek = False
isClicking = False


def mplay():
    global musiccontrols, trackend, pausestate, epoch, offset, tempepoch, version, hasChangedTrack
    if elapse.get() == round(trackend):
        mstop()
        pausestate = True
    if musiccontrols == 1:
        playbtn.configure(text="⏸")
        mixer.unpause()
        epoch += int(time.time()) - tempepoch
        pausestate = False
        musiccontrols = 0
    elif musiccontrols == 0:
        playbtn.configure(text="▶")
        mixer.pause()
        tempepoch = int(time.time())
        pausestate = True
        musiccontrols = 1
    else:
        playbtn.configure(text="⏸")
        epoch = int(time.time())
        mixer.play()
        hasChangedTrack = True
        pausestate = False
        musiccontrols = 0
    if pausestate:
        if "\nIn:" not in playingstr and "\nBy:" not in playingstr:
            win.title("ZedPlayer " + version)
        elif "\nIn:" in playingstr:
            win.title("ZedPlayer " + version)
        elif "\nBy:" in playingstr:
            win.title("ZedPlayer " + version)
    else:
        if "\nIn:" not in playingstr and "\nBy:" not in playingstr:
            win.title(playingstr.split("\n")[0])
        elif "\nIn:" in playingstr:
            win.title(playingstr.split("By: ")[1].split("\n")[0] + " - " + playingstr.split("\n")[0])
        elif "\nBy:" in playingstr:
            win.title(playingstr.split("By: ")[1].split("\n")[0] + " - " + playingstr.split("\n")[0])


def mstop():
    global musiccontrols, offset, pausestate, version
    offset = 0
    mixer.stop()
    playbtn.configure(text="▶")
    pausestate = True
    musiccontrols = 3
    if pausestate:
        if "\nIn:" not in playingstr and "\nBy:" not in playingstr:
            win.title("ZedPlayer " + version)
        elif "\nIn:" in playingstr:
            win.title("ZedPlayer " + version)
        elif "\nBy:" in playingstr:
            win.title("ZedPlayer " + version)
    else:
        if "\nIn:" not in playingstr and "\nBy:" not in playingstr:
            win.title(playingstr.split("\n")[0])
        elif "\nIn:" in playingstr:
            win.title(playingstr.split("By: ")[1].split("\n")[0] + " - " + playingstr.split("\n")[0])
        elif "\nBy:" in playingstr:
            win.title(playingstr.split("By: ")[1].split("\n")[0] + " - " + playingstr.split("\n")[0])


def mseek():
    global offset, playlist, trackend, song, playingstr, canNotRepeat, epoch, pausestate, version, hasChangedTrack
    offset = 0
    try:
        mstop()
        mixer.load(playlist[0])
        mplay()
        hasChangedTrack = True
        epoch = int(time.time())
        try:
            song = eyed3.load(playlist[0]).tag
        except AttributeError:
            song = ""
        if not playlist[0] == "":
            trackend = pygame.mixer.Sound(playlist[0]).get_length()
            playingstr = os.path.basename(playlist[0])[:-int(len(os.path.basename(playlist[0])) -
                                                             os.path.basename(playlist[0]).rfind("."))]
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
        mplay()
        hasChangedTrack = True
        epoch = int(time.time())
    if pausestate:
        if "\nIn:" not in playingstr and "\nBy:" not in playingstr:
            win.title("ZedPlayer " + version)
        elif "\nIn:" in playingstr:
            win.title("ZedPlayer " + version)
        elif "\nBy:" in playingstr:
            win.title("ZedPlayer " + version)
    else:
        if "\nIn:" not in playingstr and "\nBy:" not in playingstr:
            win.title(playingstr.split("\n")[0])
        elif "\nIn:" in playingstr:
            win.title(playingstr.split("By: ")[1].split("\n")[0] + " - " + playingstr.split("\n")[0])
        elif "\nBy:" in playingstr:
            win.title(playingstr.split("By: ")[1].split("\n")[0] + " - " + playingstr.split("\n")[0])


try:
    song = eyed3.load(playlist[0]).tag
except AttributeError:
    song = ""
except IndexError:
    showerror("No attributes",
              "ZedPlayer has launched without attributes, therefore has nothing to play and will now exit.")
    sys.exit()

if not playlist[0] == "":
    trackend = pygame.mixer.Sound(playlist[0]).get_length()
    playingstr = os.path.basename(playlist[0])[:-int(len(os.path.basename(playlist[0])) -
                                                     os.path.basename(playlist[0]).rfind("."))]
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
    global mixer, canRun, epoch, hasChangedTrack
    elapse.config(length=win.winfo_width() - elapsestr.winfo_width() - 8, to=trackend)
    if not canRun:
        volume.set(int(open(os.getenv('APPDATA') + "\\ZedPlayer\\volume.info", "r").read().strip()))
        volume.configure(length=win.winfo_height() - 32)
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.call("taskkill /f /pid " + open(os.getenv('APPDATA') + "\\ZedPlayer\\pid.old", "r").read().strip(),
                        startupinfo=si)
        with redirect_stdout(open(os.getenv('APPDATA') + "\\ZedPlayer\\pid.old", "w")):
            print(os.getpid())
        canRun = True
        mixer.play()
        win.focus_force()
        if 0 in get_available_cameras()[0]:
            Thread(target=snap).start()
        epoch = int(time.time())
        Thread(target=richpresence).start()
        if pausestate:
            if "\nIn:" not in playingstr and "\nBy:" not in playingstr:
                win.title("ZedPlayer " + version)
            elif "\nIn:" in playingstr:
                win.title("ZedPlayer " + version)
            elif "\nBy:" in playingstr:
                win.title("ZedPlayer " + version)
        else:
            if "\nIn:" not in playingstr and "\nBy:" not in playingstr:
                win.title(playingstr.split("\n")[0])
            elif "\nIn:" in playingstr:
                win.title(playingstr.split("By: ")[1].split("\n")[0] + " - " + playingstr.split("\n")[0])
            elif "\nBy:" in playingstr:
                win.title(playingstr.split("By: ")[1].split("\n")[0] + " - " + playingstr.split("\n")[0])


def volumeadj(*args):
    mixer.set_volume(volume.get() / 100)
    with redirect_stdout(open(os.getenv('APPDATA') + "\\ZedPlayer\\volume.info", "w")):
        print(volume.get())


def get_available_cameras():
    devices = FilterGraph().get_input_devices()
    camnums = []
    camnames = []
    for deviceindex, devicename in enumerate(devices):
        camnums.append(deviceindex)
        camnames.append(devicename)
    return camnums, camnames


def stg():
    global hasdiscord, canUseCamera, showCamWindow
    if not any(isinstance(x, Toplevel) for x in win.winfo_children()):
        stgwin = Toplevel(win)
        stgwin.resizable(False, False)
        center(stgwin)
        try:
            stgwin.iconbitmap(sys._MEIPASS + "\\incl\\zedplayer.ico")
        except AttributeError:
            stgwin.iconbitmap(os.getcwd() + "\\incl\\zedplayer.ico")
        stgwin.title("ZedPlayer Settings")
        stgwin.configure(bg="#1a1a1a")
        Label(stgwin, text="Settings", font="Consolas 22", fg="#2c89a0", bg="#1a1a1a") \
            .grid(column=0, row=0, columnspan=2)
        rb = Button(stgwin, text="Open reactions folder", font="Consolas 10", fg="#ffffff", bg="#242424",
                    command=lambda: os.startfile(reactdir))
        usediscord = IntVar()
        usecamera = IntVar()
        showcam = IntVar()

        def dsdef():
            global hasdiscord
            if usediscord.get() == 0:
                hasdiscord = False
            else:
                Thread(target=richpresence).start()

        def cmdef():
            global canUseCamera
            if usecamera.get() == 0:
                camsel.grid_forget()
                shbtn.grid_forget()
                shlbl.grid_forget()
                rb.grid_forget()
                canUseCamera = False
                if os.path.isfile(os.getenv('APPDATA') + "\\ZedPlayer\\usecam.pass"):
                    os.remove(os.getenv('APPDATA') + "\\ZedPlayer\\usecam.pass")
            else:
                camsel.grid(column=1, row=3, sticky=W)
                shbtn.grid(column=0, row=4)
                shlbl.grid(column=1, row=4, sticky=W)
                rb.grid(column=0, row=5, columnspan=2)
                canUseCamera = True
                if not os.path.isfile(os.getenv('APPDATA') + "\\ZedPlayer\\usecam.pass"):
                    open(os.getenv('APPDATA') + "\\ZedPlayer\\usecam.pass", "x")

        def shdef():
            global showCamWindow
            if showcam.get() == 0:
                showCamWindow = False
                if os.path.isfile(os.getenv('APPDATA') + "\\ZedPlayer\\showcam.pass"):
                    os.remove(os.getenv('APPDATA') + "\\ZedPlayer\\showcam.pass")
            else:
                showCamWindow = True
                if not os.path.isfile(os.getenv('APPDATA') + "\\ZedPlayer\\showcam.pass"):
                    open(os.getenv('APPDATA') + "\\ZedPlayer\\showcam.pass", "x")

        def seldef(*args):
            global camport
            camport = get_available_cameras()[1].index(camsel.get())
            if not os.path.isfile(os.getenv('APPDATA') + "\\ZedPlayer\\camera.info"):
                with redirect_stdout(open(os.getenv('APPDATA') + "\\ZedPlayer\\camera.info", "x")):
                    print(camport)
            else:
                with redirect_stdout(open(os.getenv('APPDATA') + "\\ZedPlayer\\camera.info", "w")):
                    print(camport)

        stgbtn = Checkbutton(stgwin, bg='#1a1a1a', variable=usediscord, command=dsdef)
        Label(stgwin, text="Use Discord RPC", bg='#1a1a1a', fg="#ffffff", font="Consolas 12") \
            .grid(column=1, row=1, sticky=W)
        stgbtn.grid(column=0, row=1)
        if hasdiscord:
            stgbtn.select()

        ucbtn = Checkbutton(stgwin, bg='#1a1a1a', variable=usecamera, command=cmdef)
        if 0 in get_available_cameras()[0]:
            ucbtn.grid(column=0, row=2)
            Label(stgwin, text="Use camera for reactions", bg='#1a1a1a', fg="#ffffff", font="Consolas 12") \
                .grid(column=1, row=2, sticky=W)

        shbtn = Checkbutton(stgwin, bg='#1a1a1a', variable=showcam, command=shdef)
        shlbl = Label(stgwin, text="Show reaction window", bg='#1a1a1a', fg="#ffffff", font="Consolas 12")

        camsel = Combobox(stgwin, background="#1a1a1a", state="readonly")
        camsel.bind("<<ComboboxSelected>>", seldef)
        if canUseCamera:
            camsel.grid(column=1, row=3, sticky=W)
            shbtn.grid(column=0, row=4)
            shlbl.grid(column=1, row=4, sticky=W)
            rb.grid(column=0, row=5, columnspan=2)
            if showCamWindow:
                shbtn.select()
            ucbtn.select()
        camsel['values'] = get_available_cameras()[1]
        if not os.path.isfile(os.getenv('APPDATA') + "\\ZedPlayer\\camera.info"):
            camsel.current(0)
        else:
            camsel.current(int(open(os.getenv('APPDATA') + "\\ZedPlayer\\camera.info", "r").read().strip()))
    else:
        showerror("ZedPlayer Settings", "A settings window is already open!")


def infloop():
    global trackend, offset, canRun, canNotRepeat, isLooping, canSeek, isClicking, hasChangedTrack
    vmute = False
    while isLooping:
        time.sleep(0.00001)
        if elapse.get() == round(trackend):
            if canNotRepeat:
                mseek()
            else:
                mstop()
                mplay()
        elapsestr.configure(text=str(timedelta(seconds=elapse.get())).split(".")[0])
        if not canSeek or not isClicking:
            if vmute:
                mixer.set_volume(volume.get() / 100)
                vmute = False
            elapse.set((mixer.get_pos() / 1000) + offset)
        else:
            while isClicking:
                time.sleep(0.00001)
                if not vmute:
                    mixer.set_volume(0)
                    vmute = True
                try:
                    mixer.set_pos(elapse.get())
                except pygame.error:
                    pass
                offset = round(elapse.get()) - mixer.get_pos() / 1000
                elapsestr.configure(text=str(timedelta(seconds=elapse.get())).split(".")[0])


def snap():
    global playingstr, camport, trackend, hasChangedTrack, reactdir, showCamWindow
    while isLooping:
        if int(trackend)*4 > 80:
            for m in range(random.randint(80, int(trackend)*4)):
                time.sleep(0.25)
                if hasChangedTrack:
                    break
            if (not hasChangedTrack) and canUseCamera:
                cam = cv2.VideoCapture(camport)
                camres, camimg = cam.read()
                height, width, channel = camimg.shape
                font = cv2.FONT_HERSHEY_SIMPLEX
                dtloc = (width - (width - 5), height - (height - 20))
                trloc = (width - (width - 5), height - (height - 35))
                arloc = (width - (width - 5), height - (height - 50))
                alloc = (width - (width - 5), height - (height - 65))
                fontScale = 0.4
                fontColor = (34, 126, 245)
                thickness = 1
                lineType = 20
                currdate = datetime.now().strftime("%d/%m/%Y %H:%M")
                if not os.path.isdir(reactdir + "\\" + playingstr.split("By: ")[1].split("\n")[0]):
                    os.mkdir(reactdir + "\\" + playingstr.split("By: ")[1].split("\n")[0])
                savepath = reactdir + "\\" + playingstr.split("By: ")[1].split("\n")[0] + "\\react-" + \
                    datetime.now().strftime("%d-%m-%y-%H-%M") + ".png"

                cv2.putText(camimg, currdate,
                            dtloc,
                            font,
                            fontScale,
                            fontColor,
                            thickness,
                            lineType)
                if "\nIn:" not in playingstr and "\nBy:" not in playingstr:
                    cv2.putText(camimg, 'Track: ' + playingstr.split("\n")[0],
                                trloc,
                                font,
                                fontScale,
                                fontColor,
                                thickness,
                                lineType)
                elif "\nIn:" in playingstr:
                    cv2.putText(camimg, 'Track: ' + playingstr.split("\n")[0],
                                trloc,
                                font,
                                fontScale,
                                fontColor,
                                thickness,
                                lineType)
                    cv2.putText(camimg, 'By: ' + playingstr.split("By: ")[1].split("\n")[0],
                                arloc,
                                font,
                                fontScale,
                                fontColor,
                                thickness,
                                lineType)
                    cv2.putText(camimg, 'In: ' + playingstr.split("In: ")[1].split("\n")[0],
                                alloc,
                                font,
                                fontScale,
                                fontColor,
                                thickness,
                                lineType)
                elif "\nBy:" in playingstr:
                    cv2.putText(camimg, 'Track: ' + playingstr.split("\n")[0],
                                trloc,
                                font,
                                fontScale,
                                fontColor,
                                thickness,
                                lineType)
                    cv2.putText(camimg, 'By: ' + playingstr.split("By: ")[1].split("\n")[0],
                                arloc,
                                font,
                                fontScale,
                                fontColor,
                                thickness,
                                lineType)

                if camres:
                    cv2.imwrite(savepath, camimg)
                    if showCamWindow:
                        cv2.imshow("ZedPlayer Reaction", camimg)
                        cv2.waitKey(0)
                        try:
                            cv2.destroyWindow("ZedPlayer Reaction")
                        except cv2.error:
                            pass
                else:
                    pass
            hasChangedTrack = False
        else:
            time.sleep(1)


def forw(*args):
    global offset, trackend
    if elapse.get() < trackend - 5:
        mixer.set_pos(elapse.get() + 5)
        offset += 5


def backw(*args):
    global offset, trackend
    if elapse.get() > 5:
        mixer.set_pos(elapse.get() - 5)
        offset -= 5


def downw(*args):
    if not volume.get() < 5:
        volume.set(volume.get() - 5)
    else:
        volume.set(0)


def upw(*args):
    if not volume.get() > 95:
        volume.set(volume.get() + 5)
    else:
        volume.set(100)


def onrw(*args):
    global canNotRepeat
    if canNotRepeat:
        canNotRepeat = False
        playing.configure(text="Now playing: " + playingstr + "\n🔁", fg="#ffffff")
    else:
        canNotRepeat = True
        playing.configure(text="Now playing: " + playingstr + "\n", fg="#ffffff")


def ontab(*args):
    stg()


def onspace(*args):
    mplay()


def seekcheck(*args):
    global canSeek
    canSeek = True


def nseekcheck():
    global canSeek
    while isLooping:
        canSeek = False
        time.sleep(0.00001)


def clickcheck(*args):
    global isClicking
    isClicking = True


def nclickcheck(*args):
    global isClicking
    isClicking = False


win.bind("<Button-1>", clickcheck)
win.bind("<B1-ButtonRelease>", nclickcheck)
win.bind("<space>", onspace)
win.bind("<Left>", backw)
win.bind("<Right>", forw)
win.bind("<Up>", upw)
win.bind("<Down>", downw)
win.bind("<Tab>", ontab)
win.bind("r", onrw)

if not os.path.isfile(os.getenv('APPDATA') + "\\ZedPlayer\\volume.info"):
    with redirect_stdout(open(os.getenv('APPDATA') + "\\ZedPlayer\\volume.info", "x")):
        print("20")
if not os.path.isfile(os.getenv('APPDATA') + "\\ZedPlayer\\pid.old"):
    open(os.getenv('APPDATA') + "\\ZedPlayer\\pid.old", "x")

win.after(500, setsizes)
volume.configure(command=volumeadj)
settingsbtn.configure(command=stg)
elapse.bind("<Motion>", seekcheck)
Thread(target=infloop).start()
Thread(target=nseekcheck).start()
win.mainloop()
