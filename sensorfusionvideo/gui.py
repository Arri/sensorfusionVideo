###########################################################################
# Gui for sensor fusion video generation and recording.
#
# Author: Arasch Lagies, Axiado
# First Version: 3/18/2020
# Last Update: 3/23/2020
#
# Call: python gui.py
#
# Libraries to install:
# Install Anaconda (or Miniconda on the Raspberry Pi)
# > conda install -c anaconda numpy
# > conda install -c conda-forge matplotlib
# > conda install -c anaconda tk
#
# For serial i2c communication:
# > 
###########################################################################
import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import tkinter as Tk
from tkinter.ttk import Frame
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, HPacker, VPacker
#-------------------------------------------------------
#from comm.i2cComm import *
#from comm.serialComm import *
from comm.fromFile import *
#-------------------------------------------------------
from kalman import *
import threading
import time
import queue

X_WINSIZE = 50
Y_AX_MAX = 20000
FIX_Y_AXIS = False
style.use('ggplot')

class anim(tracking):
    def __init__(self, sensor, t1, x_axis=X_WINSIZE, y_axis=Y_AX_MAX, fixY=FIX_Y_AXIS):
        self.xx = []
        self.yy = []
        self.kmx = []
        self.kmy = []
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.fixY   = fixY
        self.sensor = sensor
        self.t1     = t1
        self.doKM   = True
        self.km     = tracking()
        
    def animate(self, i, q, ax):
        if self.fixY:
            ax.set_ylim([0, self.y_axis])
        ax.grid(True)
        ax.set_ylabel('Distance [cm]')
        ax.set_title('Measurement = blue --- Fusion = red')
        
        # text1 and text2 contain the actual text, created by TextArea
        # text1 and text2 are then packed vertically into a box using VPacker
        text1 = TextArea("Red Text", textprops=dict(color="red"))
        text2 = TextArea("Blue Text", textprops=dict(color="blue"))
        box = VPacker(children=[text1, text2], align="left", pad=5, sep=5)

        # anchored_box creates the text box outside of the plot
        anchored_box = AnchoredOffsetbox(loc=3,
                                         child=box, pad=0.,
                                         frameon=True,
                                         bbox_to_anchor=(1.05, 0.73),
                                         bbox_transform=ax.transAxes,
                                         borderpad=0.,
                                         )
        ax.add_artist(anchored_box)
        
        # Get measurement values
        value = q.get() / 10.
        with q.mutex:
            q.queue.clear()
            
        # Kalman measure (alredy done above)...
        # Kalman Update ...
        self.km.kmUpdate(i, value)
        
        self.xx.append(i)
        self.yy.append(value)
        # Kalman Predict ...
        xxk, yyk = self.km.kmPredict() # only y coordinate required here
        xk, yk = xxk[0][0], yyk[0][0]
        self.kmy.append(yk)
        
        ## Collect data in a list / array for display    
        if i > self.x_axis:
            # Remove earliest value from the list
            self.xx.remove(self.xx[0])
            self.yy.remove(self.yy[0])
            self.kmy.remove(self.kmy[0])
        valx = np.asarray(self.xx)
        valy = np.asarray(self.yy)
        valkmy = np.asarray(self.kmy)
    
        # Update display settings
        ax.clear()
        ax.grid(True)
        ax.set_ylabel('Distance [cm]')
        ax.set_title('Measurement = blue --- Fusion = red')
        
        if self.fixY:
            ax.set_ylim([0, self.y_axis])
        
        # Plot the graph...
        if i <= self.x_axis:
            ax.plot(valx[:i], valy[:i], 'b')
        else:
            ax.plot(valx, valy, 'b')
            
        if self.doKM:
            if xk <= self.x_axis:
                ax.plot(valx[:i], valkmy[:i], 'r')
            else:
                ax.plot(valx, valkmy, 'r')
            
 
    def onClick(self, event):
        self.sensor.terminate()
        self.t1.join()
        time.sleep(1)
        print("[INFO] Exiting...")
        exit(0)
        
    def startKalman(self):
        print("[INFO] Starting Kalman Fiter")
        self.doKM = True

    def stopKalman(self):
        print ("[INFO] Stopping Kalman Filter")
        self.doKM = False
        
    
       
def run():
    # Set up formatting for the movie files
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=4, metadata=dict(artist='accelerator'), bitrate=180)

    q = queue.Queue()
    sensor = Comm()
    t1 = threading.Thread(target=sensor.readLoop, name=sensor.readLoop, args=(q,))
    t1.start()

    fig = plt.Figure(figsize=(5,4), dpi=100)
    fig1 = plt.Figure(figsize=(5,4), dpi=100)

    root = Tk.Tk()
    label = Tk.Label(root,text="Axiado I2C Risc-5 Demo").grid(column=0, row=0, columnspan=2)
    an = anim(sensor,t1)
    
    Tk.Button(text = "Start Kalman", command = an.startKalman).grid(column=0, row=1)
    Tk.Button(text = "Stop Kalman", command = an.stopKalman).grid(column=1, row=1)

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(column=0,row=2, columnspan=1)

    canvas1 = FigureCanvasTkAgg(fig1, master=root)
    canvas1.get_tk_widget().grid(column=1,row=2, columnspan=1)

    ax = fig.add_subplot(111)
    fig.canvas.mpl_connect('button_press_event', an.onClick)
    ani0 = animation.FuncAnimation(fig, an.animate, fargs=(q, ax), interval=2, blit=False)
    ani1 = animation.FuncAnimation(fig1, an.animate, fargs=(q, ax), interval=2, blit=False)

    # ani.save('lines.mp4', writer=writer)

    try:
        Tk.mainloop()
    except:
        #sensor.terminate()
        #t1.join()
        exit(0)
    
if __name__=="__main__":
    run()
