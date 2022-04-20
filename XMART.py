import re, datetime, time
import glob, os, shutil
import subprocess, sys
from ftplib import FTP

dirpath = os.getcwd()

input_file = "XMART.dat"

exe_dir = (dirpath+"//Level_1//exe")
mohid_log = (exe_dir+"//Mohid.log")

#Define number of domains
number_of_domains = 1

#Define directories (comment when not applicable)
results_dir = [0]*number_of_domains
results_dir [0] = (dirpath+"//Level_1//res")
#results_dir [1] = (dirpath+"\\Level_1\\Level_2\\res")

data_dir = [0]*number_of_domains
data_dir [0] = (dirpath+"//Level_1//data")

backup_dir = [0]*number_of_domains
backup_dir [0] = (r"/dados3/mohidOutput")


boundary_conditions_dir = (dirpath+"//Level_1//GeneralData//BoundaryConditions")

dir_meteo = (r"/dados3/mohidInput/Teste/")
#file_name_meteo = "gfs.hdf5"

dir_father_phy = (r"/dados3/mohidInput/CMEMS")
file_name_phy = "Plataforma_SE.hdf5"
#file_name_phy = "Hydrodynamic_2.hdf5"

#dir_rivers = (r"/dados3/mohidInput/QSDC/")
dir_rivers = (r"/dados3/mohidInput/QMED/")

#Store ftp (No = 0 Yes = 1)
store_ftp = 0
#ftp_credentials_file = "ftp.dat"

timeseries_backup = 1
timeseries_dir = results_dir[0] + "//Run2"
#convert2netcdf_path = (r"C:\Aplica\PR_SC\Work\Hdf5toNetcdf\versao_netcdf_4")
#convert2netcdf_file = (r"C:\Aplica\PR_SC\Work\Hdf5toNetcdf\versao_netcdf_4\Convert2netcdf.dat")

#####################################################
def read_date():
	global initial_date
	global end_date
	global number_of_runs
	
	forecast_mode = 0
	refday_to_start = 0
	number_of_runs = 0
	
	with open(input_file) as file:
		for line in file:
			if re.search("^FORECAST_MODE.+:", line):
				number = line.split()
				forecast_mode = int(number[2])
				
	if forecast_mode == 1:
		with open(input_file) as file:
			for line in file:
				if re.search("^REFDAY_TO_START.+:", line):
					number = line.split()
					refday_to_start = int(number[2])
				elif re.search("^NUMBER_OF_RUNS.+:", line):
					number = line.split()
					number_of_runs = int(number[2])
					
		initial_date = datetime.datetime.now() + datetime.timedelta(days = refday_to_start)
		end_date = initial_date + datetime.timedelta(days = number_of_runs-1)
		
	else:	
		with open(input_file) as file:
			for line in file:
				if re.search("^START.+:", line):
					words = line.split()
					initial_date = datetime.datetime(int(words[2]),int(words[3]),int(words[4]),int(words[5]),int(words[6]),int(words[7]))
				elif re.search("^END.+:", line):
					words = line.split()
					end_date = datetime.datetime(int(words[2]),int(words[3]),int(words[4]),int(words[5]),int(words[6]),int(words[7]))
						
		interval = end_date - initial_date
		
		number_of_runs = interval.days	
#####################################################
def next_date (run):
	global next_start_date
	global next_end_date
		
	next_start_date = initial_date + datetime.timedelta(days = run)
	next_end_date = next_start_date + datetime.timedelta(days = 1)

#####################################################
def write_date(file_name):
		
	with open(file_name) as file:
		file_lines = file.readlines()
		
	number_of_lines = len(file_lines)
	
	for n in range(0,number_of_lines):
		line = file_lines[n]		
		if re.search("^START.+:", line):
			file_lines[n] = "START " + ": " + str(next_start_date.strftime("%Y %m %d ")) + "0 0 0\n"
			#file_lines[n] = "START " + ": " + str(next_start_date.strftime("%Y %m %d %H %M %S")) + "\n"

		elif re.search("^END.+:", line):	
			file_lines[n] = "END " + ": " + str(next_end_date.strftime("%Y %m %d ")) + "0 0 0\n"
			#file_lines[n] = "END " + ": " + str(next_end_date.strftime("%Y %m %d %H %M %S")) + "\n"
			
	with open(file_name,"w") as file:
		for n in range(0,number_of_lines) :
			file.write(file_lines[n])

#####################################################
def interpolate_gfs():

	os.chdir(interpolate_gfs_dir)
		
	write_date("Interpolate.dat")	
	output = subprocess.call(["Interpolate.bat"])
	
	hdf_files = glob.iglob(os.path.join(interpolate_gfs_dir, file_name_gfs))
	for file in hdf_files:
		shutil.copy(file, boundary_conditions_dir)
	
	files = glob.glob("*.hdf5")
	for filename in files:
		os.remove(filename)		
#####################################################
def copy_initial_files(level):

	initial_files_dir = (backup_dir[level]+"//"+str(old_start_date.strftime("%Y%m%d")) + "_" + str(old_end_date.strftime("%Y%m%d")))
	
	if os.path.exists(initial_files_dir):
		
		os.chdir(results_dir[level])
		
		files = glob.glob("*.fin*")
		for filename in files:
			os.remove(filename)
		
		files_fin = glob.iglob(os.path.join(initial_files_dir,"*_2.fin*"))
		for file in files_fin:
			if os.path.isfile(file):
				shutil.copy(file, results_dir[level])
					
		files_fin = glob.iglob(os.path.join(results_dir[level],"*_2.fin*"))
		for file in files_fin:
			if os.path.isfile(file):
				os.rename(file, file.replace("_2.fin","_1.fin"))
#####################################################
def backup(level):
	
	backup_dir_date = (backup_dir[level]+"//"+str(next_start_date.strftime("%Y%m%d")) + "_" + str(next_end_date.strftime("%Y%m%d")))
		
	if not os.path.exists(backup_dir_date):
		os.makedirs(backup_dir_date)
		
	os.chdir(results_dir[level])
	
	files = glob.glob("MPI*.*")
	for filename in files:
		os.remove(filename)
		
	result_files = glob.iglob(os.path.join(results_dir[level],"*.hdf5"))
	for file in result_files:
		shutil.copy(file, backup_dir_date)
		
	fin_files = glob.iglob(os.path.join(results_dir[level],"*_2.fin*"))
	for file in fin_files:
		shutil.copy(file, backup_dir_date)
		
	files = glob.glob("*.fin*")
	for filename in files:
		os.remove(filename)
	
	files = glob.glob("*.hdf5")
	for filename in files:
		os.remove(filename)

	if timeseries_backup == 1:
		os.chdir(timeseries_dir)
		files = glob.iglob(os.path.join(timeseries_dir,"*.*"))
		for file in files:
			shutil.copy(file, backup_dir_date)  
#####################################################
def read_keyword_value(keyword_name): 

	with open(ftp_credentials_file) as file:
		for line in file:
			if re.search("^"+keyword_name+".+: ", line):
				words = line.split()
				value = words[2]
				return value
#####################################################
def convert2netcdf(convert2netcdf_file, date, hdf_file):
		
	with open(convert2netcdf_file) as file:
		file_lines = file.readlines()
		
	number_of_lines = len(file_lines)
	
	for n in range(0,number_of_lines):
		line = file_lines[n]		
		if re.search("^HDF_FILE.+:", line):
			backup_dir_date = (backup_dir[level]+"\\" + date)
			file_lines[n] = "HDF_FILE " + ": " + backup_dir_date + "\\" + hdf_file + "\n"

		elif re.search("^NETCDF_FILE.+:", line):	
			file_lines[n] = "NETCDF_FILE " + ": " + convert2netcdf_path + "\\" + hdf_file + ".nc\n"
			
		elif re.search("^REFERENCE_TIME.+:", line):
			file_lines[n] = "REFERENCE_TIME " + ": " + str(next_start_date.strftime("%Y %m %d ")) + "0 0 0\n"
			
	with open(convert2netcdf_file,"w") as file:
		for n in range(0,number_of_lines) :
			file.write(file_lines[n])
	
	os.chdir(convert2netcdf_path)
	output = subprocess.call(["Convert2netcdf.exe"])

#####################################################

read_date()

for run in range (0,number_of_runs):	

	#Update dates
	next_date (run)
	
	#Pre-processing
	os.chdir(boundary_conditions_dir)
	files = glob.glob("*.hdf*")
	for filename in files:
		os.remove(filename)
				
	#Copy Meteo boundary conditions
	date_meteo_file = next_start_date - datetime.timedelta(days = 1)
	file_name_meteo = "wrfout_d01_"+str(date_meteo_file.strftime("%Y-%m-%d"))+".hdf5"
       #file_name_meteo = "m02_wrfout_d01_"+str(date_meteo_file.strftime("%Y-%m-%d"))+".hdf5"
	file_name_meteo_dir = dir_meteo+"//"+file_name_meteo
	shutil.copy(file_name_meteo_dir, boundary_conditions_dir)
	
	os.chdir(boundary_conditions_dir)
	os.rename(file_name_meteo, "wrf.hdf5")	
	
	#Copy ocean boundary conditions
	file_name_hydro = (dir_father_phy+"//"+str(next_start_date.strftime("%Y%m%d")) + "_" + str(next_end_date.strftime("%Y%m%d"))+"//"+file_name_phy)
	shutil.copy(file_name_hydro, boundary_conditions_dir)
	
	#Copy rivers boundary conditions
	#dir_rivers_date = (dir_rivers+"//"+str(next_start_date.strftime("%Y%m%d")))
	
	#river_files = glob.iglob(os.path.join(dir_rivers,"*.dat"))
	
	#for file in river_files:
	#	shutil.copy(file, boundary_conditions_dir)
		
	##############################################
	#MOHID
	
	#Update dates
	for level in range (0,number_of_domains):
		os.chdir(data_dir [level])
		write_date("Model_2.dat")
	
	#Copy initial files (.fin)	
	old_start_date = next_start_date - datetime.timedelta(days = 1)
	old_end_date = next_end_date - datetime.timedelta(days = 1)
	
	for level in range (0,number_of_domains):
		copy_initial_files(level)
	
	#Run
	os.chdir(exe_dir)
	output = subprocess.call(["/home/mohid/Aplica/SC_PR_SP/Level_1/exe/run.sh"])
	
	#if not ("Program Mohid Water successfully terminated") in open(mohid_log).read():
	#	sys.exit ("Program Mohid Water was not successfully terminated"+"\n"+"Check out Mohid log file")
	
	#Backup
	for level in range (0,number_of_domains):
		backup(level)
	
	#Store ftp
	if store_ftp == 1:
	
		level = 1 #Store ftp just for domain 2
	
		date = str(next_start_date.strftime("%Y%m%d")) + "_" + str(next_end_date.strftime("%Y%m%d"))
		
		convert2netcdf(convert2netcdf_file, date, "Hydrodynamic_2_Surface.hdf5")
		convert2netcdf(convert2netcdf_file, date, "WaterProperties_2_Surface.hdf5")
		
		os.chdir(dirpath)
		
		keyword_name = ("server","user","password")
		number_of_keywords = len(keyword_name)

		keyword_value = [0]*number_of_keywords
		
		for n in range (0,number_of_keywords):
			keyword_value[n] = read_keyword_value(keyword_name[n])

		server = keyword_value[0]
		user = keyword_value[1]
		password = keyword_value[2]

		ftp=FTP(server)
		ftp.login(user,password)

		ftp.cwd("/home/maretec/ftplocal/PR_SC/")
		
		if not date in ftp.nlst():
			ftp.mkd(date)
			
		ftp.cwd(date)
		
		os.chdir(convert2netcdf_path)
		
		filename = "Hydrodynamic_2_Surface.hdf5.nc"
		#ftp.set_pasv(False)
		ftp.storbinary('STOR '+filename,open(filename,'rb'))
		
		filename = "WaterProperties_2_Surface.hdf5.nc"
		#ftp.set_pasv(False)
		ftp.storbinary('STOR '+filename,open(filename,'rb'))
		
		backup_dir_date = (backup_dir[level]+"\\" + date)
		os.chdir(backup_dir_date)
		filename = "Hydrodynamic_2_Surface.hdf5"
		#ftp.set_pasv(False)
		ftp.storbinary('STOR '+filename,open(filename,'rb'))

		ftp.quit()
