import Tkinter as tk
import serial as sr
import tkMessageBox as tkmb
import serial.tools.list_ports
UART_BRIDGE = 1

# globals
commObj = None
buttons = {}
root = None

# comm class to communicate with the intan board
class SerComm:

    def __init__(self, connType=UART_BRIDGE):
        self.portName = None
        self.ser = None
        if connType == UART_BRIDGE:
            self.openUARTConn()

    def openUARTConn(self):
        for port in serial.tools.list_ports.comports(True):
            if 'FTDI' in port.description:
                self.portName = port.device
                break
        if self.portName is not None:
            self.ser = sr.Serial(self.portName, baudrate=115200, timeout=1)
        else:
            self.ser = None

    def connActive(self):
        return self.ser is not None

    def closeUARTConn(self):
        if self.ser is not None:
            self.ser.close()
            self.ser = None
        return

# button operations
def enableButton(buttonlist,key):
    buttonlist[key]['state'] = 'enabled'
    return


def disableButton(buttonlist,key):
    buttonlist[key]['state'] = 'disabled'
    return


# inits serComm object and throws error if no Intan Board is found
def connectButtonCallback():
    global commObj
    commObj = SerComm()
    if commObj.ser is None: #FTDI bridge device not found hence display error message to the user
        tkmb.showerror('Error','Intan Device not found.',type=tkmb.OK)
    else:
        disableButton(buttons,'connect')
        enableButton(buttons,'disconnect')
    return


def disconnectButtonCallback():
    global commObj
    if commObj is not None:
        commObj.closeUARTConn()
    return


# validator for spinbox widget to check if the entry is an integer
def validateInt(user_input, new_value, widget_name):
    # disallow anything but numbers in the input
    valid = new_value.isdigit() or user_input.isdigit()
    # now that we've ensured the input is only integers, range checking!
    if valid:
        # get minimum and maximum values of the widget to be validated
        minval = int(root.nametowidget(widget_name).config('from')[4])
        maxval = int(root.nametowidget(widget_name).config('to')[4])
        # check if its an integer only string
        try:
            int(user_input)
        except:
            user_input = new_value
        # check if it's in range
        if int(user_input) not in range (minval, maxval+1):
            valid = False
    if not valid:
        tkmb.showerror('Error', 'Please enter a valid Integer between 0-15', type=tkmb.OK)
    return valid


# function for enabling spike detection parameters entry fields
def spikeDetectionEnableCallback(TkVar):
    if TkVar.get() > 0:
        detectingChannelSampleFreqMenu['state'] = 'normal'
        spikeDetectionThresholdEntry['state'] = 'normal'
        detectingChannelSpinbox['state'] = 'normal'
    else:
        detectingChannelSampleFreqMenu['state'] = 'disabled'
        spikeDetectionThresholdEntry['state'] = 'disabled'
        detectingChannelSpinbox['state'] = 'disabled'


# function that handles enabling all the parameters for the voltage time discriminator
def VTDiscEnableCallback(TkVar):
    if TkVar.get() == 0:
        state = 'disabled'
    else:
        state = 'normal'

    for child in spikedetectionParamFrame.winfo_children():
        if child.winfo_class() == 'Button':
            child.configure(state=state)
        elif child.winfo_class() == 'Labelframe':
            for child2 in child.winfo_children():
                if child2.winfo_class() == 'Entry':
                    child2.configure(state=state)


# action enabling stim parameter entry fields
def stimEnableCallback(TkVar):
    if TkVar.get() > 0:
        state = 'normal'
    else:
        state = 'disabled'

    for child in stimParamFrame.winfo_children():
        if child.winfo_class() == 'Button':
            child.configure(state=state)
        elif child.winfo_class() == 'Entry':
            child.configure(state=state)


# display help graphic for the appropriate section when the help button is pressed
def displayHelpGraphic(winTitle, file):
    win = tk.Toplevel()
    win.title(winTitle)
    # can only read GIF or PPN format images
    img = tk.PhotoImage(file=file)
    img = img.subsample(2, 2) # reduce size of original image by 1/2

    lbl = tk.Label(win, image=img)
    # this is needed to prevent garbage collection of the image from memory
    lbl.image = img
    lbl.pack()

def programButtonCallback():
    pass


# Root Window
root = tk.Tk()
root.wm_title('Embedded EPhys Record/Stim Device Programmer Tool')

# connect button
comButtonFrame = tk.Frame(root)
label = tk.Label(comButtonFrame, text = 'Open Connection to Intan Stim/Rec Board.')
label.grid(row=0, column=0, sticky=tk.W)
comPortButtonConnect = tk.Button(comButtonFrame, text='Connect', width=10)
comPortButtonConnect.config(command=connectButtonCallback)
buttons['connect']=comPortButtonConnect

# disconnect button
comPortButtonDisconnect = tk.Button(comButtonFrame, text='Disconnect', width=10)
comPortButtonDisconnect.config(command=disconnectButtonCallback)
buttons['disconnect'] = comPortButtonDisconnect

disableButton(buttons,'disconnect') # not needed on program start

# Program device button
comPortButtonProgram = tk.Button(comButtonFrame, text='Program',width=10)
comPortButtonProgram.config(command=programButtonCallback)
buttons['program'] = comPortButtonProgram

disableButton(buttons, 'program')

# display button in a grid
comPortButtonConnect.grid(row=1, column=0, sticky=tk.W)
comPortButtonDisconnect.grid(row=2, column=0, sticky=tk.W)
comPortButtonProgram.grid(row=2, column=1, sticky=tk.W)
comButtonFrame.pack(anchor=tk.W, fill=None, side=tk.TOP, pady=30)



# Recording file name
recordingFileNameFrame = tk.Frame(root)
label = tk.Label(recordingFileNameFrame, text = 'Enter Name for Recording File')
label.grid(row=0, column=0, sticky=tk.W)
recordingFileNameVal = tk.StringVar()
recordingFileNameVal.set('')
recordingFileNameEntry = tk.Entry(recordingFileNameFrame, textvariable=recordingFileNameVal,width=15)
recordingFileNameEntry.grid(row=0, column=1, sticky=tk.W)
recordingFileNameFrame.pack(fill=tk.X)

# -------------- Check Boxes for Spike Detector and Stim ----------------------
# spike detection enable check box
CheckBoxFrame = tk.Frame(root)
detectionEnableCheckBoxVal = tk.IntVar()
detectionEnableCheckBoxVal.set(0)
detectionEnableCheckBox = tk.Checkbutton(CheckBoxFrame, text='Enable Spike Detection', variable=detectionEnableCheckBoxVal,
                                         command= lambda: spikeDetectionEnableCallback(detectionEnableCheckBoxVal))
detectionEnableCheckBox.grid(row=0, column=0, sticky=tk.W)

# Voltage-Time discriminator enable check box
VTDiscEnableCheckBoxVal = tk.IntVar()
VTDiscEnableCheckBoxVal.set(0)
VTDiscEnableCheckBox = tk.Checkbutton(CheckBoxFrame, text='Enable Voltage-Time Spike Discriminator', variable=VTDiscEnableCheckBoxVal,
                                      command= lambda: VTDiscEnableCallback(VTDiscEnableCheckBoxVal))
VTDiscEnableCheckBox.grid(row=0, column=1, sticky=tk.W, padx=20)

# Stim enable checkbox
stimEnableCheckBoxVal = tk.IntVar()
stimEnableCheckBoxVal.set(0)
stimEnableCheckBox = tk.Checkbutton(CheckBoxFrame, text='Enable Stim', variable=stimEnableCheckBoxVal,
                                    command= lambda: stimEnableCallback(stimEnableCheckBoxVal))
stimEnableCheckBox.grid(row=0, column=2, sticky=tk.W)

CheckBoxFrame.pack(fill=tk.X)
# ----------------------- ------------------------------ ----------------------


# spike detecting channel spinbox
detectingChannelSpinboxFrame = tk.Frame(root)
label = tk.Label(detectingChannelSpinboxFrame, text = 'Spike Detection Channel Number')
label.grid(row=0, column=0, sticky=tk.W)
detectingChannelSpinboxVCMD = (detectingChannelSpinboxFrame.register(validateInt),'%P', '%S', '%W')
detectingChannelSpinbox = tk.Spinbox(detectingChannelSpinboxFrame, width=5, validate='key', validatecommand=detectingChannelSpinboxVCMD, from_=0, to=15)
detectingChannelSpinbox.grid(row=0, column=1, sticky=tk.W)
detectingChannelSpinbox['state'] = 'disabled'
detectingChannelSpinboxFrame.pack(fill=tk.X)

# Spike Detection Voltage Threshold
spikeDetectionThresholdFrame = tk.Frame(root)
label = tk.Label(spikeDetectionThresholdFrame, text = 'Spike Detection Threshold (uV)')
label.grid(row=0, column=0, sticky=tk.W)
spikeDetectionThresholdVal = tk.StringVar()
spikeDetectionThresholdVal.set(60)
spikeDetectionThresholdEntry = tk.Entry(spikeDetectionThresholdFrame, textvariable=spikeDetectionThresholdVal,width=10)
spikeDetectionThresholdEntry.grid(row=0,column=1,sticky=tk.W)
spikeDetectionThresholdEntry['state'] = 'disabled'
spikeDetectionThresholdFrame.pack(fill=tk.X)

# spike detecting channel sampling frequency option menu
detectingChannelSampleFreqMenuFrame = tk.Frame(root)
label = tk.Label(detectingChannelSampleFreqMenuFrame, text = 'Spike Detection Channel Sampling frequency')
label.grid(row=0, column=0, sticky=tk.W)
detectingChannelSampleFreqVal = tk.IntVar()
detectingChannelSampleFreqVal.set(30000)
FreqOpts = [30000,20000,10000,5000]
detectingChannelSampleFreqMenu = tk.OptionMenu(detectingChannelSampleFreqMenuFrame, detectingChannelSampleFreqVal, *FreqOpts)
detectingChannelSampleFreqMenu['state'] = 'disabled'
detectingChannelSampleFreqMenu.grid(row=0, column=1, sticky=tk.W)
detectingChannelSampleFreqMenuFrame.pack(fill=tk.X)

# ------------- Voltage Time Discriminator PARAMETER ENTRY ---------------------
spikedetectionParamFrame = tk.LabelFrame(root, background='gray70', foreground='gray1', text = 'Spike Detection Using Voltage-Time Discriminator')
spikedetectionParamFrame.pack(fill=tk.X,pady=20)

helpButton = tk.Button(spikedetectionParamFrame,text = '?', highlightbackground='gray70',command= lambda: displayHelpGraphic('Votlage-Time Discriminator','Spike_discriminator.gif'))
helpButton.grid(row=0,column=0,sticky=tk.W)

# -------------------- Window 1 Parameters --------------------------
window1Frame = tk.LabelFrame(spikedetectionParamFrame, background='gray70', foreground='gray1', text = 'Window 1 Params')
window1Frame.grid(row=1, column=0, sticky=tk.W,padx=20)

label = tk.Label(window1Frame,text = 'Width (us)',background='gray70')
label.grid(row=0, column=0, sticky=tk.W)
width1EntryVal = tk.StringVar()
width1EntryVal.set('0')
width1Entry = tk.Entry(window1Frame, textvariable=width1EntryVal,width=5)
width1Entry.grid(row=0,column=1,sticky=tk.W+tk.E)

label = tk.Label(window1Frame,text = 'Lower Threshold (uV)', background='gray70')
label.grid(row=1, column=0, sticky=tk.W)
lower1EntryVal = tk.StringVar()
lower1EntryVal.set('0')
lower1Entry = tk.Entry(window1Frame, textvariable=lower1EntryVal,width=5)
lower1Entry.grid(row=1,column=1, sticky=tk.W+tk.E)

label = tk.Label(window1Frame,text = 'Upper Threshold (uV)', background='gray70')
label.grid(row=2, column=0, sticky=tk.W)
upper1EntryVal = tk.StringVar()
upper1EntryVal.set('0')
upper1Entry = tk.Entry(window1Frame, textvariable=lower1EntryVal,width=5)
upper1Entry.grid(row=2,column=1, sticky=tk.W+tk.E)

# -------------------- Window 2 Parameters----------------------------

window2Frame = tk.LabelFrame(spikedetectionParamFrame, background='gray70', foreground='gray1', text = 'Window 2 Params')
window2Frame.grid(row=1, column=1, sticky=tk.W, padx=20)

label = tk.Label(window2Frame,text = 'Width (us)',background='gray70')
label.grid(row=0, column=0, sticky=tk.W)
width2EntryVal = tk.StringVar()
width2EntryVal.set('0')
width2Entry = tk.Entry(window2Frame, textvariable=width2EntryVal,width=5)
width2Entry.grid(row=0,column=1,sticky=tk.W+tk.E)

label = tk.Label(window2Frame,text = 'Lower Threshold (uV)', background='gray70')
label.grid(row=1, column=0, sticky=tk.W)
lower2EntryVal = tk.StringVar()
lower2EntryVal.set('0')
lower2Entry = tk.Entry(window2Frame, textvariable=lower2EntryVal,width=5)
lower2Entry.grid(row=1,column=1, sticky=tk.W+tk.E)

label = tk.Label(window2Frame,text = 'Upper Threshold (uV)', background='gray70')
label.grid(row=2, column=0, sticky=tk.W)
upper2EntryVal = tk.StringVar()
upper2EntryVal.set('0')
upper2Entry = tk.Entry(window2Frame, textvariable=upper2EntryVal,width=5)
upper2Entry.grid(row=2,column=1, sticky=tk.W+tk.E)

# disable the entire voltage time discriminator system
for child in spikedetectionParamFrame.winfo_children():
    if child.winfo_class() == 'Button':
        child.configure(state='disabled')
    elif child.winfo_class() == 'Labelframe':
        for child2 in child.winfo_children():
            if child2.winfo_class() == 'Entry':
                child2.configure(state='disabled')



# ------------------------------------------------------------------

# recording channel entry widget
recordingChannelsFrame = tk.Frame(root)
label = tk.Label(recordingChannelsFrame, text = 'Enter Recording Channels separated by commas (16 channels max)')
label.grid(row=0, column=0, sticky=tk.W)
recordingChannelsEntryVal = tk.StringVar()
recordingChannelsEntryVal.set('')
recordringChannelsEntry = tk.Entry(recordingChannelsFrame, textvariable=recordingChannelsEntryVal)
recordringChannelsEntry.grid(row=1,column=0,sticky=tk.W+tk.E)
recordingChannelsFrame.pack(fill=tk.X)
recordingChannelsFrame.columnconfigure(index=0, weight=1)

# recording channels sampling frequency
recordingChannelsFreqFrame = tk.Frame(root)
label = tk.Label(recordingChannelsFreqFrame, text = 'Enter Sampling Freq for Recording Channels (S/s)')
label.grid(row=0, column=0, sticky=tk.W)
recordingChannelsFreqEntryVal = tk.StringVar()
recordingChannelsFreqEntryVal.set(10000)
recordringChannelsEntry = tk.Entry(recordingChannelsFreqFrame, textvariable=recordingChannelsFreqEntryVal,width=10)
recordringChannelsEntry.grid(row=0,column=1,sticky=tk.W)
recordingChannelsFreqFrame.pack(fill=tk.X)

# recording length
recordingLengthFrame = tk.Frame(root)
label = tk.Label(recordingLengthFrame, text = 'Enter Recording Time Duration (s)')
label.grid(row=0, column=0, sticky=tk.W)
recordingLengthVal = tk.StringVar()
recordingLengthVal.set(60)
recordingLengthEntry = tk.Entry(recordingLengthFrame, textvariable=recordingLengthVal,width=10)
recordingLengthEntry.grid(row=0,column=1,sticky=tk.W)
recordingLengthFrame.pack(fill=tk.X)

# Hardware Filter Bandwidth Upper Cutoff
hardwareFilterUpperCutoffFrame = tk.Frame(root)
label = tk.Label(hardwareFilterUpperCutoffFrame, text = 'Enter Upper cutoff for Hardware Bandpass Filter (Hz)')
label.grid(row=0, column=0, sticky=tk.W)
hardwareFilterUpperCutoffVal = tk.StringVar()
hardwareFilterUpperCutoffVal.set(5000)
hardwareFilterUpperCutoffEntry = tk.Entry(hardwareFilterUpperCutoffFrame, textvariable=hardwareFilterUpperCutoffVal, width=10)
hardwareFilterUpperCutoffEntry.grid(row=0,column=1, sticky=tk.W)
hardwareFilterUpperCutoffFrame.pack(fill=tk.X)

# Hardware Filter Bandwidth Lower cutoff
hardwareFilterLowerCutoffFrame = tk.Frame(root)
label = tk.Label(hardwareFilterLowerCutoffFrame, text = 'Enter Lower cutoff for Hardware Bandpass Filter (Hz)')
label.grid(row=0, column=0, sticky=tk.W)
hardwareFilterLowerCutoffVal = tk.StringVar()
hardwareFilterLowerCutoffVal.set(1)
hardwareFilterLowerCutoffEntry = tk.Entry(hardwareFilterLowerCutoffFrame, textvariable=hardwareFilterLowerCutoffVal,width=10)
hardwareFilterLowerCutoffEntry.grid(row=0,column=1, sticky=tk.W)
hardwareFilterLowerCutoffFrame.pack(fill=tk.X)


# ------------------- STIM settings --------------------------------

stimParamFrame = tk.LabelFrame(root, background='gray70', foreground='gray1', text = 'Stim Settings Params')
stimParamFrame.pack(fill=tk.X,pady=20)

stimhelpButton = tk.Button(stimParamFrame,text = '?', highlightbackground='gray70', command=lambda: displayHelpGraphic('Stim Parameters','stimParams.gif'))
stimhelpButton.grid(row=0,column=0,sticky=tk.W)

# stim channel
label = tk.Label(stimParamFrame, text = 'Enter Channel for Stim',  background='gray70')
label.grid(row=1, column=0, sticky=tk.W)
stimChannelEntryVal = tk.StringVar()
stimChannelEntryVal.set(0)
stimChannelEntry = tk.Entry(stimParamFrame, textvariable=stimChannelEntryVal, width=2)
stimChannelEntry.grid(row=1,column=1,sticky=tk.W, padx=(0,30))

# stim latency entry
label = tk.Label(stimParamFrame, text = 'Stim latency (us)',  background='gray70')
label.grid(row=2, column=0, sticky=tk.W)
stimLatencyEntryVal = tk.StringVar()
stimLatencyEntryVal.set(0)
stimLatencyEntry = tk.Entry(stimParamFrame, textvariable=stimLatencyEntryVal, width=2)
stimLatencyEntry.grid(row=2,column=1,sticky=tk.W, padx=(0,30))

# stim magnitude entry
label = tk.Label(stimParamFrame, text = 'Stim magnitude (nA)',  background='gray70')
label.grid(row=3, column=0, sticky=tk.W)
stimMagnitudeEntryVal = tk.StringVar()
stimMagnitudeEntryVal.set(0)
stimMagnitudeEntry = tk.Entry(stimParamFrame, textvariable=stimMagnitudeEntryVal, width=2)
stimMagnitudeEntry.grid(row=3,column=1, sticky=tk.W, padx=(0,30))

# pulse number
label = tk.Label(stimParamFrame, text = 'Pulse Number',  background='gray70')
label.grid(row=1, column=2, sticky=tk.W)
pulseNumberEntryVal = tk.StringVar()
pulseNumberEntryVal.set(0)
pulseNumberEntry = tk.Entry(stimParamFrame, textvariable=pulseNumberEntryVal, width=2)
pulseNumberEntry.grid(row=1,column=3, sticky=tk.W)

# pulse spacing
label = tk.Label(stimParamFrame, text = 'Pulse Spacing (us)',  background='gray70')
label.grid(row=2, column=2, sticky=tk.W)
pulseSpacingEntryVal = tk.StringVar()
pulseSpacingEntryVal.set(0)
pulseSpacingEntry = tk.Entry(stimParamFrame, textvariable=pulseSpacingEntryVal, width=8)
pulseSpacingEntry.grid(row=2,column=3, sticky=tk.W)

# pulse duration
label = tk.Label(stimParamFrame, text = 'Pulse Duration (us)',  background='gray70')
label.grid(row=3, column=2, sticky=tk.W)
pulseDurationEntryVal = tk.StringVar()
pulseDurationEntryVal.set(0)
pulseDurationEntry = tk.Entry(stimParamFrame, textvariable=pulseDurationEntryVal, width=8)
pulseDurationEntry.grid(row=3,column=3, sticky=tk.W)

for child in stimParamFrame.winfo_children():
    if child.winfo_class() == 'Button':
        child.configure(state='disabled')
    elif child.winfo_class() == 'Entry':
        child.configure(state='disabled')

# --------------------------------------------------------------------

# --------main GUI Display setup-------------
w = root.winfo_width() + 600   # width for the Tk root
h = root.winfo_height() + 830 # height for the Tk root

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window top left corner
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# set the dimensions of the window
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
# start in fullscreen mode
# root.attributes('-fullscreen', True)
# run GUI
root.mainloop()



