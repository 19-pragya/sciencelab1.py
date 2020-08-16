def PulseTime(self, channel='ID1', PulseType='LOW', timeout=0.1):
        """
		duty cycle measurement on channel
		returns wavelength(seconds), and length of first half of pulse(high time)
		low time = (wavelength - high time)
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ==============================================================================================
		**Arguments**
		==============  ==============================================================================================
		channel         The input pin to measure wavelength and high time.['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		PulseType		Type of pulse to detect. May be 'HIGH' or 'LOW'
		timeout         Use the timeout option if you're unsure of the input signal time period.
						returns 0 if timed out
		==============  ==============================================================================================
		:return : pulse width
		.. seealso:: timing_example_
		"""
        x, y = self.MeasureMultipleDigitalEdges(channel, channel, 'rising', 'falling', 2, 2, timeout, zero=True)
        if x != None and y != None:  # Both timers registered something. did not timeout
            if y[0] > 0:  # rising edge occured first
                if PulseType == 'HIGH':
                    return y[0]
                elif PulseType == 'LOW':
                    return x[1] - y[0]
            else:  # falling edge occured first
                if PulseType == 'HIGH':
                    return y[1]
                elif PulseType == 'LOW':
                    return abs(y[0])
        return -1, -1

    def MeasureMultipleDigitalEdges(self, channel1, channel2, edgeType1, edgeType2, points1, points2, timeout=0.1,
                                    **kwargs):
        """
		Measures a set of timestamped logic level changes(Type can be selected) from two different digital inputs.
		Example
			Aim : Calculate value of gravity using time of flight.
			The setup involves a small metal nut attached to an electromagnet powered via SQ1.
			When SQ1 is turned off, the set up is designed to make the nut fall through two
			different light barriers(LED,detector pairs that show a logic change when an object gets in the middle)
			placed at known distances from the initial position.
			one can measure the timestamps for rising edges on ID1 ,and ID2 to determine the speed, and then obtain value of g
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		channel1        The input pin to measure first logic level change
		channel2        The input pin to measure second logic level change
						 -['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		edgeType1       The type of level change that should be recorded
							* 'rising'
							* 'falling'
							* 'four rising edges' [default]
		edgeType2       The type of level change that should be recorded
							* 'rising'
							* 'falling'
							* 'four rising edges'
		points1			Number of data points to obtain for input 1 (Max 4)
		points2			Number of data points to obtain for input 2 (Max 4)
		timeout         Use the timeout option if you're unsure of the input signal time period.
						returns -1 if timed out
		**kwargs
		  SQ1			set the state of SQR1 output(LOW or HIGH) and then start the timer.  eg. SQR1='LOW'
		  zero			subtract the timestamp of the first point from all the others before returning. default:True
		==============  ============================================================================================
		:return : time
		.. seealso:: timing_example_
		"""
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.TIMING_MEASUREMENTS)
        timeout_msb = int((timeout * 64e6)) >> 16
        # print ('timeout',timeout_msb)
        self.H.__sendInt__(timeout_msb)
        self.H.__sendByte__(self.__calcDChan__(channel1) | (self.__calcDChan__(channel2) << 4))
        params = 0
        if edgeType1 == 'rising':
            params |= 3
        elif edgeType1 == 'falling':
            params |= 2
        else:
            params |= 4

        if edgeType2 == 'rising':
            params |= 3 << 3
        elif edgeType2 == 'falling':
            params |= 2 << 3
        else:
            params |= 4 << 3

        if ('SQR1' in kwargs):  # User wants to toggle SQ1 before starting the timer
            params |= (1 << 6)
            if kwargs['SQR1'] == 'HIGH': params |= (1 << 7)
        self.H.__sendByte__(params)
        if points1 > 4: points1 = 4
        if points2 > 4: points2 = 4
        self.H.__sendByte__(points1 | (points2 << 4))  # Number of points to fetch from either channel

        self.H.waitForData(timeout)

        A = np.array([self.H.__getLong__() for a in range(points1)])
        B = np.array([self.H.__getLong__() for a in range(points2)])
        tmt = self.H.__getInt__()
        self.H.__get_ack__()
        # print(A,B)
        if (tmt >= timeout_msb): return None, None
        rtime = lambda t: t / 64e6
        if (kwargs.get('zero', True)):  # User wants set a reference timestamp
            return rtime(A - A[0]), rtime(B - A[0])
        else:
            return rtime(A), rtime(B)

    def capture_edges1(self, waiting_time=1., **args):
        """
		log timestamps of rising/falling edges on one digital input
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		=================   ======================================================================================================
		**Arguments**
		=================   ======================================================================================================
		waiting_time        Total time to allow the logic analyzer to collect data.
							This is implemented using a simple sleep routine, so if large delays will be involved,
							refer to :func:`start_one_channel_LA` to start the acquisition, and :func:`fetch_LA_channels` to
							retrieve data from the hardware after adequate time. The retrieved data is stored
							in the array self.dchans[0].timestamps.
		keyword arguments
		channel             'ID1',...,'ID4'
		trigger_channel     'ID1',...,'ID4'
		channel_mode        acquisition mode\n
							default value: 3
							- EVERY_SIXTEENTH_RISING_EDGE = 5
							- EVERY_FOURTH_RISING_EDGE    = 4
							- EVERY_RISING_EDGE           = 3
							- EVERY_FALLING_EDGE          = 2
							- EVERY_EDGE                  = 1
							- DISABLED                    = 0
		trigger_mode        same as channel_mode.
							default_value : 3
		=================   ======================================================================================================
		:return:  timestamp array in Seconds
		>>> I.capture_edges(0.2,channel='ID1',trigger_channel='ID1',channel_mode=3,trigger_mode = 3)
		#captures rising edges only. with rising edge trigger on ID1
		"""
        aqchan = args.get('channel', 'ID1')
        trchan = args.get('trigger_channel', aqchan)

        aqmode = args.get('channel_mode', 3)
        trmode = args.get('trigger_mode', 3)

        self.start_one_channel_LA(channel=aqchan, channel_mode=aqmode, trigger_channel=trchan, trigger_mode=trmode)

        time.sleep(waiting_time)

        data = self.get_LA_initial_states()
        tmp = self.fetch_long_data_from_LA(data[0], 1)
        # data[4][0] -> initial state
        return tmp / 64e6

    def start_one_channel_LA_backup__(self, trigger=1, channel='ID1', maximum_time=67, **args):
        """
		start logging timestamps of rising/falling edges on ID1
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		================== ======================================================================================================
		**Arguments**
		================== ======================================================================================================
		trigger            Bool . Enable edge trigger on ID1. use keyword argument edge='rising' or 'falling'
		channel            ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		maximum_time       Total time to sample. If total time exceeds 67 seconds, a prescaler will be used in the reference clock
		kwargs
		triggger_channels  array of digital input names that can trigger the acquisition.eg. trigger= ['ID1','ID2','ID3']
						   will triggger when a logic change specified by the keyword argument 'edge' occurs
						   on either or the three specified trigger inputs.
		edge               'rising' or 'falling' . trigger edge type for trigger_channels.
		================== ======================================================================================================
		:return: Nothing
		"""
        self.clear_buffer(0, self.MAX_SAMPLES / 2)
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.START_ONE_CHAN_LA)
        self.H.__sendInt__(self.MAX_SAMPLES / 4)
        # trigchan bit functions
        # b0 - trigger or not
        # b1 - trigger edge . 1 => rising. 0 => falling
        # b2, b3 - channel to acquire data from. ID1,ID2,ID3,ID4,COMPARATOR
        # b4 - trigger channel ID1
        # b5 - trigger channel ID2
        # b6 - trigger channel ID3

        if ('trigger_channels' in args) and trigger & 1:
            trigchans = args.get('trigger_channels', 0)
            if 'ID1' in trigchans: trigger |= (1 << 4)
            if 'ID2' in trigchans: trigger |= (1 << 5)
            if 'ID3' in trigchans: trigger |= (1 << 6)
        else:
            trigger |= 1 << (self.__calcDChan__(
                channel) + 4)  # trigger on specified input channel if not trigger_channel argument provided

        trigger |= 2 if args.get('edge', 0) == 'rising' else 0
        trigger |= self.__calcDChan__(channel) << 2

        self.H.__sendByte__(trigger)
        self.H.__get_ack__()
        self.digital_channels_in_buffer = 1
        for a in self.dchans:
            a.prescaler = 0
            a.datatype = 'long'
            a.length = self.MAX_SAMPLES / 4
            a.maximum_time = maximum_time * 1e6  # conversion to uS
            a.mode = self.EVERY_EDGE

            # def start_one_channel_LA(self,**args):
            """
			start logging timestamps of rising/falling edges on ID1
			.. tabularcolumns:: |p{3cm}|p{11cm}|
			================== ======================================================================================================
			**Arguments**
			================== ======================================================================================================
			args
			channel             ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
			trigger_channel     ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
			channel_mode        acquisition mode\n
								default value: 1(EVERY_EDGE)
								- EVERY_SIXTEENTH_RISING_EDGE = 5
								- EVERY_FOURTH_RISING_EDGE    = 4
								- EVERY_RISING_EDGE           = 3
								- EVERY_FALLING_EDGE          = 2
								- EVERY_EDGE                  = 1
								- DISABLED                    = 0
			trigger_edge        1=Falling edge
								0=Rising Edge
								-1=Disable Trigger
			================== ======================================================================================================
			:return: Nothing
			self.clear_buffer(0,self.MAX_SAMPLES/2);
			self.H.__sendByte__(CP.TIMING)
			self.H.__sendByte__(CP.START_ONE_CHAN_LA)
			self.H.__sendInt__(self.MAX_SAMPLES/4)
			aqchan = self.__calcDChan__(args.get('channel','ID1'))
			aqmode = args.get('channel_mode',1)
			if 'trigger_channel' in args:
				trchan = self.__calcDChan__(args.get('trigger_channel','ID1'))
				tredge = args.get('trigger_edge',0)
				self.__print__('trigger chan',trchan,' trigger edge ',tredge)
				if tredge!=-1:
					self.H.__sendByte__((trchan<<4)|(tredge<<1)|1)
				else:
					self.H.__sendByte__(0)  #no triggering
			elif 'trigger_edge' in args:
				tredge = args.get('trigger_edge',0)
				if tredge!=-1:
					self.H.__sendByte__((aqchan<<4)|(tredge<<1)|1)  #trigger on acquisition channel
				else:
					self.H.__sendByte__(0)  #no triggering
			else:
				self.H.__sendByte__(0)  #no triggering
			self.H.__sendByte__((aqchan<<4)|aqmode)
			self.H.__get_ack__()
			self.digital_channels_in_buffer = 1
			a = self.dchans[0]
			a.prescaler = 0
			a.datatype='long'
			a.length = self.MAX_SAMPLES/4
			a.maximum_time = 67*1e6 #conversion to uS
			a.mode = args.get('channel_mode',1)
			a.initial_state_override=False
			'''
			if trmode in [3,4,5]:
				a.initial_state_override = 2
			elif trmode == 2:
				a.initial_state_override = 1
			'''
			"""
