import sys
import multiprocessing
import os
import logging
import time
import pandas as pd
import csv
import subprocess
import paramiko
from multiprocessing import Process, Manager, Value

import namednodes
namednodes.sv.initialize()
namednodes.sv.get_all()

from common import baseaccess
if baseaccess.getaccess() != 'tssa':
	import itpii
	itp = itpii.baseaccess() 

BASE_PATH="stress_automation/"
BASE_TEST_PATH="stress_automation/tests.csv"
testNum = 1

## The script needs to have four arguments
## [args 1-2] : -h - host IP address
## [args 3-4] : -u - username for ssh access
## [args 5-6] : -pw - password for ssh access
## [args 7-8] : -H - number of hours to run the test
## [args 9-10]: -M - number of minutes to run the test [the time is a cumulative of #hours and #minutes]

HOST = sys.argv[1]
if HOST == '-h':
    host = sys.argv[2]
     
USERNAME = sys.argv[3]
if USERNAME == '-u':
    username = sys.argv[4]
    
PASSWORD = sys.argv[5]
if PASSWORD == '-pw':
    password = sys.argv[6]

HOUR = sys.argv[7]
if HOUR == '-H':
	hour = (int)(sys.argv[8])
	
MINUTE = sys.argv[9]
if MINUTE == '-M':
	minute = (int)(sys.argv[10])
	
totaltime=(hour*3600)+(minute*60)

def timeoutfun(totaltime,exit_flag):
	while exit_flag[0]!=1 and totaltime>0:
		time.sleep(1)
		totaltime=totaltime-1
	exit_flag[0]=1
	exit()
	
def checkSystem():
	TIMEOUT = 180	
	while TIMEOUT > 0:
		t = os.system('ping -n 4 {0} | find "Reply" > nul'.format(host))
		if t == 0:
			return t
		else:
			print("Trying to reach the target IP")
			time.sleep(1)
			TIMEOUT=TIMEOUT-1
	return t

def logging(testNum):
	print(" =========== In LOGGING function =========== ")
	#PYSV_PROJECT = "pontevecchio"  # PySV name for the PO project
	#PYSV_REPO = fr"C:\pythonsv\{PYSV_PROJECT}"  # PySV Project Repo
	#sys.path.append(PYSV_REPO)
	# Change working directory to pontevecchio to allow SVN update and make sure PythonSV scripts don't get lost with paths
	#os.chdir(PYSV_REPO)
	 
	#itp.unlock()
	#print(" =========== Initialize svtools =========== ")
	# The scripts below are fully provided by the SV team and should appear as a result of svn checkout / svn update
	#import startpvc_auto       # update per project
	#startpvc_auto.auto_main()  # update per project

	dir="C:\Stress"
	if not os.path.exists(dir):
		os.makedirs(dir)
			
	os.chdir(dir)
	logName='Combination'+str(testNum)+".log"
	log(r"{0}".format(logName))
	print("\n++++++++++++++++++++++++++++++++++++++++++++++++++LOGGING - IPEHR++++++++++++++++++++++++++++++++++++++++++++\n")
	sv.gfxcard0.tiles.gfx.gtgp.showsearch("ipehr")
	print("\n++++++++++++++++++++++++++++++++++++++++++++++++++LOGGING - INSTDONE+++++++++++++++++++++++++++++++++++++++++\n")
	sv.gfxcard0.tiles.gfx.gtgp.showsearch("instdone_ccs")
	print("\n++++++++++++++++++++++++++++++++++++++++++++++++++LOGGING - GTSTATUS+++++++++++++++++++++++++++++++++++++++++\n")
	import pontevecchio.debug.domains.gfx.gt.gtStatus as gs
	gs.status()
	print("\n++++++++++++++++++++++++++++++++++++++++++++++++++LOGGING - SOC LOG++++++++++++++++++++++++++++++++++++++++++\n")
	import pontevecchio.fv.ras.error_logging_modules.soc_error_log as soc
	soc.soc_error_log()
	#from pontevecchio.debug.domains.gfx.tools.scandump import pvcgfxscanAFD as pvcgfxscanAFD
	#pvcgfxscanAFD.gtScandump()
	nolog()

## boot system
def reset():
	#PYSV_PROJECT = "pontevecchio"  # PySV name for the PO project
	#PYSV_REPO = fr"C:\pythonsv\{PYSV_PROJECT}"  # PySV Project Repo
	#sys.path.append(PYSV_REPO)
	# Change working directory to pontevecchio to allow SVN update and make sure PythonSV scripts don't get lost with paths
	#os.chdir(PYSV_REPO)
	 
	#itp.unlock()
	#print(" =========== Initialize svtools =========== ")
	# The scripts below are fully provided by the SV team and should appear as a result of svn checkout / svn update
	#import startpvc_auto       # update per project
	#startpvc_auto.auto_main()  # update per project
	 
	import toolext.bootscript.boot as b
	b.clean_up_vars()
	#ratio10_ovrd0 = ["fuses.punit.pcode_gt_p0_ratio=0x10",
	#"fuses.punit.pcode_gt_p0_ratio_systolic=0x10",
	#"fuses.punit.pcode_gt_p0_ratio_compute=0x10",
	#"fuses.punit.pcode_gt_p1_ratio=0x10",
	#"fuses.punit.pcode_gt_p1_ratio_systolic=0x10",
	#"fuses.punit.pcode_gt_p1_ratio_compute=0x10",
	#"fuses.punit.pcode_gt_pn_ratio=0x10",
	#"fuses.punit.pcode_gt_min_ratio=0x10",
	#"fuses.punit.pcode_gt_p0_ratio_media_ff=0x10",
	#"fuses.punit.pcode_gt_p1_ratio_media_ff=0x10",
	#"fuses.punit.pcode_gt_max_chiplet_ifc_multiplier=0x40"]
	#status = b.go(pwrgoodmethod='usb',sfo_qdf="QZNW", num_host_wr=1, fusestr=ratio10_ovrd0)
	status = b.go() 
	#status = b.go(fusestr0= cdyn_plus_eu_load_line_tile0, fusestr1 = cdyn_plus_eu_load_line_tile1,pwrgoodmethod='usb',sfo_qdf="QZNW", num_host_wr=1)
	# LNDEC WA
	#sv.gfxcards.tiles.gfx.gtgp.unslcgctl9434.cg3ddislnhdecgp=1
	#clear errors
	import fv.ras.error_logging_modules.ieh_error_logging as ie
	ie.log_errors()
	import fv.ras.pcie_errors as pe
	pe.clear_errors()
	
	itp.halt()
	itp.breaks.machinecheck = 1
	itp.go()
	
	import pontevecchio.debug.domains.gfx.gt.gtPmStatus as pms
	pms.dumpGtFrequency(None)
	
	#if type == "log":
	#	dir="C:\Stress"
	#	if not os.path.exists(dir):
	#		os.makedirs(dir)
				
	#	os.chdir(dir)
	#	logName=str(testNum)+".log"
	#	log(r"{0}".format(logName))
	#	print("\n++++++++++++++++++++++++++++++++++++++++++++++++++LOGGING - IPEHR++++++++++++++++++++++++++++++++++++++++++++\n")
	#	sv.gfxcard0.tiles.gfx.gtgp.showsearch("ipehr")
	#	print("\n++++++++++++++++++++++++++++++++++++++++++++++++++LOGGING - INSTDONE+++++++++++++++++++++++++++++++++++++++++\n")
	#	sv.gfxcard0.tiles.gfx.gtgp.showsearch("instdone_ccs")
	#	print("\n++++++++++++++++++++++++++++++++++++++++++++++++++LOGGING - GTSTATUS+++++++++++++++++++++++++++++++++++++++++\n")
	#	import pontevecchio.debug.domains.gfx.gt.gtStatus as gs
	#	gs.status()
	#	print("\n++++++++++++++++++++++++++++++++++++++++++++++++++LOGGING - SOC LOG++++++++++++++++++++++++++++++++++++++++++\n")
	#	import pontevecchio.fv.ras.error_logging_modules.soc_error_log as soc
	#	soc.soc_error_log()
	#	#from pontevecchio.debug.domains.gfx.tools.scandump import pvcgfxscanAFD as pvcgfxscanAFD
	#	#pvcgfxscanAFD.gtScandump()
	#	nolog()
	
	print(f"exited with status = {status}")
	print(" =========== PythonSV based boot finished =========== ")

	status = checkSystem()
	
	if status == 0:
		time.sleep(120)
		loadDriver()
	else:
		print("System is unreachable. Please check.")
		
	# Apply WA
	#log(r"C:\Stress\WA.log")
	import pontevecchio.debug.domains.gfx.gt.gtPmStatus as pms
	pms.dumpGtFrequency(None)
	sv.gfxcards.tiles.gfx.gtgp.showsearch("ff_slice_cs_chicken2_cc")
	sv.gfxcards.tiles.gfx.gtgp.ff_slice_cs_chicken2_cccsunit_be_common = 0x80008000
	sv.gfxcards.tiles.gfx.gtgp.ff_slice_cs_chicken2_ccsunit0_be_common = 0x80008000
	sv.gfxcards.tiles.gfx.gtgp.ff_slice_cs_chicken2_ccsunit1_be_common = 0x80008000
	sv.gfxcards.tiles.gfx.gtgp.ff_slice_cs_chicken2_ccsunit2_be_common = 0x80008000
	sv.gfxcards.tiles.gfx.gtgp.ff_slice_cs_chicken2_ccsunit3_be_common = 0x80008000
	sv.gfxcards.tiles.gfx.gtgp.showsearch("ff_slice_cs_chicken2_cc")
	#nolog()
	
## Load the driver; and check if i915 is loaded. Exit otherwise.
def loadDriver():
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(host, 22, username, password)
	stdin, stdout, stderr = ssh.exec_command('sudo modprobe i915; if lsmod | grep i915; then echo "Module Loaded"; echo 300 | sudo tee /sys/class/drm/card1/gt/gt0/rps_min_freq_mhz; echo 300 | sudo tee /sys/class/drm/card1/gt/gt1/rps_min_freq_mhz; for i in /sys/class/drm/card*/engine/*/heartbeat_interval_ms; do echo 0 | sudo tee $i; done; for i in /sys/class/drm/card*/engine/*/preempt_timeout_ms; do echo 0 | sudo tee $i; done; for i in /sys/class/drm/card*/engine/*/max_busywait_duration_ns; do echo 0 | sudo tee $i; done; for i in /sys/class/drm/card*/engine/*/stop_timeout_ms; do echo 0 | sudo tee $i; done; else echo "Module Not Loaded"; while :; do echo "Hit CTRL+C to stop  "; sleep 1; done; fi', get_pty=True)
	stdin.write(password)
	stdin.write("\n")
	stdin.flush()
	for line in iter(stdout.readline,""): 
		print(line)

## python installation; required for the host side script to work
def setupPython():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, username, password)
    stdin, stdout, stderr = ssh.exec_command('yes | sudo apt-get install python3-pandas; python3 --version; yes | sudo apt-get install python3-prettytable', get_pty=True)
    stdin.write(password)
    stdin.write("\n")   
    stdin.flush()
    for line in iter(stdout.readline,""): 
        print(line)

## download test csv
def setupResults():
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(host, 22, username, password)
	# get the test file
	sftp=ssh.open_sftp()
	sftp.get(BASE_TEST_PATH,'tests.csv')
	sftp.close()
	
	# get number of tests and setup log folder
	list = pd.read_csv('tests.csv')
	rows = len(list.index)
	testsAvailable = int(rows/5)
	
	stdin, stdout, stderr = ssh.exec_command('cd $HOME/{0}; mkdir -p logs'.format(BASE_PATH), get_pty=True)

def runTest(exit_flag,testNum):
	#system check
	#status = checkSystem()
	#if status != 0:
	#	reset(testNum)
	
	if exit_flag[0] != 1:
		try:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(host, 22, username, password)
			stdin, stdout, stderr = ssh.exec_command('cd $HOME/{0}; python3 testRun.py -t {1} -tn {2}'.format(BASE_PATH,totaltime,testNum), get_pty=True)
			#stdin.write(password)
			#stdin.write("\n")   
			#stdin.flush()
			for line in iter(stdout.readline,""): 
				print(line)
		except KeyboardInterrupt:
			pass
	else:
		exit()
		
def targetLog(exit_flag,testNum):
	#create the log folder
	basePath=os.path.join(BASE_PATH,'logs/','Combination'+str(testNum))
	os.system('mkdir -p {0}'.format(basePath))

	if exit_flag[0] != 1:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host, 22, username, password)
		stdin, stdout, stderr = ssh.exec_command('dmesg -wT > $HOME/{0}/dmesg.log'.format(basePath), get_pty=True)
		#stdin.write(password)
		#stdin.write("\n")   
		#stdin.flush()
		for line in iter(stdout.readline,""): 
			print(line)
	
def main():
	global testNum
	global exit_flag
	global type
	#setupPython()
	setupResults()
	# check number of rows
	list = pd.read_csv('tests.csv')
	rows = len(list.index)
	#loadDriver()
	reset()

	manager = Manager()
	#exit_flag = 0
	exit_flag = manager.list(range(2))

	TIMEOUT = totaltime+60 #adding additional time for host-DUT latency; log dump etc

	testsAvailable = int(rows/5)
	while testNum <= testsAvailable:
		exit_flag[0]=0
		
		start_test = multiprocessing.Process(target=runTest,args=(exit_flag,testNum))
		start_test.daemon = True
		start_test.start()
		start_test.join(TIMEOUT)
		
		start_log = multiprocessing.Process(target=targetLog,args=(exit_flag,testNum))
		start_log.daemon = True
		start_log.start()
		start_log.join(TIMEOUT)
		
		if start_test.is_alive():
			print("Remote time should be completed by now!!")
			start_test.terminate()
			start_log.terminate()
			print("Run terminated. All seems well. Please check logs on system under logs/testNum folder.")
			
			# check if the IP is reachable
			status = checkSystem()
			if status != 0:
				logging(testNum)
				reset()
								
		#print("+++++++++++++++++++ BEFORE LOGGING +++++++++++++++++++++++")
		logging(testNum)
		print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX END OF TEST XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
		reset()
		testNum += 1
		
if __name__=="__main__": 
	PYSV_PROJECT = "pontevecchio"  # PySV name for the PO project
	PYSV_REPO = fr"C:\pythonsv\{PYSV_PROJECT}"  # PySV Project Repo
	sys.path.append(PYSV_REPO)
	# Change working directory to pontevecchio to allow SVN update and make sure PythonSV scripts don't get lost with paths
	os.chdir(PYSV_REPO)
	 
	itp.unlock()
	print(" =========== Initialize svtools =========== ")
	# The scripts below are fully provided by the SV team and should appear as a result of svn checkout / svn update
	import startpvc_auto       # update per project
	startpvc_auto.auto_main()  # update per project

	main()

	exit() 