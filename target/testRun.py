import sys
import multiprocessing
import os
import time
import pandas as pd
import csv
import subprocess
from multiprocessing import Process, Manager, Value
from datetime import datetime

RESULT_FILE_PATH="results.csv"
INPUT_FILE_PATH="tests.csv"
global timeout
HOME=os.environ['HOME']

if sys.argv[1] == '-t':
    timeout = (int)(sys.argv[2])

if sys.argv[3] == '-tn':
    testNum = (int)(sys.argv[4])
	
# check number of rows
list = pd.read_csv(INPUT_FILE_PATH)
rows = len(list.index)

def timeoutfun(timeout,exit_flag):
	while exit_flag[0]!=1 and timeout>0:
		time.sleep(1)
		timeout=timeout-1
	exit_flag[0]=1
	os._exit(0)
	
def create_testresultcsv():
    if os.path.exists(RESULT_FILE_PATH):
        os.remove(RESULT_FILE_PATH)
    header = ['testnumber','time','folder','command','status']
    with open(RESULT_FILE_PATH, 'w') as f:
    # create the csv writer
        writer = csv.writer(f)
    # write a row to the csv file
        writer.writerow(header)
        f.close()
	
def copy_to_excel(line):
	li = line.split(",")
	if(li[0]=='TEST_RESULT'):
		del li[0]
		li = [x.replace("\r\n","") for x in li]
		with open(RESULT_FILE_PATH, 'a+') as f:
		# create the csv writer
			writer = csv.writer(f)
		# write a row to the csv file
			writer.writerow(li)
			f.close()	
		
def set_and_run(test_number,test_folder,test_command,exit_flag):
	os.environ["EnableRecoverablePageFaults"] = "0"
	os.environ["IGC_DisableWriteCombine"] = "1"
	os.environ["PrintDebugSettings"] = "1"
	os.environ["BatchBufferStartPrepatchingWaEnabled"] = "1"
	os.environ["DirectSubmissionForceLocalMemoryStorageMode"] = "2"
	
	if test_folder.find('binocle') != -1:
		os.environ["UseDrmVirtualEnginesForCcs"] = "0"
	
	if test_folder.find('projection_kernel_only_in_openmp') != -1:
		os.environ["LIBOMPTARGET_PLUGIN"] = "opencl"
		os.environ["I_MPI_OFFLOAD_DEVICE_LIST"] = "0,0,0,0,1,1,1,1"
		os.environ["OMP_TARGET_OFFLOAD"] = "MANDATORY"
		os.environ["I_MPI_DEBUG"] = "3"
		os.environ["LIBOMPTARGET_DEBUG"] = "1"

	#create the log folder
	basePath=os.path.join(envPath,'logs/','Combination'+str(testNum))
	#if os.path.exists(basePath):
	#	os.system('rm -rf {0}'.format(basePath))
	#os.system('mkdir -p {0}'.format(basePath))
	logpath=os.path.join(basePath,str(test_number)+".log")

	#Run a lot of times; till we say no!!
	while exit_flag[0] != 1:
		print("-------------------Test Started---------------------")
		os.chdir(HOME)
		os.chdir(test_folder)
		
		if test_folder.find('OpenCV') != -1:
			path = os.getcwd()
			os.environ["LD_LIBRARY_PATH"] = path
			
		if test_folder.find('HCPBench') != -1:
			os.chdir('../HCPBenchSYCLlib')
			path = os.getcwd()
			os.environ["LD_LIBRARY_PATH"] = path
			#os.chdir(HOME)
			#os.chdir(test_folder)
		
		timestamp = str(datetime.now())
		env = str(os.environ)

		with open(logpath,"w+") as f:
			testnumber = str(test_number)
			result = "TEST STARTED"
			os.chdir(basePath)
			print("[TEST_PROGRESS,"+testnumber+","+timestamp+","+test_folder+","+test_command+","+result+"]")
			os.chdir(basePath)
			copy_to_excel("TEST_RESULT,"+testnumber+","+timestamp+","+test_folder+","+test_command+","+result+"")
			f.write("\n[ENV VARIABLES: ,"+env+"]\n")
			os.chdir(HOME)
			os.chdir(test_folder)
			try:
				#value=subprocess.call(""+test_command+" && echo $?", shell=True, stdout=f, stderr=subprocess.PIPE)
				value=subprocess.call(""+test_command+" && echo $?", shell=True, stdout=f, stderr=f)
			except subprocess.TimeoutExpired:
				f.write("We have a timeout...exiting")
				result = "TEST FAILED"
		
			if value !=0:
				result = "TEST FAILED"
			else:
				result = "TEST PASSED"
			
			#testnumber = str(test_number)
			f.write("\n[TEST_RESULT,"+testnumber+","+timestamp+","+test_folder+","+test_command+","+result+"]\n")
			print("[TEST_RESULT,"+testnumber+","+timestamp+","+test_folder+","+test_command+","+result+"]")
			os.chdir(basePath)
			copy_to_excel("TEST_RESULT,"+testnumber+","+timestamp+","+test_folder+","+test_command+","+result+"")
			f.write("-------------------Test Ended---------------------")
			print("-------------------Test Ended---------------------")
			
			f.close()
	
def main():
	global envPath
	envPath=os.getcwd()
	
	# check results file and create one if it does not exists
	#checkFile = os.path.isfile('results.csv')
	#if checkFile == False:
	#	create_testresultcsv()
	
	basePath=os.path.join(envPath,'logs/','Combination'+str(testNum))
	if os.path.exists(basePath):
		os.system('rm -rf {0}'.format(basePath))
	os.system('mkdir -p {0}'.format(basePath))
	os.chdir(basePath)
	
	# check results file and create one if it does not exists
	checkFile = os.path.isfile('results.csv')
	if checkFile == False:
		create_testresultcsv()
	os.chdir(envPath)
	#envPath=os.getcwd()

	processes = []
	tprocesses = []

	manager = Manager()
	exit_flag = manager.list(range(2))

	# calculate rows we need to go after
	a = testNum*5 - 4
	df = pd.read_csv(INPUT_FILE_PATH, skiprows = [i for i in range(1,a)], nrows = 5, encoding = 'unicode_escape')
		
	for index, row in df.iterrows():
		p = multiprocessing.Process(target=set_and_run,args=(row['testnumber'],row['folder'],row['command_line'],exit_flag))
		p.start()
		processes.append(p)
		
	timer_process = multiprocessing.Process(target=timeoutfun,args=(timeout,exit_flag))
	timer_process.start()
	tprocesses.append(timer_process)
	
	for p in processes:
		p.join()
		
	for timer_process in tprocesses:
		timer_process.join()
		
if __name__=="__main__": 

    main()

    os._exit(0) 