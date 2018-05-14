##!/opt/support/bin/python3

####################################################################################################################
##
## AUTHOR: Harikishan Mulagada
## ROLE  : Staff Engineering SteelCentral
##
## 03/22/17 - Added core file count and core file names to be written in systemdetails.txt
## 03/22/17 - Added SEVERE in the list of search string
## 03/22/17 - Added latest backtrace file info in errorsandwarns.txt
## 04/04/17 - Comment to look into errorsandwarns for backtrace on latest core
## 04/05/17 - Added system info to systemdetails.txt from bios_serial_number.txt
## 04/06/17 - Added Physical Drives status and count from storcli.txt to systemdetails.txt
##            (Bad code - remove harcoding of index values and arthimetic to get the index value)
## 04/07/17 - Added version of code to be pulled from .yaml files in opt/versions.
##            Check if more necessary details can be pulled from list of available yaml files
## 04/11/17 - movefiles function to move the output files to loaction of the tar file.
##            check with EE's -
##                          A. Keep the same location and add case#
##                          B. Move the file to tar file location where they create a folder for each case
## 04/12/17 - Added case number to be entered which is appended to output files
##            Cleaning up unzipped folder
## 04/13/17 - Moving output files to location of the dump file. If the file exists remove the existing file
##            and move the new file.
## 04/14/17 - Ran into 'UnicodeDecodeError' when opening 'temporal_data_store_rmp-reportmanagerd.log'
##            (\data\log\temporal_data_store\)
##            Added try catch block to catch the exception and skip the file which have different encoding
##            Changed number of lines from backtrace to be written from 70 to 100
## 05/16/17 - Get list of .sqlite files. Function to connect to dabatase. Currently we have only metrics.sqlite
##            Generating 3 dat files for cpu,memory and probe.
## 05/19/17 - Added check for case number. If entered case number is not numeric do not proceed until
##            until valid numeric value is entered
## 06/02/17 - Gripen will have log 'manage.log' for dbperf module which will give latest status of the module
##            'Enabled' or 'Disabled'. Function to read the file and write the status
##            Added logic to get list of '.json' and '.conf' files. Might be useful later
## 06/20/17 - isnumeric is not a valid function in Python 2. Changed it to isdigit.
## 07/13/17 - Changed logic to pick the first core file from the list instead of last. The list sorted. So we should
##            get the latest core dump and not the oldest
## 08/03/17 - Added logic to look into feature status file to get the latest status of modules and licensing
##            Added logic to print dbperf history like when was it enabled/disabled etc from manage.log
## 08/07/17 - Added logic to get the latest core dumps for each process and write the back trace of latest dump for each
##            only. The previous logic added 07/13 is faulty.
## 08/10/17 - Added logic to get the approximate reboot time from boot.log.Currently we do not have lastb call in the sysdump. boot.log modified timestamp might
##            be the best bet.
## 08/21/17 - The script will unzip the sysdump in the same location as the sysdump
##            No cleanup is being done. If the unzipped folder exist we continue with analysis
##            No deleting folders at the start or end of the script. This was necessary earlier because .tgz was being
##            unzipped locally and output files were created and then all folders were deleted
##            Deleting only output files if they already exist
##            Logic to count the number of hostgroups from JSON file
## 08/28/17 - Added logic for openfile function to use encoding utf8 so it does not fail on opening any UNICODE
##            files - e.g - hostgroup json
## 09/06/17 - Added io.open since encoding ut8 option in openfile function will not work with python 2.x
## 09/06/17 - Added except block to catch OSError since python 2.x does not support PermissionError
## 09/06/17 - Tested placing the script in same location as sysdump and it does not change how the script runs nor does delete
##            anything unnecessarily
## 09/06/17 - Added logic to get the storage layout information
## 10/10/17 - Added logic to change permissions on the unzipped folder and files so other users can access
##	      Added logic to look for rollup processor to determine possible probe hangs
## 10/11/17 - Added logic to look for slab file messages to check the buffers in npm_capture
## 10/30/17 - Added logic to look for symptoms on BUG 291485
## 11/02/17 - Added logic to get the timezone of the apppliance from timezone.txt. The file is new from Harrier release
## 11/03/17 - Added logic to extract and work in proper workdir. Harrier release changed the name of extracted folder.
## 11/07/17 - Added logic to extract the data area quotas and used space from global.yaml file in npm_data_manager.
## 12/06/17 - Added logic to check if DPI is disabled and if we need to check for BUG 293099
## 12/16/17 - Added logic to show the Install time for the latest upgrade
## 12/29/17 - Added logic to show weblinks for the output files for easy access
## 01/02/18 - Added logic to catch BUG 289823 - rollup_stats.json
## 01/03/18 - Added logic to catch BUG 294375 - Incorrect storage block settings
## 01/04/18 - Added logic to get the execution time of the script.
## 01/16/18 - Added logic to get ERRORS and WARNINGS from yarder log
## 01/21/18 - Added logic to get the DB Types monitored
## 01/25/18 - Keep a list of all .gz and .logz files in a list to see what you can do with them later
## 02/01/18 - Added logic to check at_api mem usage violations as mentioned in BUG#290431
## 02/05/18 - Added logic to catch Call Traces in /var/log/messages (Not the full traces, just the instance when it happened)
##	      Added logic to exclude files to be parsed by errorsandwarns. Use skipfiles list to exclude/include files
## 02/09/18 - Added logic to readh npm_alerts.db file for alert information but python sqlite3 version is not matching
##	      sqlite3 version with which AR11 is creating the DB.
##
## 02/15/18 - Added logic to catch TDS ASA data being dropped. These messages exists only from INVADER and above.
## 02/20/18 - Added logic to check if NIC is in wrong slot. Check tcstats.txt to see if we have mon0_0
## 03/07/18 - Added logic to get the number of defined applications and also enabled applications
## 04/12/18 - Added more files to skipfiles list to stop processing them
##	      Added logic to catch exception when files are missing - codeversion and layout
## 04/13/18 - Added logic to get hardware and software drops from metric.sqlite DB
## 04/16/18 - Added logic to get the status of the secure vault. This feature is available only for 11.4 and above.
## 05/11/18 - Added logic to get the out-of-sync clock messages in /var/log/messages
####################################################################################################################

####################################################################################################################
                                        ##############TO DO#############

## 07/19/17 - Implement logic to check if the same error occurs more than once and write accoordingly. This is major change.
## 07/20/17 - Found storcli_calls_show.txt. Added same storcli logic but that does not work completely. Find out if this
##            for Gripen or specific models and add logic. Currently calling storcli logic for this file too
## 09/05/17 - If the sysdump name is anything besides what the appliance generated then the script would fail.
##            This is happening because we are constructing the working folder name based on the filename of the dump.
##            If the file is different from the extracted folder name then obviously script does not find the folder
##            and does not read any files.
## 02/15/18 - Need to test logic added on 02/15/18 and 02/01/18 with sysdumps from INVADER or above. For now just verified if the script runs without issues
##	      even after adding the logic to catch the errors for above 2 changes.
###################################################################################################################


import os
import re
import sqlite3
import tarfile
import shutil
import stat
import time
import io
import json

start = time.time()

def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)

##Delete all previously extracted folders
def cleanup(path,filename,systemdetails):

    cwd = os.path.dirname(os.path.abspath(path))
    os.chdir(cwd)

##    print('Deleting folders...')
##    
##    for fdname in os.listdir(cwd):
##        if os.path.isdir(os.path.abspath(fdname)):
##            print('Deleting folder',os.path.abspath(fdname))
##            shutil.rmtree(os.path.abspath(fdname),ignore_errors=False,onerror=del_rw)


    for fname in os.listdir(cwd):
        if (fname.find(filename)!=-1 or fname.find(systemdetails)!=-1):
            print('File already exists...',fname)
            print('Deleting file...',fname)
            os.remove(fname)

##Unzip the diag bundle zip file
####def unzip1(filepath):
####
####    print('Unzipping bundle..')
####    
####    zfile = tarfile.open(filepath)
####    zfile.extractall()
####    zfile.close()
####
####    print('Finished unzipping the bundle...')

##Unzip to same location where the bundle is present
def unzip(filepath):

    extractpath = os.path.dirname(os.path.abspath(filepath))

    print('Unzipping sysdump to... ',os.path.abspath(extractpath))

    filename = os.path.basename(filepath)
##    file_tar,file_tar_ext = os.path.splitext(filepath)
##    file_untar, file_untar_ext = os.path.splitext(file_tar)
##    workdir = os.path.join(os.path.dirname(filepath),filename[filename.index('sysdump'):].split('.')[0])

##    print('PROPER DIR: ',workdir)

    os.chdir(extractpath)

    try:
    	zfile = tarfile.open(filepath)
        zfile.extractall(os.path.abspath(extractpath))
    except Exception as e:
##        pass
        print('Sysdump already unzipped.')

    zfile.close()
    
    print('Finished unzipping the bundle...')
    
    if filename.split('.')[0] in os.listdir(extractpath):
	workdir = os.path.abspath(filename.split('.')[0])
    else:
	if filename[filename.index('sysdump'):].split('.')[0] in os.listdir(extractpath):
		workdir = os.path.join(os.path.dirname(filepath),filename[filename.index('sysdump'):].split('.')[0])

    return workdir


##Use to open a file for any function
def openfile(file):
    print ('Reading file',file+'\n')
    fobj = io.open(file,encoding="utf8")
    return fobj

##Use to close a file for any function
def closefile(fobj):
    fobj.close()

##Connect to metrics database
def dbconnect(logfile):

    if (os.path.exists(logfile)):

        conn = sqlite3.connect(logfile)
        c = conn.cursor()
     
    else:

        print('Database File does not exists..\n')
        conn = ' '
        c = ' '

    return conn,c

##Close database connection
def dbclose(conn):
    conn.close()

##Funcction to get alert details
def alerts(conn,c):
	try:
##		c.execute("SELECT policy_name,count(id) FROM Summary GROUP BY policy_name")
		c.execute('SELECT policy_name,count(id) FROM Summary GROUP BY policy_name UNION SELECT ''Total alerts'',count(id) FROM Summary')
		alertlst  = c.fetchall()

		fwrite.write(systemdetails,'a')
		fwrite.write('***** System Alerts Details *****\n')
	
		for x in alertlst:
			fwrite.write(str(alertlst[x]).strip('()')+'\n')

		fwrite.close()

	except Exception as e:
		print('Unable to connect to db... ')
		print(e)

	return

##Function to get software/hardware drops
def sw_hw_drops(conn,c):
	try:
		c.execute("SELECT datetime(timestamp,'unixepoch','localtime') as datetime, interface,sum(hw_dropped_packets) hw_drops,sum(sw_dropped_packets) sw_drops FROM capture_interface where (hw_dropped_packets!=0 or sw_dropped_packets) group by interface,timestamp order by datetime")
		drplst = c.fetchall()

		for x in drplst:
			print(str(drplst[x]).strip('()')+'\n')

	except Exception as e:
		print(e)


####Function to get cpu data sorted by time
##def cpudata(conn,c):
##
##        c.execute("select datetime(timestamp,'unixepoch','localtime') as datetime, avg(total) as average, avg(idle) as idle from cpu group by datetime(timestamp,'unixepoch') order by datetime(timestamp,'unixepoch')")
##        list = c.fetchall()
##
##        fwrite = open(cpu,'a')
##        fwrite.write('(datetime , total , idle) \n')
##        for x in range(0,len(list)):
##            fwrite.write(str(list[x]).strip('()')+'\n')
##        fwrite.close()
##        
##        return list
##
####Function to get memory data sorted by time
##def memdata(conn,c):
##
##        c.execute("SELECT datetime(timestamp,'unixepoch','localtime') as datetime,memfree,cached,active FROM memory order by datetime(timestamp,'unixepoch')")
##        list = c.fetchall()
##
##        fwrite = open(mem,'a')
##        fwrite.write('(datetime, memfree, cached, active) \n')
##        for x in range(0,len(list)):
##            fwrite.write(str(list[x]).strip('()')+'\n')
##        fwrite.close()
##        
##        return list
##
####Function to get probe data sorted by time
##def probedata(conn,c):
##
##    c.execute("select datetime(timestamp, 'unixepoch', 'localtime') as datetime, tcp_opened_connections_rate, tcp_active_connections_rate, tcp_timeout_connections_rate, tcp_closed_connections_rate, udp_started_flows_rate, udp_active_flows_rate, udp_timeout_flows_rate, tcp_connections_duration, udp_flows_duration, http_response_body_size, http_response_rate, http_request_body_size, http_request_rate, http_dropped_url_objects_rate, ssl_conns, ssl_conns_with_errors, ssl_handshake_success, ssl_bad_certificate, ssl_missing_key, ssl_non_rsa, ssl_session_restored, ssl_session_cache_hit, ssl_session_cache_miss, ssl_session_cache_max_entries, ssl_cert_cache_hit, ssl_cert_cache_miss, ssl_cert_cache_max_entries, ssl_gap_in_conn, packets_received, packets_dropped from probe order by timestamp")
##    list = c.fetchall()
##
##    fwrite = open(probe,'a')
##    fwrite.write('(datetime, tcp_opened_connections_rate, tcp_active_connections_rate, tcp_timeout_connections_rate, tcp_closed_connections_rate, udp_started_flows_rate, udp_active_flows_rate, udp_timeout_flows_rate, tcp_connections_duration, udp_flows_duration, http_response_body_size, http_response_rate, http_request_body_size, http_request_rate, http_dropped_url_objects_rate, ssl_conns, ssl_conns_with_errors, ssl_handshake_success, ssl_bad_certificate, ssl_missing_key, ssl_non_rsa, ssl_session_restored, ssl_session_cache_hit, ssl_session_cache_miss, ssl_session_cache_max_entries, ssl_cert_cache_hit, ssl_cert_cache_miss, ssl_cert_cache_max_entries, ssl_gap_in_conn, packets_received, packets_dropped) \n')
##    for x in range(0,len(list)):
##        fwrite.write(str(list[x]).strip('()')+'\n')
##    fwrite.close()
##        
##    return list

    
#Directory walk of the extracted bundle and build list for config,log,core files
def navigatefolders(workdir):
    
    ##cwd = os.getcwd()
    cwd = os.path.abspath(os.path.dirname(workdir))
    os.chdir(cwd)

    print('Currently working in...' ,cwd)
    
    filelist = []
    configfiles = []
    corefiles = []
    yamlfiles = []
    sqlfiles = []
    jsonfiles = []
    conffiles = []
    gnrlfiles = []
    gzfiles = []
    folderstoread = ['coredumps']
    skipfiles = [
		'copy_log_type.sh.out',
		'ledctl.log',
		'ledmon.log',
		'dbperf_unproc_log.sh.out',
		'storage_monitoring_sysdump.py.out',
		'npm_fiberblaze_sysdump.sh.out',
		'wta_config_sysdump.py.out',
		'policy_manager_copy_policies.sh.out',
		'rsl_core_rest_svc_sysdump.py.out',
		'usernotify_sysdump.py.out',
		'lumberjack_sl6_alloy_sysdump.py.out',
		'alert_manager_copy_alerts.sh.out',
		'npm_capture_sysdump.py.out',
		'npm_napatech_sysdump.sh.out',
		'npm_webui_sysdump.sh.out',
		'probe_sysdump.py.out',
		'db_collection_state_info.py.out',
		'lumberjack_sl6_platform_sysdump.py.out',
		'probe_collection_info.log',
		'rsl_core_rest_svcs_collection_info.log',
		'file_permissions.txt',
		'rpm_versions.txt',
		'imgctrl.log',
		'secure_vault_sysdump.py.out',
		'system_metrics_sysdump.py.out',
		'yum.log'
		]
    
    
    for fdname in os.listdir(cwd):
        if (os.path.isdir(fdname) and os.path.abspath(fdname)== workdir):
            for path,subdirs,files in os.walk(os.path.abspath(fdname)):
                for x in files:
                    if ((x.endswith('.txt')) or (x.find('manage.log')!=-1)):
                        configfiles.append(os.path.join(os.path.abspath(path),x))
                    else:
                        if (x.endswith('.log') or x.endswith('.out')):
                            if(x.find('boot.log')!=-1):
                                filelist.append(os.path.join(os.path.abspath(path),x))
                                configfiles.append(os.path.join(os.path.abspath(path),x))
                            else:
                                filelist.append(os.path.join(os.path.abspath(path),x))
                        else:
                            if (x.endswith('.yaml')):
                                yamlfiles.append(os.path.join(os.path.abspath(path),x))
                            else:
                                if(x.endswith('.sqlite') or x.endswith('.db')):
                                    sqlfiles.append(os.path.join(os.path.abspath(path),x))
                                else:
                                    if(x.endswith('.json')):
                                        jsonfiles.append(os.path.join(os.path.abspath(path),x))
                                    else:
                                        if(x.endswith('.conf')):
                                            conffiles.append(os.path.join(os.path.abspath(path),x))
					else:
					    if((x.find('yarder')!=-1 or x.find('npm_cli')!=-1 or x.find('messages')!=-1)and x.find('.gz')==-1):
						gnrlfiles.append(os.path.join(os.path.abspath(path),x))
					    else:
					    	if (x.find('.gz')!=-1 or x.find('.logz')!=-1):
							gzfiles.append(os.path.join(os.path.abspath(path),x))


    for logfile in yamlfiles:
        if(logfile.find('versions')!=-1 or logfile.find('npm_data_manager')!=-1 or logfile.find('global.yaml')!=-1 or logfile.find('ver-appliance_history.yaml')!=-1):
            yamls(logfile)
    
    for logfile in configfiles:
        #print(logfile)
        configdetails(logfile)

    for logfile in jsonfiles:
        jsonparse(logfile)

    for logfile in conffiles:
        confiles(logfile)

    for logfile in filelist:
        if logfile.find('probe.log')!=-1:
            print('Processing ',logfile)
            probehang(logfile)
            errorsandwarns(logfile)
	else:
	    if logfile.find('npm_capture.log')!=-1:
	    	print('Processing ',logfile)
		npmcpthang(logfile)
		bug291485(logfile,settingsconf)
		bug294375(logfile)
		errorsandwarns(logfile)
	    else:
		if logfile.find('sqldecode')!=-1:
			print('Processing ',logfile)
			dbtypes(logfile)
			errorsandwarns(logfile)
		else:
	            if logfile.find('atserv_api')!=-1:
			print('Processing ',logfile)
			at_api_memusage(logfile)
			errorsandwarns(logfile)
		    else:
			if logfile.find('fsrvcltraf.log')!=-1:
				print('Processing ',logfile)
				tdsasadrops(logfile)
				errorsandwarns(logfile)
			else:
			    if os.path.basename(logfile) in skipfiles:
			    	print('Skipping file... ',logfile)
			    else:
			    	print('Processing ',logfile)
				errorsandwarns(logfile)

    for logfile in gnrlfiles:
	if logfile.find('messages')!=-1:
		outofsync(logfile)
		call_traces(logfile)
		errorsandwarns(logfile)
	else:
		print('Processing ',logfile)
		errorsandwarns(logfile)
##Get list of all core files
    for logfile in configfiles:
        for foldername in folderstoread:
            if foldername in logfile:
                corefiles.append(logfile)


    for logfile in sqlfiles:
	if logfile.find('npm_alerts.db')!=-1:
    		print(logfile)
		conn, c = dbconnect(logfile)
		
		if ((conn != ' ') and (c !=' ')):
			alerts(conn,c)

		dbclose(conn)
		
	else:
		if logfile.find('metrics.sqlite')!=-1:
			print(logfile)
			conn, c = dbconnect(logfile)

		if ((conn != ' ') and (c !=' ')):
			sw_hw_drops(conn,c)

		dbclose(conn)

    coredetails(corefiles)

##    for logfile in sqlfiles:
##        print(logfile)
##        conn, c = dbconnect(logfile)
##
##        if ((conn != ' ') and (c !=' ')):
##            cpudata(conn,c)
##            memdata(conn,c)
##            probedata(conn,c)
##            
##            dbclose(conn)

##Function to catch TDS ASA drops
def tdsasadrops(logfile):
	srchstrngs = ['start dropping tds data','# of tds queuer drops =']
	cnt = []
	try:
		fobj = openfile(logfile)
		fwrite = open(systemdetails,'a')

		for strng in srchstrngs:
			for line in fobj:
				if strng in line:
					cnt.append(line)
			if len(cnt)>0:
				fwrite.write('\n TDS is  droping data \n')
				fwrite.write('Message - '+strng+' Occurred '+str(len(cnt))+' Times \n')
			cnt=[]

	except Exception as e:
		print('Unable to open file... ',logfile)
		print(e)
	
	fobj.close()
	fwrite.close()

	return

##Function to catch Call Traces in messages
def call_traces(logfile):
	srchstr = ('Call Trace:')
	trclst = []
	try:
		fobj = openfile(logfile)
		fwrite = open(filename,'a')
		
		for line in fobj:
			if srchstr in line:
				trclst.append(line)		
		
		if len(trclst)>0:
			fwrite.write('\n'+'******Call Traces in file '+ str(logfile)+'******' + '\n\n')
			for x in trclst:
				fwrite.write(x)

	except Exception as e:
		print('Unable to open file... ',logfile)
		print(e)
	
	fobj.close()
	fwrite.close()

	return trclst

##Function to catch clock out of sync messages
def outofsync(logfile):
	srchstr = ('timestamp clock got Out-of-Sync with reference')
	trclst = []
	try:
		fobj = openfile(logfile)
		fwrite = open(systemdetails,'a')

		for line in fobj:
			if srchstr in line:
				trclst.append(line)

		if len(trclst)>0:
			fwrite.write('\n*****Clock out of sync *****\n')
			fwrite.write('Timestamp clock got Out-of-Sync occurred: '+str(len(trclst))+' times \n')
			fwrite.write('Please look into /var/log/messages file to see clock is out of sync \n')

	except Exception as e:
		print(e)

	fobj.close()
	fwrite.close()

	return trclst

##Function to check memory usage violations for at_api (Bug#290431)
def at_api_memusage(logfile):
	srchstr = ('bytes allocated for this API request exceeds max allowable value')
	cnt = 0
	try:
		fobj = openfile(logfile)
		fwrite = open(systemdetails,'a')
		
		for line in fobj:
			if line in srchstr:
				cnt=cnt+1
		if cnt>0:
			fwrite.write('\n*****ATserv Memory Usage Violations ******\n')
			fwrite.write('atserv api memory usage exceeded 512MB quota - '+ cnt+ ' times \n')
			fwrite.write('For more details please take a look at the below bug \n')
			fwrite.write('https://bugzilla.nbttech.com/show_bug.cgi?id=290431 \n')

	except Exception as e:
		print('Unable to open file... ',logfile)
		print(e)
	
	fobj.close()
	fwrite.close()

	return cnt		

##Function get DB Types from sqldecode.log
def dbtypes(logfile):
	dblist = []
	try:
		fobj = openfile(logfile)
		fwrite = open(systemdetails,'a')
		fwrite.write('\n***** Databases Monitored*****\n')

		for line in fobj:
			if (line.find('DBA-SQL-I-0 New database')!=-1 and line.find('(monitored)')!=-1):
				##tmp = (line[line.index('database'):])
				match = re.findall(r'\[[\ a-zA-Z]*\]',line)          ##matches all DB types excpet DB2 - \[[a-zA-Z][\d2 a-zA-Z]*\]
				ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',line)
				##print(match+ip)
				##dblist.append(re.findall(r'[\d.-]+',tmp))
				if match not in dblist:
					dblist.append(match)

##		print(dblist)
		for db in dblist:
			if len(db)>0:
				fwrite.write(str(db[0])+'\n')
			else:
				fwrite.write('[DB2 DRDA]'+'\n')

		fobj.close()
		fwrite.close()
		
	except Exception as e:
		print('Unable to open file... ',logfile)
		print(e)
	
	return dblist

##Function to check packet broker misconfiguration
def bug291485(logfile,settingsconf):
    lines = ['with timestamps not synced with system clock','with timestamps in the past']
    try:
        fobj = openfile(logfile)
        fwrite = open(systemdetails,'a')
        ctnt = fobj.readlines()

        fobj.close()
        
        for line in lines:
            match = [s for s in ctnt if line in s]
        
        ##print(match)

        if len(match)>0:
            fwrite.write('\n*****BUG 291485***** \n')
	    fwrite.write('Messages with- ' + line + ' - occurred ' + str(len(match))+ ' time(s) \n')
            fwrite.write('Indicates npm_capture may get stuck due to packet broker misconfiguration \n')
            fwrite.write('Confirm with customer if they are using timestamping. Check settings.conf \n')
            fwrite.write('Please take a look at "https://bugzilla.nbttech.com/show_bug.cgi?id=291485" \n')
        
    except UnicodeDecodeError:
        print('Unable to open file... ',logfile)

    try:
        if (len(settingsconf)>0 and settingsconf.find('settings.conf')!=-1):
            fobj = openfile(settingsconf)

            for n in fobj:
                if (n.find('ANUE')!=-1 or n.find('GIGAMON_TRAILER')!=-1):
                    fwrite.write('Found '+ str(n.strip()) + ' in settings.conf file \n')
                    fwrite.write('Change packet_broker configuration to NONE \n')

        fwrite.close()
        
    except UnicodeDecodeError:
        print('Unable to open file... ',settingsconf)


##Function to check storage volume misconfiguration in block size
def bug294375(logfile):
	lines = ['Incorrect file size for storage file']
	try:
		fobj = openfile(logfile)
		fwrite = open(systemdetails,'a')
		ctnt = fobj.readlines()

		fobj.close()

		for line in lines:
			match = [s for s in ctnt if line in s]

		if len(match)>0:
			fwrite.write('\n***** BUG 294375 ***** \n')
			fwrite.write('Messages - ' + line + ' - occurred ' + str(len(match))+ ' time(s) \n')
			fwrite.write('Indicates Storage Unit block size misconfiguration \n')
			fwrite.write('Check if you have npm capture core dumping \n')
			fwrite.write('Please take a look at the bug below for more details and symptoms \n')
			fwrite.write('https://bugzilla.nbttech.com/show_bug.cgi?id=294375 \n')

	except Exception as e:
		print('Unable to open logfile... ',logfile)
	
	return

#Function to check if there is a possible hang in the probe process
def probehang(logfile):
    line = 'Rollups processor: exported 0  basic connections - 0  tcp connections'
    try:
        fobj = openfile(logfile)
        fwrite = open(systemdetails,'a')
        ctnt = fobj.readlines()

        fobj.close()

        match = [s for s in ctnt if line in s]
        
        if len(match)>0:
            fwrite.write('\n***** Probe hangs ***** \n')
            if len(match)<20:
                fwrite.write(line + ' occured ' + str(len(match))+ ' times (probably OK) \n')
            else:
                fwrite.write(line + ' occured ' + str(len(match))+ ' times \n')

            fwrite.write('Indicates worker queues maxing out. Might cause probe hangs. \n')
            fwrite.write('Please take look into probe.log for more details. \n \n')
	    
	    fwrite.write('Take a look the article to see if you are running the issue mentioned here... \n')
	    fwrite.write('https://supportkb.riverbed.com/support/index?page=content&id=S31640 \n')
	
        fwrite.close()
            
    except UnicodeDecodeError:
        print('Unable to open file... ',logfile)


##Function to check if there is a possible issue with npm capture dropping traffic because of buffrer overflows
def npmcpthang(logfile):
	line = 'Pool default_write_pool has 1 free slabs'
	try:
	    fobj = openfile(logfile)
	    fwrite = open(systemdetails,'a')
	    ctnt = fobj.readlines()
	    
	    fobj.close()
	    
	    match = [s for s in ctnt if line in s]
	    
 	    if len(match)>0:
		fwrite.write('\n***** npm capture hang and packets dropped ***** \n')
		if len(match)<20:
                    fwrite.write(line + ' event occured ' + str(len(match))+ ' time(s) (probably OK) \n')
                else:
                    fwrite.write(line + ' event occured ' + str(len(match))+ ' time(s) \n')
                    
		fwrite.write('Indicates that no buffering is available in npm_capture and packets might be dropped \n')
		fwrite.write('Please check capture_slabpool table in the system metrics database to see if there are no gaps \nfor long period of time. \n')
	   
	    fwrite.close()

	except UnicodeDecodeError:
		print('Unable to open file... ',logfile)


##Function to write core file count and list to systemdetails file
def coredetails(cdmpfiles):
    dict = {}
    fwrite = open(systemdetails,'a')
    fwrite.write('\n***** Core Files summary ***** \n')    

    cdmpcnt = len(cdmpfiles)
    fwrite.write('Total Number of cores: '+str(cdmpcnt)+'\n')
    fwrite.write('--For backtrace on latest core file(s) please look in errorsandwarns.txt \n')

## Use this call to write list of all corefiles in the systemdetails
##    for logfile in cdmpfiles:
##        fwrite.write('\n')
##        fwrite.write(logfile[logfile.index('coredump'):])

    if cdmpcnt!=0:
        cdmpfiles.sort()
            
        for s in cdmpfiles:
            if s.find('backtrace')!=-1:
                filelocidx = re.search('coredumps',s).start()
                fileloc = s[:filelocidx]
                
                tmp = s[s.index('coredump'):]
                pos = re.search("\d",tmp).start()
                
                k = tmp[:pos-1]
                v = tmp[pos:]

                dict.update({k:v})
         
        for key,value in dict.items():
            fwrite.write('\n')
            fwrite.write(key+'-'+value)
            backtraceltst(os.path.abspath(fileloc+key+'-'+value))

    fwrite.close()

##Write first 100 lines backtrace from latest core file
def backtraceltst(crdmpltst):
    n = 100
    fobj = openfile(crdmpltst)

    fwrite = open(filename,'a')

    fwrite.write('\n***** backtrace details ***** \n')
    fwrite.write(crdmpltst)
    fwrite.write('\n')

    for i in range(1,n):
        line = fobj.readline()
        if line.startswith('[New') == False:
            fwrite.write(line)
        
    fwrite.close()
    closefile(fobj)
    
##Function to search for all Errors and Warnings in log files
def errorsandwarns(logfile):

    searchstrings = ['SEVERE','ERROR','WARN','FATAL','DBA-DBW-E','DBA-PCX-E','DBA-SQL-E','DBA-DSP-E','DBA-ATS-E']
    ##'DBA-DBW-W','DBA-PCX-W','DBA-SQL-W','DBA-DSP-W','DBA-ATS-W' - Warnings for ASX, add if needed

    try:
        fobj = open(logfile)
        fwrite = open(filename,'a')
        fwrite.write('\n'+'******Errors and Warnings in file '+ str(logfile)+'******' + '\n\n')

        try:
            for i in fobj:
                for string in searchstrings:
                    if string in i.strip():
                        fwrite.write(i)

            fobj.close()
            fwrite.close()

        except UnicodeDecodeError:
            print('Skipping ',logfile)
            
    ##except FileNotFoundError:
        ##print(logfile,'File does not exist...\n')

    except Exception as e:
	print('Unable to open file... ',str(e))
	print('\n')

##Functions to get configuration and other details
def netstat(logfile):
    fobj = openfile(logfile)

    fwrite = open(systemdetails,'a')
    fwrite.write('\n***** Netstat Output summary ***** \n')
    
    TIME_WAIT = 0
    CLOSE_WAIT = 0
    FIN_WAIT = 0

    for x in fobj:
        if re.search('TIME_WAIT',x.strip()):
            TIME_WAIT = TIME_WAIT+1
        else:
            if re.search('CLOSE_WAIT',x.strip()):
                CLOSE_WAIT = CLOSE_WAIT+1
            else:
                if re.search('FIN_WAIT',x.strip()):
                    FIN_WAIT = FIN_WAIT+1
                    
    fwrite.write('TIME_WAITs :'+str(TIME_WAIT)+'\n')
    fwrite.write('CLOSE_WAITs :'+str(CLOSE_WAIT)+'\n')
    fwrite.write('FIN_WAITs :'+str(FIN_WAIT)+'\n')

    fwrite.close()
    
    return

def top(logfile):
    fobj = openfile(logfile)
    n = 14

    fwrite = open(systemdetails,'a')
    fwrite.write('\n***** Top Command summary ***** \n')
    
    for i in range(1,n):
        line = fobj.readline()
        fwrite.write(line)

    fwrite.close()
    closefile(fobj)

    return

def uname(logfile):
    fobj = openfile(logfile)

    fwrite = open(systemdetails,'a')
    fwrite.write('\n***** uname details ***** \n')
    
    for i in fobj:
        fwrite.write(i[:i.index('#')])
    fwrite.write('\n')

    fwrite.close()
    closefile(fobj)

    return

def df(logfile):
    fobj = openfile(logfile)

    fwrite = open(systemdetails,'a')
    fwrite.write('\n***** Disk Usage details ***** \n')

    for i in fobj:
        if(i.find('Filesystem')== -1):
            fwrite.write(i)    
    
    fwrite.write('\n***** Data Areas Usage *****\n')
    fwrite.write('NOT OK is displayed when Used space exceeds allocated Quota\n')
    fwrite.write('(If the violation is less than 100MB it can probably be ignored)\n\n')
    for key,value in finaldata.items():
	if (int(value[0])-int(value[1]))<0:
		fwrite.write('- '+key+'(NOT OK)'+'\n')
	else:
		fwrite.write('- '+key+'(OK)'+'\n')
	fwrite.write('Quota(mb):'+str(value[0])+'\n')
	fwrite.write('Used(mb):'+str(value[1])+'\n')
	##fwrite.write(str(int(value[0])-int(value[1]))+'\n')


    fwrite.close()
    closefile(fobj)

    return

def ifconfig(logfile):
    fobj = openfile(logfile)

    fwrite = open(systemdetails,'a')
    fwrite.write('\n****** ifconfig details *****\n')
    
    for i in fobj:
        if (i.find('inet addr:')!=-1 and i.find('Bcast:')!=-1):
            fwrite.write('IP Address '+i[i.index(':'):i.index('Bcast')]+'\n')

    fwrite.close()
    closefile(fobj)

    return

def supervisorstatus(logfile):
    fobj = openfile(logfile)

    fwrite = open(systemdetails,'a')
    fwrite.write('\n****** sysctl status *****\n')

    for i in fobj:
        fwrite.write(i)

    fwrite.close()
    closefile(fobj)

def sysinfo(logfile):
    fobj = openfile(logfile)

    fwrite = open(systemdetails,'a')
    fwrite.write('\n****** System Info *****\n')

    for i in fobj:
        if((i.strip().find('Serial Number:')!=-1) or (i.strip().find('Product Name:')!=-1)or (i.strip().find('UUID:')!=-1)):
            fwrite.write(i.strip()+'\n')
    
    fwrite.write(version+'\n')
    ##fwrite.write('Timezone: '+str(timezone)+'\n')
    fwrite.write('Upgrade Time: '+str(updatetime)+'\n')

    fwrite.close()
    closefile(fobj)            

def storcli(logfile):
    searchstring = 'PD LIST :\n'
    fobj = openfile(logfile)

    fwrite = open(systemdetails,'a')
    fwrite.write('\n****** Drives status *****\n')

    fwrite.write(str(layout)+'\n')
    
    for i in fobj:
        if i.find('Physical Drives')!=-1:
            fwrite.write(i)

    fo = openfile(logfile)
    lines = fo.readlines()

    if searchstring in lines:
        lines = lines[lines.index(searchstring)+3:]

        for x in lines:
            fwrite.write(x)
    else:
        fwrite.write('No Physical Drives \n')
    
    fwrite.close()
    closefile(fobj)
    closefile(fo)

##Function to get the timezone of the appliance
def timezone(logfile):
	global timezone
	fobj = openfile(logfile)
	fwrite = open(systemdetails,'a')
	
	timezone = fobj.readlines()
		
	if len(timezone)>0:
		timezone = timezone[0]
	else:
		timezone = ('Unable to pull this detail for this release...')	
	
	fwrite.write('\nTimezone: '+timezone+'\n')
	
	fobj.close()
	fwrite.close()

	return timezone

##Function to check if NIC is in the wrongslot
def tcstats(logfile):
	try:
		fobj = openfile(logfile)
		fwrite = open(systemdetails,'a')
		
		NIC  = fobj.readlines()

		if 'mon0_0' in NIC:
			fwrite.write('\n***** NIC in wrong location *****\n')
			fwrite.write('A NIC in the wrong slot(mon0_0). No card should occupy mon0_0.\n')
			fwrite.write('Check tcstats file for more details... \n')
		
		fobj.close()
		fwrite.close()

	except Exception as e:
		print(e)

	return

##Function to check the status of the secure vault
def secure_vault_status(logfile):
	try:
		fobj = openfile(logfile)
		fwrite = open(systemdetails,'a')

		status = fobj.readlines()
		
		fwrite.write('\n***** Secure Vault Status *****\n')
		if str(status).find('active')!=-1:
			fwrite.write('Secure Vault is active \n')
		elif str(status).find('locked')!=-1:
			fwrite.write('Secure Vault is locked \n')
			fwrite.write('Indicates MAC was changed, or other errors \n')
			fwrite.write('Check boot/messages logs for errors \n')

		fobj.close()
		fwrite.close()

	except Exception as e:
		print(e)


	
#Function to get the version of the code
def codeversion(logfile):
	try:

    		global version
    		fobj = openfile(logfile)
    
    		for i in fobj:
        		if i.find('version:')!=-1:
            			version = i.strip()
    
    		closefile(fobj)

	except Exception as e:
		print(e)

	return version

#Function to get the Storage layout
def layout(logfile):
	try:
		global layout
		fobj = openfile(logfile)

		for i in fobj:
			if i.find('layout:')!=-1:
            			layout = i.strip()

    		closefile(fobj)

	except Exception as e:
		print(e)
    
	return layout

##Function to get the space usage for data areas
def dataarea(logfile):
	arr = ['']*3	
	global finaldata
	finaldata = {}

	try:
		fobj = openfile(logfile)
	
		for line in fobj:
			if line.find('data_module_name:')!=-1:
				arr[0] = line.split(':')[1].strip()
			if line.find('quota_size_mb')!=-1:
				arr[1] = line.split(':')[1].strip()
			if line.find('used_space_mb')!=-1:
				arr[2] = line.split(':')[1].strip()
		
			if (arr[0]!='' and arr[1]!='' and arr[2]!=''):
				##print(str(arr[0])+'-'+str(arr[1])+'-'+str(arr[2]))
				if arr[0] not in finaldata:
					finaldata.update({arr[0]:[arr[1],arr[2]]})
					arr = ['']*3
##		print(finaldata)
##		for key,value in finaldata.items():
##			print(key)
##			print('Quota- ',str(value[0]))
##			print('Used- ',str(value[1]))
	except Exception as e:
		print('Unable to open file.... ',logfile)
	
	closefile(fobj)
	
	return finaldata

##Function to get the latest upgrade time stamp
def upgrdtme(logfile):
	global updatetime
	fobj = openfile(logfile)
	lines = fobj.readlines()

	tmp = lines[-5:]

	for n in tmp:
		if n.find('install_time_str:')!=-1:
			updatetime = n.replace('install_time_str:','')
	return updatetime

##Function to get details from yaml version files
def yamls(logfile):
    if (logfile.find('ver-appliance.yaml')!=-1):
        codeversion(logfile)
    elif (logfile.find('layout.yaml')!=-1):
        layout(logfile)
    elif (logfile.find('global.yaml')!=-1):
	dataarea(logfile)
    elif(logfile.find('ver-appliance_history.yaml')!=-1):
	upgrdtme(logfile)
    
##Function to get history of dbperf module enabling/disabling - Gripen onwards
def dbperfhis(logfile):
    fobj = openfile(logfile)
    lines = fobj.readlines()

    fwrite = open(systemdetails,'a')
    fwrite.write('\n***** DB Module history *****\n')

    tmp = lines[-5:]

    for n in tmp:
        fwrite.write(n)

    fwrite.close()
    closefile(fobj)
    

##Function to get feature status - licensed and enabled features - Gripen onwards
def featurestatus(logfile):
    fobj = openfile(logfile)

    fwrite = open(systemdetails,'a')
    fwrite.write('\n***** Feature Status *****\n')

    for i in fobj:
        if(i.find('True')!=-1 or i.find('licensed')!=-1):
            fwrite.write(i)
    
    fwrite.write('\n')
    fwrite.close()
    closefile(fobj)

##Function to get the approximate last reboot of the system
def lastreb(logfile):
    fobj = openfile(logfile)

    fwrite = open(systemdetails,'a')
    fwrite.write('\n***** Approximate reboot time *****\n')

    reboottime = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(os.path.getmtime(logfile)))
    ##reboottime = str(os.path.getmtime(logfile))
    fwrite.write(reboottime+'\n')

    fwrite.close()
    closefile(fobj)

##Function to get the count of hostgroups
def hostgroups(logfile):
        x = 0
        fobj = openfile(logfile)

        fwrite = open(systemdetails,'a')
        fwrite.write('\n***** Number of hostgroups *****\n')

        for n in fobj:
            if(n.find('"id"')!=-1):
                x = x+1
        fwrite.write(str(x)+'\n')

        fwrite.close()
        closefile(fobj)

##Function to get the count of defined apps
def definedapps(logfile):
	try:
		config = json.load(open(logfile))
		num_enabled_apps = 0

		fwrite = open(systemdetails,'a')

		for apprule in config["items"]:
			if apprule["enabled"] is True:
				num_enabled_apps+= 1

		fwrite.write('\n**** Total number of defined apps *****\n')
		fwrite.write(str(len(config["items"]))+'\n')

		fwrite.write('\n***** Total number of enabled apps ***** \n')
		fwrite.write(str(num_enabled_apps)+'\n')

		fwrite.close()
		return
	except Exception as e:
		print('Exception reading file... ',logfile)
		print(e)

##Function to check if filters are blocked
def filterblocks(logfile):
	try:
		fobj = openfile(logfile)
		fwrite = open(systemdetails,'a')
		line = fobj.readlines()
	

		tmp = line[-1:]
		ctr = str(tmp[0]).replace('"','',)
		ctr = ctr[ctr.index('shm_error:'):]
		ctr = ctr.split(':')
		ctr = int(str(ctr[1]).replace('}',''))
##	print(ctr)
		if ctr>0:
			fwrite.write('\n***** BUG 289823 ***** \n')
			fwrite.write('shm_error counter in rollups_stats.json file is greater than 0 for last minute of the bundle.')
			fwrite.write('\nPlease take a look at below bug for all symptoms and check if your case matches them.')
			fwrite.write('\n"https://bugzilla.nbttech.com/show_bug.cgi?id=289823" \n')
			fwrite.write('\nSnippet from json file: \n')
			fwrite.write(tmp[0]+'\n')	
	
	except Exception as e:
		print('Unable to open file....',logfile)
	
	closefile(fobj)
	fwrite.close()

	return

##Function to check existence of slab settings file
def bug288879(logfile):
    fobj  = openfile(logfile)

    fwrite = open(systemdetails,'a')
    fwrite.write('\n********BUG 288879********\n')
    fwrite.write('Please take a look at "https://bugzilla.nbttech.com/show_bug.cgi?id=288879"')
    fwrite.write('\nIf the system has been upgraded from Eagle+ to later release the appliance will hit this bug.')
    fwrite.write('\nThe file is slab_pool.conf and is not needed in Gripen and higher versions. \n')
    fwrite.write('\nThe file is located at - '+logfile+'\n')

    fwrite.close()
    closefile(fobj)

##Function to check if Deep Packet Inspection is disabled
def dpi(logfile):
	fobj = openfile(logfile)
	fwrite = open(systemdetails,'a')

	for x in fobj:
		if (x.find('dpi_enabled')!=-1):
			enb = x.split(':')[1]
			enb = enb.replace(',', '')
			if (enb.upper() == 'FALSE'):
				fwrite.write('\n***** BUG 293099 ***** \n')
				fwrite.write('DPI should not be disabled unless customer does not need this feature \n')
				fwrite.write('The bug should list narrower change and upgrade version to fix the bug \n')
				fwrite.write('Please check https://bugzilla.nbttech.com/show_bug.cgi?id=293099 \n \n')
	
	closefile(fobj)
	fwrite.close()		

##Function to parse JSON file
def jsonparse(logfile):
    if(logfile.find('hostgroup-settings.json')!=-1):
        hostgroups(logfile)
    if(logfile.find('rollups_stats.json')!=-1):
	filterblocks(logfile)
    if(logfile.find('app_rule-settings.json')!=-1):
	definedapps(logfile)


##Function to go through all .conf files
def confiles(logfile):
    global settingsconf
    
    if (logfile.find('slab_pool.conf')!=-1):
        bug288879(logfile)
    if(logfile.find('settings.conf')!=-1):
        settingsconf = logfile
    if(logfile.find('probe.conf')!=-1):
	dpi(logfile)

    return settingsconf

##Function to change permissions
def changeperm(fldrnm):
	print('Changing permissions on folder and files in...',fldrnm)
	try:
		for root,dirs,files in os.walk(fldrnm):
			for d in dirs:
				os.chmod(os.path.join(root,d),0o755)
			for f in files:
				os.chmod(os.path.join(root,f),0o755)
	except OSError as e:
		print('Cannot change permissions...different user unzipped the file',e)
	return

##Function to generate weblinks for output files
def weblinks(path,filename,systemdetails):	
	baseURL = 'http://support.nbttech.com/'
	sysURL = ''
	errURL = ''

	tmpPath = str(os.path.dirname(path))[str(os.path.dirname(path)).index('data/'):]
	
	sysURL = baseURL+tmpPath+'/'+systemdetails
	errURL = baseURL+tmpPath+'/'+filename
	logURL = baseURL+tmpPath	

	print('Creating Web Link to files...\n')
	print('***********************************\n')
	print('           WEB LINKS               \n')
	
	print('Browse Logs: '+logURL+'\n')
	print('Systemdetails: '+sysURL+'\n')
	print('Errors Log: '+errURL+'\n')
	
	print('\n***********************************\n')

##Function to get configuration and other system details
def configdetails(logfile):
    
    if (logfile.find('netstat.txt')!=-1):
        netstat(logfile)
    else:
        if (logfile.find('top.txt')!=-1):
            top(logfile)
        else:
            if (logfile.find('uname.txt')!=-1):
                uname(logfile)
            else:
                if (logfile.find('df.txt')!=-1):
                    df(logfile)
                else:
                    if (logfile.find('ifconfig.txt')!=-1):
                        ifconfig(logfile)
                    else:
                        if (logfile.find('supervisorctl_status.txt')!=-1):
                            supervisorstatus(logfile)
                        else:
                            if (logfile.find('bios_serial_number.txt')!=-1):
                                sysinfo(logfile)
                            else:
                                if(logfile.find('storcli.txt')!=-1):
                                    storcli(logfile)
                                else:
                                    if(logfile.find('feature_status.txt')!=-1):
                                        featurestatus(logfile)
                                    else:
                                        if(logfile.find('storcli_call_show.txt')!=-1):
                                            storcli(logfile)
                                        else:
                                            if(logfile.find('manage.log')!=-1):
                                               dbperfhis(logfile)
                                            else:
                                                if(logfile.find('boot.log')!=-1):
                                                    lastreb(logfile)
						else:
						    if(logfile.find('timezone.txt')!=-1):
							timezone(logfile)
						    else:
							if(logfile.find('tcstats.txt')!=-1):
								tcstats(logfile)
							else:
							    if(logfile.find('secure_vault_rest_state.txt')!=-1):
								secure_vault_status(logfile)
##Function to move files to location where the bundle is present
####def movefiles(path):
####    cwd = os.getcwd()
####    dst = os.path.abspath(os.path.dirname(path))
####    
####    for file in os.listdir(os.getcwd()):
####        filelist = (os.path.join(os.path.abspath(file),dst))
####        if ((file.endswith('.txt') or file.endswith('.dat')) and (file.find('probe')!=-1 or file.find('mem')!=-1 or file.find('cpu')!=-1 or file.find('errorsandwarns')!=-1 or file.find('systemdetails')!=-1)):
####            try:
####                print('Moving '+os.path.abspath(file)+' to '+dst)
####                shutil.move(os.path.abspath(file),dst)
####            except IOError:
####                 print(file+' already exists...Removing file')
####                 os.remove(os.path.join(dst,file))
####                 shutil.move(os.path.abspath(file),dst)

                
##Main function
def main():
    global filename
    global systemdetails
    global cpu
    global mem
    global probe
    global settingsconf
        
    print('Enter the full path to sysdump :')
    path = raw_input()

    while True:
        print('Enter valid case number :')
        casenum = raw_input()

        if casenum.isdigit():
            break

    filename = str(casenum)+'_'+'errorsandwarns.txt'
    systemdetails = str(casenum)+'_'+'systemdetails.txt'
    settingsconf = ''
##    cpu = str(casenum)+'_'+'cpu.dat'
##    mem = str(casenum)+'_'+'mem.dat'
##    probe = str(casenum)+'_'+'probe.dat'
    cleanup(path,filename,systemdetails)
    workdir = unzip(path)
    navigatefolders(workdir)
    changeperm(workdir)
    weblinks(path,filename,systemdetails)        
##    movefiles(path)
##    cleanup()
    end = time.time()
    print('Took '+str(end-start)+'s'+' for the script to finish.... ')        
main()
