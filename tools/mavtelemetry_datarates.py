#!/usr/bin/env python
'''
GUI to calculate telemetry data rate between vehicle and GCS

Amilcar Lucas
Karthik Desai

Copyright IAV GmbH 2017
Released under GNU GPL version 3 or later
'''

from future import standard_library
standard_library.install_aliases()
from builtins import str

## Generate window for calculating the datasize
from tkinter import Tk, Text, TOP, BOTH, X, Y, N, LEFT,RIGHT, CENTER, RIDGE, VERTICAL, END, IntVar, IntVar, Scrollbar
from tkinter.ttk import Frame, Label, Entry, Combobox, Checkbutton

# import MAVLink messages length dictionary
# this file is generated by a script
mav_message_size = 'mavlink_messages_size.py'
exec(compile(source=open(mav_message_size).read(), filename=mav_message_size, mode='exec'))

# Please adapt this list to the vehicle you are using
# These were done by looking at the GCS_MAVLINK_Copter::data_stream_send() function
# in the ardupilot/ArduCopter/GCS_Mavlink.cpp file
mavlink_streams_list = [
#      STREAM  DEFAULT DEFAULT                 DEFAULT
#       NAME    RATE   MAVLINK                 CHECKBOX
#               [Hz]   MESSAGE                 STATES
    ("RAW_SENS", 0, [('RAW_IMU'              , True),
                     ('SCALED_PRESSURE'      , True),
                     ('SENSOR_OFFSETS'       , True),
                     ('NONE'                 , False)]),
    ("EXT_STAT", 1, [('SYS_STATUS'           , True),
                     ('POWER_STATUS'         , True),
                     ('MEMINFO'              , True),
                     ('MISSION_CURRENT'      , True),
                     ('GPS_RAW_INT'          , True),
                     ('GPS_RTK'              , False),
                     ('GPS2_RAW'             , False),
                     ('GPS2_RTK'             , False),
                     ('NAV_CONTROLLER_OUTPUT', True),
                     ('LIMITS_STATUS'        , True),
                     ('NONE'                 , False)]),
    ("POSITION", 1, [('GLOBAL_POSITION_INT'  , True),
                     ('LOCAL_POSITION_NED'   , True),
                     ('NONE'                 , False)]),
    ("RAW_CTRL", 0, [('RC_CHANNELS_SCALED'   , True),
                     ('NONE'                 , False)]),
    ("RC_CHAN",  0, [('SERVO_OUTPUT_RAW'     , True),
                     ('RC_CHANNELS_RAW'      , True),
                     ('NONE'                 , False)]),
    ("EXTRA1",   2, [('ATTITUDE'             , True),
                     ('SIMSTATE'             , False),
                     ('AHRS2'                , True),
                     ('PID_TUNING'           , True),
                     ('NONE'                 , False)]),
    ("EXTRA2",   2, [('VFR_HUD'              , True),
                     ('NONE'                 , False)]),
    ("EXTRA3",   1, [('AHRS'                 , True),
                     ('HWSTATUS'             , True),
                     ('SYSTEM_TIME'          , True),
                     ('RANGEFINDER'          , True),
                     ('TERRAIN_REQUEST'      , False),
                     ('BATTERY2'             , True),
                     ('MOUNT_STATUS'         , True),
                     ('OPTICAL_FLOW'         , True),
                     ('GIMBAL_REPORT'        , True),
                     ('MAG_CAL_REPORT'       , False),
                     ('MAG_CAL_PROGRESS'     , False),
                     ('EKF_STATUS_REPORT'    , True),
                     ('VIBRATION'            , True),
                     ('RPM'                  , True),
                     ('NONE'                 , False)]),
#    ("PARAMS",   8, [('PARAM_VALUE'          , True),
#                     ('NONE'                 ,False)]),
    ("ADSB",     0, [('ADSB_VEHICLE'         , True),
                     ('NONE'                 , False)]),
    ("RTCM_INJ", 1, [('GPS_RTCM_DATA'        , True),
                     ('NONE'                 , False)]),
]


class MainWindow(Frame):
    def __init__(self, parent):

        Frame.__init__(self, parent)
        self.parent = parent
        self.streamrate_name_array = {}
        self.streamrate_cb_array = {}
        self.streamDataRate_array = {}
        self.streamrate_edit_array = {}
        # you can change this one to make the GUI wider
        self.columns = 3
        self.initUI()

        self.parent.bind('<Return>', self.updateCombo)
        self.updateCombo()

    def updateCombo(self, event = None):
        totalBits = 0
        for frame_name in mavlink_streams_list:
            bits = 0
            for frame_boxes in frame_name[2]:
                temp = self.streamrate_name_array[frame_name[0]][frame_boxes[0]].get()
                if (self.streamrate_cb_array[frame_name[0]][frame_boxes[0]].get()):
                    bits = bits + (8*mavlink_message_lengths_dict[temp]) # convert number of bytes to number of bits
            datarate = float(self.streamrate_edit_array[frame_name[0]].get())
            tempDataBits = int(bits * datarate)
            self.streamDataRate_array[frame_name[0]].config(text=str(tempDataBits)+" bits/s")
            totalBits = int(totalBits + tempDataBits)
        self.end_total_data_rate_label.config(text = "Total Data Rate is "+str(totalBits) + " bits/s")


    def initUI(self):
      
        self.parent.title("Calculate Mavlink UAV->GCS telemetry datarate")
        self.pack(fill=BOTH, expand=1)
     
        count = 0
        count_frame = 0
        count_row = 0
        for frame_name in mavlink_streams_list:
            child_frame = Frame(self,borderwidth = 2, relief = RIDGE)
            child_frame.grid(row = count_row, column = count_frame % self.columns)
            if(count_frame % self.columns == self.columns-1):
                count_row = count_row + 1
            count_frame = count_frame + 1

            frame_label = Label(child_frame, text = frame_name[0] + " message stream")
            frame_label.pack(side= TOP)
            
            self.streamrate_name_array[frame_name[0]] = {}
            self.streamrate_cb_array[frame_name[0]] = {}
            
            comboFrame = Frame(child_frame)
            comboFrame.pack(side = LEFT)
            for frame_boxes in frame_name[2] :

                comboframe = Frame(comboFrame)
                comboframe.pack(side = TOP)

                combo = Combobox(comboframe,values = tuple(mavlink_msg_temp for mavlink_msg_temp in mavlink_message_lengths_dict))
                combo.grid(row = count, column = 0)
                index = list(mavlink_message_lengths_dict.keys()).index(frame_boxes[0])
                combo.current(index)
               
                var = IntVar()
                if (frame_boxes[1]):
                    var.set(1)
                else:
                    var.set(0)
                checkbox = Checkbutton(comboframe,variable = var, command = self.updateCombo)
                checkbox.grid(row = count, column = 1)

                self.streamrate_name_array[frame_name[0]][frame_boxes[0]] = combo
                self.streamrate_cb_array[frame_name[0]][frame_boxes[0]] = var

                combo.bind("<<ComboboxSelected>>",self.updateCombo)
                count = count + 1

            streamrate_frame = Frame(child_frame)
            streamrate_frame.pack(side = TOP, anchor = CENTER)
            data_rate_label = Label(streamrate_frame, text="Stream Rate")
            data_rate_label.pack()

            self.data_rate_edit = Entry(streamrate_frame,width = 2)
            self.data_rate_edit.insert(0,frame_name[1])
            self.streamrate_edit_array[frame_name[0]] =  self.data_rate_edit
            self.data_rate_edit.pack(side = LEFT, anchor = CENTER)

            unit_Label = Label(streamrate_frame, text="Hz")
            unit_Label.pack(side=RIGHT,anchor = CENTER)

            datarate_frame = Frame(child_frame)
            datarate_frame.pack(side = TOP, anchor = CENTER)
            total_data_rate_label = Label(datarate_frame, text="Data Rate")
            total_data_rate_label.pack(side=TOP,anchor = CENTER)
            self.total_data_rate_answer = Label(datarate_frame, text="   bits/s")
            self.total_data_rate_answer.pack(side=TOP,anchor = CENTER)
            self.streamDataRate_array[frame_name[0]] = self.total_data_rate_answer

        self.end_total_data_rate_label = Label(self.parent, text="Total Data Rate")
        self.end_total_data_rate_label.pack(side=TOP)


def main():
    root = Tk()
    app = MainWindow(root)
    root.mainloop()  


if __name__ == '__main__':
    main()