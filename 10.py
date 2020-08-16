 def __start_ctmu__(self, Crange, trim, tgen=1):
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.START_CTMU)
        self.H.__sendByte__((Crange) | (tgen << 7))
        self.H.__sendByte__(trim)
        self.H.__get_ack__()

    def __stop_ctmu__(self):
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.STOP_CTMU)
        self.H.__get_ack__()

    def resetHardware(self):
        """
		Resets the device, and standalone mode will be enabled if an OLED is connected to the I2C port
		"""
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.RESTORE_STANDALONE)

    def read_flash(self, page, location):
        """
		Reads 16 BYTES from the specified location
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		================    ============================================================================================
		**Arguments**
		================    ============================================================================================
		page                page number. 20 pages with 2KBytes each
		location            The flash location(0 to 63) to read from .
		================    ============================================================================================
		:return: a string of 16 characters read from the location
		"""
        self.H.__sendByte__(CP.FLASH)
        self.H.__sendByte__(CP.READ_FLASH)
        self.H.__sendByte__(page)  # send the page number. 20 pages with 2K bytes each
        self.H.__sendByte__(location)  # send the location
        ss = self.H.fd.read(16)
        self.H.__get_ack__()
        return ss

    def read_bulk_flash(self, page, numbytes):
        """
		Reads BYTES from the specified location
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		================    ============================================================================================
		**Arguments**
		================    ============================================================================================
		page                Block number. 0-20. each block is 2kB.
		numbytes               Total bytes to read
		================    ============================================================================================
		:return: a string of 16 characters read from the location
		"""
        self.H.__sendByte__(CP.FLASH)
        self.H.__sendByte__(CP.READ_BULK_FLASH)
        bytes_to_read = numbytes
        if numbytes % 2: bytes_to_read += 1  # bytes+1 . stuff is stored as integers (byte+byte) in the hardware
        self.H.__sendInt__(bytes_to_read)
        self.H.__sendByte__(page)
        ss = self.H.fd.read(int(bytes_to_read))
        self.H.__get_ack__()
        if numbytes % 2: return ss[:-1]  # Kill the extra character we read. Don't surprise the user with extra data
        return ss

    def write_flash(self, page, location, string_to_write):
        """
		write a 16 BYTE string to the selected location (0-63)
		DO NOT USE THIS UNLESS YOU'RE ABSOLUTELY SURE KNOW THIS!
		YOU MAY END UP OVERWRITING THE CALIBRATION DATA, AND WILL HAVE
		TO GO THROUGH THE TROUBLE OF GETTING IT FROM THE MANUFACTURER AND
		REFLASHING IT.
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		================    ============================================================================================
		**Arguments**
		================    ============================================================================================
		page                page number. 20 pages with 2KBytes each
		location            The flash location(0 to 63) to write to.
		string_to_write     a string of 16 characters can be written to each location
		================    ============================================================================================
		"""
        while (len(string_to_write) < 16): string_to_write += '.'
        self.H.__sendByte__(CP.FLASH)
        self.H.__sendByte__(CP.WRITE_FLASH)  # indicate a flash write coming through
        self.H.__sendByte__(page)  # send the page number. 20 pages with 2K bytes each
        self.H.__sendByte__(location)  # send the location
        self.H.fd.write(string_to_write)
        time.sleep(0.1)
        self.H.__get_ack__()

    def write_bulk_flash(self, location, data):
        """
		write a byte array to the entire flash page. Erases any other data
		DO NOT USE THIS UNLESS YOU'RE ABSOLUTELY SURE YOU KNOW THIS!
		YOU MAY END UP OVERWRITING THE CALIBRATION DATA, AND WILL HAVE
		TO GO THROUGH THE TROUBLE OF GETTING IT FROM THE MANUFACTURER AND
		REFLASHING IT.
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		================    ============================================================================================
		**Arguments**
		================    ============================================================================================
		location            Block number. 0-20. each block is 2kB.
		bytearray           Array to dump onto flash. Max size 2048 bytes
		================    ============================================================================================
		"""
        if (type(data) == str): data = [ord(a) for a in data]
        if len(data) % 2 == 1: data.append(0)

        self.H.__sendByte__(CP.FLASH)
        self.H.__sendByte__(CP.WRITE_BULK_FLASH)  # indicate a flash write coming through
        self.H.__sendInt__(len(data))  # send the length
        self.H.__sendByte__(location)
        for n in range(len(data)):
            self.H.__sendByte__(data[n])
        self.H.__get_ack__()

        # verification by readback
        tmp = [ord(a) for a in self.read_bulk_flash(location, len(data))]
        print('Verification done', tmp == data)
        if tmp != data: raise Exception('Verification by readback failed')

    # -------------------------------------------------------------------------------------------------------------------#

    # |===============================================WAVEGEN SECTION====================================================|
    # |This section has commands related to waveform generators W1, W2, PWM outputs, servo motor control etc.            |
    # -------------------------------------------------------------------------------------------------------------------#

    def set_wave(self, chan, freq):
        """
		Set the frequency of wavegen
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		chan       	Channel to set frequency for. W1 or W2
		frequency       Frequency to set on wave generator
		==============  ============================================================================================
		:return: frequency
		"""
        if chan == 'W1':
            self.set_w1(freq)
        elif chan == 'W2':
            self.set_w2(freq)
