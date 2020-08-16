def start_four_channel_LA(self, trigger=1, maximum_time=0.001, mode=[1, 1, 1, 1], **args):
        """
		Four channel Logic Analyzer.
		start logging timestamps from a 64MHz counter to record level changes on ID1,ID2,ID3,ID4.
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		trigger         Bool . Enable rising edge trigger on ID1
		maximum_time    Maximum delay expected between two logic level changes.\n
						If total time exceeds 1 mS, a prescaler will be used in the reference clock
						However, this only refers to the maximum time between two successive level changes. If a delay larger
						than .26 S occurs, it will be truncated by modulo .26 S.\n
						If you need to record large intervals, try single channel/two channel modes which use 32 bit counters
						capable of time interval up to 67 seconds.
		mode            modes for each channel. List with four elements\n
						default values: [1,1,1,1]
						- EVERY_SIXTEENTH_RISING_EDGE = 5
						- EVERY_FOURTH_RISING_EDGE    = 4
						- EVERY_RISING_EDGE           = 3
						- EVERY_FALLING_EDGE          = 2
						- EVERY_EDGE                  = 1
						- DISABLED                    = 0
		==============  ============================================================================================
		:return: Nothing
		.. seealso::
			Use :func:`fetch_long_data_from_LA` (points to read,x) to get data acquired from channel x.
			The read data can be accessed from :class:`~ScienceLab.dchans` [x-1]
		"""
        self.clear_buffer(0, self.MAX_SAMPLES)
        prescale = 0
        """
		if(maximum_time > 0.26):
			#self.__print__('too long for 4 channel. try 2/1 channels')
			prescale = 3
		elif(maximum_time > 0.0655):
			prescale = 3
		elif(maximum_time > 0.008191):
			prescale = 2
		elif(maximum_time > 0.0010239):
			prescale = 1
		"""
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.START_FOUR_CHAN_LA)
        self.H.__sendInt__(self.MAX_SAMPLES / 4)
        self.H.__sendInt__(mode[0] | (mode[1] << 4) | (mode[2] << 8) | (mode[3] << 12))
        self.H.__sendByte__(prescale)  # prescaler
        trigopts = 0
        trigopts |= 4 if args.get('trigger_ID1', 0) else 0
        trigopts |= 8 if args.get('trigger_ID2', 0) else 0
        trigopts |= 16 if args.get('trigger_ID3', 0) else 0
        if (trigopts == 0): trigger |= 4  # select one trigger channel(ID1) if none selected
        trigopts |= 2 if args.get('edge', 0) == 'rising' else 0
        trigger |= trigopts
        self.H.__sendByte__(trigger)
        self.H.__get_ack__()
        self.digital_channels_in_buffer = 4
        n = 0
        for a in self.dchans:
            a.prescaler = prescale
            a.length = self.MAX_SAMPLES / 4
            a.datatype = 'int'
            a.name = a.digital_channel_names[n]
            a.maximum_time = maximum_time * 1e6  # conversion to uS
            a.mode = mode[n]
            n += 1

    def get_LA_initial_states(self):
        """
		fetches the initial states of digital inputs that were recorded right before the Logic analyzer was started, and the total points each channel recorded
		:return: chan1 progress,chan2 progress,chan3 progress,chan4 progress,[ID1,ID2,ID3,ID4]. eg. [1,0,1,1]
		"""
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.GET_INITIAL_DIGITAL_STATES)
        initial = self.H.__getInt__()
        A = (self.H.__getInt__() - initial) / 2
        B = (self.H.__getInt__() - initial) / 2 - self.MAX_SAMPLES / 4
        C = (self.H.__getInt__() - initial) / 2 - 2 * self.MAX_SAMPLES / 4
        D = (self.H.__getInt__() - initial) / 2 - 3 * self.MAX_SAMPLES / 4
        s = self.H.__getByte__()
        s_err = self.H.__getByte__()
        self.H.__get_ack__()

        if A == 0: A = self.MAX_SAMPLES / 4
        if B == 0: B = self.MAX_SAMPLES / 4
        if C == 0: C = self.MAX_SAMPLES / 4
        if D == 0: D = self.MAX_SAMPLES / 4

        if A < 0: A = 0
        if B < 0: B = 0
        if C < 0: C = 0
        if D < 0: D = 0

        return A, B, C, D, {'ID1': (s & 1 != 0), 'ID2': (s & 2 != 0), 'ID3': (s & 4 != 0), 'ID4': (s & 8 != 0),
                            'SEN': (s & 16 != 16)}  # SEN is inverted comparator output.

    def stop_LA(self):
        """
		Stop any running logic analyzer function
		"""
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.STOP_LA)
        self.H.__get_ack__()

    def fetch_int_data_from_LA(self, bytes, chan=1):
        """
		fetches the data stored by DMA. integer address increments
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		bytes:          number of readings(integers) to fetch
		chan:           channel number (1-4)
		==============  ============================================================================================
		"""
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.FETCH_INT_DMA_DATA)
        self.H.__sendInt__(bytes)
        self.H.__sendByte__(chan - 1)

        ss = self.H.fd.read(int(bytes * 2))
        t = np.zeros(int(bytes) * 2)
        for a in range(int(bytes)):
            t[a] = CP.ShortInt.unpack(ss[a * 2:a * 2 + 2])[0]

        self.H.__get_ack__()

        t = np.trim_zeros(t)
        b = 1
        rollovers = 0
        while b < len(t):
            if (t[b] < t[b - 1] and t[b] != 0):
                rollovers += 1
                t[b:] += 65535
            b += 1
        return t
