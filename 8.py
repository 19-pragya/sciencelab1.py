 def fetch_long_data_from_LA(self, bytes, chan=1):
        """
		fetches the data stored by DMA. long address increments
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		bytes:          number of readings(long integers) to fetch
		chan:           channel number (1,2)
		==============  ============================================================================================
		"""
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.FETCH_LONG_DMA_DATA)
        self.H.__sendInt__(bytes)
        self.H.__sendByte__(chan - 1)
        ss = self.H.fd.read(int(bytes * 4))
        self.H.__get_ack__()
        tmp = np.zeros(int(bytes))
        for a in range(int(bytes)):
            tmp[a] = CP.Integer.unpack(ss[a * 4:a * 4 + 4])[0]
        tmp = np.trim_zeros(tmp)
        return tmp

    def fetch_LA_channels(self):
        """
		reads and stores the channels in self.dchans.
		"""
        data = self.get_LA_initial_states()
        # print (data)
        for a in range(4):
            if (self.dchans[a].channel_number < self.digital_channels_in_buffer): self.__fetch_LA_channel__(a, data)
        return True

    def __fetch_LA_channel__(self, channel_number, initial_states):
        s = initial_states[4]
        a = self.dchans[channel_number]
        if a.channel_number >= self.digital_channels_in_buffer:
            self.__print__('channel unavailable')
            return False

        samples = a.length
        if a.datatype == 'int':
            tmp = self.fetch_int_data_from_LA(initial_states[a.channel_number], a.channel_number + 1)
            a.load_data(s, tmp)
        else:
            tmp = self.fetch_long_data_from_LA(initial_states[a.channel_number * 2], a.channel_number + 1)
            a.load_data(s, tmp)

        # offset=0
        # a.timestamps -= offset
        a.generate_axes()
        return True

    def get_states(self):
        """
		gets the state of the digital inputs. returns dictionary with keys 'ID1','ID2','ID3','ID4'
		>>> self.__print__(get_states())
		{'ID1': True, 'ID2': True, 'ID3': True, 'ID4': False}
		"""
        self.H.__sendByte__(CP.DIN)
        self.H.__sendByte__(CP.GET_STATES)
        s = self.H.__getByte__()
        self.H.__get_ack__()
        return {'ID1': (s & 1 != 0), 'ID2': (s & 2 != 0), 'ID3': (s & 4 != 0), 'ID4': (s & 8 != 0)}

    def get_state(self, input_id):
        """
		returns the logic level on the specified input (ID1,ID2,ID3, or ID4)
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**    Description
		==============  ============================================================================================
		input_id        the input channel
							'ID1' -> state of ID1
							'ID4' -> state of ID4
		==============  ============================================================================================
		>>> self.__print__(I.get_state(I.ID1))
		False
		"""
        return self.get_states()[input_id]

    def set_state(self, **kwargs):
        """
		set the logic level on digital outputs SQR1,SQR2,SQR3,SQR4
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		\*\*kwargs      SQR1,SQR2,SQR3,SQR4
						states(0 or 1)
		==============  ============================================================================================
		>>> I.set_state(SQR1=1,SQR2=0)
		sets SQR1 HIGH, SQR2 LOw, but leave SQR3,SQR4 untouched.
		"""
        data = 0
        if 'SQR1' in kwargs:
            data |= 0x10 | (kwargs.get('SQR1'))
        if 'SQR2' in kwargs:
            data |= 0x20 | (kwargs.get('SQR2') << 1)
        if 'SQR3' in kwargs:
            data |= 0x40 | (kwargs.get('SQR3') << 2)
        if 'SQR4' in kwargs:
            data |= 0x80 | (kwargs.get('SQR4') << 3)
        self.H.__sendByte__(CP.DOUT)
        self.H.__sendByte__(CP.SET_STATE)
        self.H.__sendByte__(data)
        self.H.__get_ack__()
