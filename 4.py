def r2r_time(self,channel='ID1',timeout=0.1):
		"""
		Returns the time interval between two rising edges
		of input signal on ID1
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ================================================================================================
		**Arguments**
		==============  ================================================================================================
		channel         The input to measure time between two rising edges.['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		timeout         Use the timeout option if you're unsure of the input signal time period.
						returns 0 if timed out
		==============  ================================================================================================
		:return float: time between two rising edges of input signal
		.. seealso:: timing_example_
		"""
		self.H.__sendByte__(CP.TIMING)
		self.H.__sendByte__(CP.GET_TIMING)
		timeout_msb = int((timeout*64e6))>>16
		self.H.__sendInt__(timeout_msb)
		self.H.__sendByte__( EVERY_RISING_EDGE<<2 | 2)
		self.H.__sendByte__(self.__calcDChan__(channel))
		tmt = self.H.__getInt__()
		x=[self.H.__getLong__() for a in range(2)]
		self.H.__get_ack__()
		if(tmt >= timeout_msb):return -1
		rtime = lambda t: t/64e6
		y=x[1]-x[0]
		return rtime(y)
	'''

    def r2r_time(self, channel, skip_cycle=0, timeout=5):
        """
		Return a list of rising edges that occured within the timeout period.
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ==============================================================================================================
		**Arguments**
		==============  ==============================================================================================================
		channel         The input to measure time between two rising edges.['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		skip_cycle      Number of points to skip. eg. Pendulums pass through light barriers twice every cycle. SO 1 must be skipped
		timeout         Number of seconds to wait for datapoints. (Maximum 60 seconds)
		==============  ==============================================================================================================
		:return list: Array of points
		"""
        if timeout > 60: timeout = 60
        self.start_one_channel_LA(channel=channel, channel_mode=3, trigger_mode=0)  # every rising edge
        startTime = time.time()
        while time.time() - startTime < timeout:
            a, b, c, d, e = self.get_LA_initial_states()
            if a == self.MAX_SAMPLES / 4:
                a = 0
            if a >= skip_cycle + 2:
                tmp = self.fetch_long_data_from_LA(a, 1)
                self.dchans[0].load_data(e, tmp)
                # print (self.dchans[0].timestamps)
                return [1e-6 * (self.dchans[0].timestamps[skip_cycle + 1] - self.dchans[0].timestamps[0])]
            time.sleep(0.1)
        return []

    def f2f_time(self, channel, skip_cycle=0, timeout=5):
        """
		Return a list of falling edges that occured within the timeout period.
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ==============================================================================================================
		**Arguments**
		==============  ==============================================================================================================
		channel         The input to measure time between two falling edges.['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		skip_cycle      Number of points to skip. eg. Pendulums pass through light barriers twice every cycle. SO 1 must be skipped
		timeout         Number of seconds to wait for datapoints. (Maximum 60 seconds)
		==============  ==============================================================================================================
		:return list: Array of points
		"""
        if timeout > 60: timeout = 60
        self.start_one_channel_LA(channel=channel, channel_mode=2, trigger_mode=0)  # every falling edge
        startTime = time.time()
        while time.time() - startTime < timeout:
            a, b, c, d, e = self.get_LA_initial_states()
            if a == self.MAX_SAMPLES / 4:
                a = 0
            if a >= skip_cycle + 2:
                tmp = self.fetch_long_data_from_LA(a, 1)
                self.dchans[0].load_data(e, tmp)
                # print (self.dchans[0].timestamps)
                return [1e-6 * (self.dchans[0].timestamps[skip_cycle + 1] - self.dchans[0].timestamps[0])]
            time.sleep(0.1)
        return []

    def MeasureInterval(self, channel1, channel2, edge1, edge2, timeout=0.1):
        """
		Measures time intervals between two logic level changes on any two digital inputs(both can be the same)
		For example, one can measure the time interval between the occurence of a rising edge on ID1, and a falling edge on ID3.
		If the returned time is negative, it simply means that the event corresponding to channel2 occurred first.
		returns the calculated time
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		channel1        The input pin to measure first logic level change
		channel2        The input pin to measure second logic level change
						 -['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		edge1           The type of level change to detect in order to start the timer
							* 'rising'
							* 'falling'
							* 'four rising edges'
		edge2           The type of level change to detect in order to stop the timer
							* 'rising'
							* 'falling'
							* 'four rising edges'
		timeout         Use the timeout option if you're unsure of the input signal time period.
						returns -1 if timed out
		==============  ============================================================================================
		:return : time
		.. seealso:: timing_example_
		"""
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.INTERVAL_MEASUREMENTS)
        timeout_msb = int((timeout * 64e6)) >> 16
        self.H.__sendInt__(timeout_msb)

        self.H.__sendByte__(self.__calcDChan__(channel1) | (self.__calcDChan__(channel2) << 4))

        params = 0
        if edge1 == 'rising':
            params |= 3
        elif edge1 == 'falling':
            params |= 2
        else:
            params |= 4

        if edge2 == 'rising':
            params |= 3 << 3
        elif edge2 == 'falling':
            params |= 2 << 3
        else:
            params |= 4 << 3

        self.H.__sendByte__(params)
        A = self.H.__getLong__()
        B = self.H.__getLong__()
        tmt = self.H.__getInt__()
        self.H.__get_ack__()
        # self.__print__(A,B)
        if (tmt >= timeout_msb or B == 0): return np.NaN
        rtime = lambda t: t / 64e6
        return rtime(B - A + 20)

    def DutyCycle(self, channel='ID1', timeout=1.):
        """
		duty cycle measurement on channel
		returns wavelength(seconds), and length of first half of pulse(high time)
		low time = (wavelength - high time)
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ==============================================================================================
		**Arguments**
		==============  ==============================================================================================
		channel         The input pin to measure wavelength and high time.['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		timeout         Use the timeout option if you're unsure of the input signal time period.
						returns 0 if timed out
		==============  ==============================================================================================
		:return : wavelength,duty cycle
		.. seealso:: timing_example_
		"""
        x, y = self.MeasureMultipleDigitalEdges(channel, channel, 'rising', 'falling', 2, 2, timeout, zero=True)
        if x != None and y != None:  # Both timers registered something. did not timeout
            if y[0] > 0:  # rising edge occured first
                dt = [y[0], x[1]]
            else:  # falling edge occured first
                if y[1] > x[1]:
                    return -1, -1  # Edge dropped. return False
                dt = [y[1], x[1]]
            # self.__print__(x,y,dt)
            params = dt[1], dt[0] / dt[1]
            if params[1] > 0.5:
                self.__print__(x, y, dt)
            return params
        else:
            return -1, -1
