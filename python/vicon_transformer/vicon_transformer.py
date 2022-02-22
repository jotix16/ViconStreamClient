#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   vicon_transformer.py
@Time    :   2022/02/22
@Author  :   Mikel Zhobro
@Version :   1.0
@Contact :   zhobromikel@gmail.com
@License :   (C)Copyright 2021-2022, Mikel Zhobro
@Desc    :   Read frames provided by a Vicon system and transform them into a wand independent form.
'''


import json
import numpy as np
from os.path import dirname, abspath, join
import zmq

# object names
# ['frame_number', 'frame_rate', 'latency', 'my_frame_number', 'num_subjects',
# 'on_time', 'subjectNames', 'subject_0', 'subject_1', 'subject_2', 'subject_3',
# 'subject_4', 'subject_5', 'subject_6', 'subject_7', 'subject_8', 'subject_9',
# 'time_stamp']

ORIGIN = "rll_ping_base"

def T(R, p):
    tmp = np.eye(4)
    tmp[:3,:3] = np.array(R).reshape(3,3)
    tmp[:3,3:4] = np.array(p).reshape(3,1)
    return tmp

def inv_T(T):
    invT = T.copy()
    invT[:3,:3] = T[:3,:3].T
    invT[:3,3:4] = -invT[:3,:3].dot(T[:3,3:4])
    return invT

class ViconJson:
    def __init__(
        self,
        fname='testViconFrameTableRot.json',#'testViconFrame.txt'
        ip="10.42.2.29",
        port="5555",
        timeout_in_ms=5000
        ):
        self.zmq_connected = False
        self.sub = None
        self.context = None
        self.ip = ip
        self.port = port
        self.timeout_in_ms = timeout_in_ms
        self.T_origin_vicon = np.eye(4)
        # try connecting to zmq
        self.zmq_connect(self.ip,self.port,self.timeout_in_ms)
        # read frame from file when connection cannot be established
        if self.zmq_connected:
            self.json_obj = self.read_vicon_json_from_zmq()
            print('Vicon connected via zmq')
        else:
            self.json_obj = self.read_vicon_json_from_file(self.get_config_dir()+'/'+fname)
            print('Vicon initialised via test frame from file')
        self._init_origin()

    def _init_origin(self):
        originKey = ORIGIN
        self.T_origin_vicon = inv_T(self.get_T(originKey))

    def read_vicon_json_from_zmq(self):
        if not self.zmq_connected:
            print('read_vicon_json_from_zmq: connect before reading')
            return []
        else: # read
            self.json_obj = self.sub.recv_json()
            return self.json_obj

    def zmq_connect(self,ip,port,timeout):
        print('zmq_connect: connecting...')
        try:
            self.context = zmq.Context()
            self.sub=self.context.socket(zmq.SUB)
            self.sub.setsockopt(zmq.SUBSCRIBE, b"")
            self.sub.RCVTIMEO = self.timeout_in_ms # wait 5s for new message
            msg  = 'tcp://'+str(self.ip)+':'+str(port)
            self.sub.connect(msg)
            if self.sub.closed is True:
                print('zmq_connect(): could not connect')
                return
            # test read frame until frame available or timeout
            n=0
            while n<10 or not self.zmq_connected:
                self.json_obj = self.sub.recv_json()
                if self.json_obj != []:
                    self.zmq_connected = True
                n=n+1
            if self.zmq_connected:
                print('zmq_connect(): connected')
            else:
                print('zmq_connect(): could not read a frame')
                self.zmq_disconnect()
        except Exception as e:
            print('zmq_connect(): could not connect')
            return

    def zmq_disconnect(self):
        print('zmq_disconnect: disconnecting...')
        if self.zmq_connected:
            self.context.destroy()
            if self.sub.closed is True:
                self.zmq_connected = False
                print('zmq_disconnect: disconnected. Bye...')
            else:
                print('zmq_disconnect: disconnecting failed!')
        else:
            print('zmq_disconnect: already disconnected. Bye...')

    def read_vicon_json_from_file(self,fname):
        with open(fname) as json_file:
            r = json.load(json_file)
        return r

    def get_config_dir(self):
        return abspath(join(dirname(__file__), '..', '..', 'config'))

    def get_T(self, key):
        # Returns homogenous transformation in the desired origin frame
        idx = self.json_obj['subjectNames'].index(key)
        tr = 1e-3 * np.asarray(self.json_obj['subject_'+str(idx)]['global_translation'][0]).reshape(3,1)
        R = np.asarray(self.json_obj['subject_'+str(idx)]['global_rotation']["matrix"][0])
        return self.T_origin_vicon @ T(R, tr)
