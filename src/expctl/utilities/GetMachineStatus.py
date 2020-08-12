# -*- coding: utf-8 -*-

def GetStatus(DeviceManager, MonitorSeq):
	status = DeviceManager.Run(MonitorSeq)
	return status
