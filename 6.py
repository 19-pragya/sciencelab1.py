def start_one_channel_LA(self, **args):
        """
		start logging timestamps of rising/falling edges on ID1
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		================== ======================================================================================================
		**Arguments**
		================== ======================================================================================================
		args
		channel            ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		channel_mode       acquisition mode.
						   default value: 1
							- EVERY_SIXTEENTH_RISING_EDGE = 5
							- EVERY_FOURTH_RISING_EDGE    = 4
							- EVERY_RISING_EDGE           = 3
							- EVERY_FALLING_EDGE          = 2
							- EVERY_EDGE                  = 1
							- DISABLED                    = 0
		================== ======================================================================================================
		:return: Nothing
		see :ref:`LA_video`
		"""
        # trigger_channel    ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
        # trigger_mode       same as channel_mode.
        #				   default_value : 3
        self.clear_buffer(0, self.MAX_SAMPLES / 2)
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.START_ALTERNATE_ONE_CHAN_LA)
        self.H.__sendInt__(self.MAX_SAMPLES / 4)
        aqchan = self.__calcDChan__(args.get('channel', 'ID1'))
        aqmode = args.get('channel_mode', 1)
        trchan = self.__calcDChan__(args.get('trigger_channel', 'ID1'))
        trmode = args.get('trigger_mode', 3)

        self.H.__sendByte__((aqchan << 4) | aqmode)
        self.H.__sendByte__((trchan << 4) | trmode)
        self.H.__get_ack__()
        self.digital_channels_in_buffer = 1

        a = self.dchans[0]
        a.prescaler = 0
        a.datatype = 'long'
        a.length = self.MAX_SAMPLES / 4
        a.maximum_time = 67 * 1e6  # conversion to uS
        a.mode = args.get('channel_mode', 1)
        a.name = args.get('channel', 'ID1')

        if trmode in [3, 4, 5]:
            a.initial_state_override = 2
        elif trmode == 2:
            a.initial_state_override = 1

    def start_two_channel_LA(self, **args):
        """
		start logging timestamps of rising/falling edges on ID1,AD2
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  =======================================================================================================
		**Arguments**
		==============  =======================================================================================================
		trigger         Bool . Enable rising edge trigger on ID1
		\*\*args
		chans			Channels to acquire data from . default ['ID1','ID2']
		modes               modes for each channel. Array .\n
							default value: [1,1]
							- EVERY_SIXTEENTH_RISING_EDGE = 5
							- EVERY_FOURTH_RISING_EDGE    = 4
							- EVERY_RISING_EDGE           = 3
							- EVERY_FALLING_EDGE          = 2
							- EVERY_EDGE                  = 1
							- DISABLED                    = 0
		maximum_time    Total time to sample. If total time exceeds 67 seconds, a prescaler will be used in the reference clock
		==============  =======================================================================================================
		::
			"fetch_long_data_from_dma(samples,1)" to get data acquired from channel 1
			"fetch_long_data_from_dma(samples,2)" to get data acquired from channel 2
			The read data can be accessed from self.dchans[0 or 1]
		"""
        # Trigger not working up to expectations. DMA keeps dumping Null values even though not triggered.

        # trigger         True/False  : Whether or not to trigger the Logic Analyzer using the first channel of the two.
        # trig_type		'rising' / 'falling' .  Type of logic change to trigger on
        # trig_chan		channel to trigger on . Any digital input. default chans[0]

        modes = args.get('modes', [1, 1])
        strchans = args.get('chans', ['ID1', 'ID2'])
        chans = [self.__calcDChan__(strchans[0]), self.__calcDChan__(strchans[1])]  # Convert strings to index
        maximum_time = args.get('maximum_time', 67)
        trigger = args.get('trigger', 0)
        if trigger:
            trigger = 1
            if args.get('edge', 'rising') == 'falling': trigger |= 2
            trigger |= (self.__calcDChan__(args.get('trig_chan', strchans[0])) << 4)
        # print (args.get('trigger',0),args.get('edge'),args.get('trig_chan',strchans[0]),hex(trigger),args)
        else:
            trigger = 0

        self.clear_buffer(0, self.MAX_SAMPLES)
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.START_TWO_CHAN_LA)
        self.H.__sendInt__(self.MAX_SAMPLES / 4)
        self.H.__sendByte__(trigger)

        self.H.__sendByte__((modes[1] << 4) | modes[0])  # Modes. four bits each
        self.H.__sendByte__((chans[1] << 4) | chans[0])  # Channels. four bits each
        self.H.__get_ack__()
        n = 0
        for a in self.dchans[:2]:
            a.prescaler = 0
            a.length = self.MAX_SAMPLES / 4
            a.datatype = 'long'
            a.maximum_time = maximum_time * 1e6  # conversion to uS
            a.mode = modes[n]
            a.channel_number = chans[n]
            a.name = strchans[n]
            n += 1
        self.digital_channels_in_buffer = 2

    def start_three_channel_LA(self, **args):
        """
		start logging timestamps of rising/falling edges on ID1,ID2,ID3
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		================== ======================================================================================================
		**Arguments**
		================== ======================================================================================================
		args
		trigger_channel     ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		modes               modes for each channel. Array .\n
							default value: [1,1,1]
							- EVERY_SIXTEENTH_RISING_EDGE = 5
							- EVERY_FOURTH_RISING_EDGE    = 4
							- EVERY_RISING_EDGE           = 3
							- EVERY_FALLING_EDGE          = 2
							- EVERY_EDGE                  = 1
							- DISABLED                    = 0
		trigger_mode        same as modes(previously documented keyword argument)
							default_value : 3
		================== ======================================================================================================
		:return: Nothing
		"""
        self.clear_buffer(0, self.MAX_SAMPLES)
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.START_THREE_CHAN_LA)
        self.H.__sendInt__(self.MAX_SAMPLES / 4)
        modes = args.get('modes', [1, 1, 1, 1])
        trchan = self.__calcDChan__(args.get('trigger_channel', 'ID1'))
        trmode = args.get('trigger_mode', 3)

        self.H.__sendInt__(modes[0] | (modes[1] << 4) | (modes[2] << 8))
        self.H.__sendByte__((trchan << 4) | trmode)

        self.H.__get_ack__()
        self.digital_channels_in_buffer = 3

        n = 0
        for a in self.dchans[:3]:
            a.prescaler = 0
            a.length = self.MAX_SAMPLES / 4
            a.datatype = 'int'
            a.maximum_time = 1e3  # < 1 mS between each consecutive level changes in the input signal must be ensured to prevent rollover
            a.mode = modes[n]
            a.name = a.digital_channel_names[n]
            if trmode in [3, 4, 5]:
                a.initial_state_override = 2
            elif trmode == 2:
                a.initial_state_override = 1
            n += 1
