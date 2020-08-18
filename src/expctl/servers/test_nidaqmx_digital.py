import nidaqmx
from nidaqmx.constants import LineGrouping
#from nidaqmx.constants.Signal import SAMPLE_CLOCK, START_TRIGGER, EXTERNAL
from nidaqmx.constants import Signal
import math 
import numpy as np

with nidaqmx.Task() as task:
	task.do_channels.add_do_chan(
		'PCI6537/line0:31',
		line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)

	# WHAT did the old code do?
	localMHz=1e6
	seq_duration = 1e3 #1ms #float(seq.TIME_STOP) # microseconds
	timeout = 10.0 # (seconds)
	sample_rate = 10.0  # number of samples per microsecond (clock speed in MHz)
	samps_per_channel = int(math.ceil(sample_rate*seq_duration)+1) # MHz * us (+1 for steady_state_value)
	buffer_size = samps_per_channel # number of samples
	print(buffer_size)
	
	# task_handle = device.CreateTask(server.task_id) # Create task OK
	# device.CreateDOChan(task_handle, b"all_channels") # Create all channels OK
	# device.ConfigureTiming(task_handle, params) 
	# calls dll.DAQmxCfgSampClkTiming(task_handle, params.clock_source, params.sample_rate,
	#                               self.Rising, self.FiniteSamps, params.buffer_size)
	# def cfg_samp_clk_timing(
	#         self, rate, source="", active_edge=Edge.RISING,
	#         sample_mode=AcquisitionType.FINITE, samps_per_chan=1000)

	task.timing.cfg_samp_clk_timing(rate=sample_rate*localMHz, source="RTSI7", samps_per_chan=samps_per_channel)


	# device.ExportSampleClockSignal(task_handle, line="PFI4")
	# API call to dll.DAQmxExportSignal(task_handle, int32(self.SampleClock), ctypes.create_string_buffer(line))
	#export_signal(self, signal_id, output_terminal)
	# NOT USED task.export_signal(SAMPLE_CLOCK, output_terminal="PFI4")

	# device.ExportStartTrigger(task_handle, line=b"PFI4") # Trigger output for other devices
	task.export_signals.export_signal(Signal.START_TRIGGER, output_terminal="PFI4")
	
	# device.ExternalSampleClock(task_handle, b"RTSI7", 10e6) # Define external clock frequency
	# int32 DAQmxSetSampClkSrc(TaskHandle taskHandle, const char *data);
	# int32 DAQmxSetSampClkRate(TaskHandle taskHandle, float64 data);
	# maybe done by cfg_samp_clk_timing? 
	#task.timing.samp_clk_src = "RTSI7"
	#task.timing.samp_clk_rate = 10e6
	print(task.timing.samp_clk_src)
	print(task.timing.samp_clk_rate)

	
	# device.DigitalWriteU32(task_handle, params, seq_data) # Upload sequence data
	# calls DAQmxWriteDigitalU32
	#print('1 Channel N Lines N Samples Unsigned Integer Write: ')
	seq_data = np.zeros(buffer_size, dtype=np.uint32)
	for i in range(0, 1000, 10):
		seq_data[i:i+5] = 0xffffffff

	task.write(seq_data, auto_start=True)

	#task.start()
	task.wait_until_done(timeout=10.0)
	# print("  Starting task ID "+str(server.task_id)+" (task_handle: "+str(task_handle.value)+")...")
	# device.StartTask(task_handle) # Start the experiment
	# device.WaitUntilTaskDoneOrBreak(task_handle)
	# device.cleanupTask(task_handle)

  