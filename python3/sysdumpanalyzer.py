####################################################################################################################
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
## 09/06/17 - Tested placing the script in same location as sysdump and it does not change how the script runs nor does delete
##            anything unnecessarily
## 09/06/17 - Added logic to get the storage layout information
####################################################################################################################

####################################################################################################################
                                        ##############TO DO#############

## 07/19/17 - Implement logic to check if the same error occurs more than once and write accoordingly. This is major change.
## 07/20/17 - Found storcli_calls_show.txt. Added same storcli logic but that does not work completely. Find out if this
##            for Gripen or specific models and add logic. Currently calling storcli logic for this file too
## 08/09/17 - Timezone of the system. Need logic to get the timezone where the system is deployed
## 08/21/17 - Test on Linux and python 2.6. Test placing the script in same folder as sysdumps
## 09/05/17 - If the sysdump name is anything besides what the appliance generated then the script would fail.
##            This is happening because we are constructing the working folder name based on the filename of the dump.
##            If the file is different from the extracted folder name then obviously script does not find the folder
##            and does not read any files.
####################################################################################################################

import os
import re
import sqlite3
import tarfile
import shutil
import stat
import time

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

##Unzip to same location where the bundle is present - TEST WORK IN PROGRESS
def unzip(filepath):

    extractpath = os.path.dirname(os.path.abspath(filepath))

    print('Unzipping sysdump to... ',os.path.abspath(extractpath))

    filename = os.path.basename(filepath)
##    file_tar,file_tar_ext = os.path.splitext(filepath)
##    file_untar, file_untar_ext = os.path.splitext(file_tar)
    workdir = os.path.join(os.path.dirname(filepath),filename[filename.index('sysdump'):].split('.')[0])

##    print('PROPER DIR: ',workdir)

    os.chdir(extractpath)

    try:
        zfile = tarfile.open(filepath)
        zfile.extractall(os.path.abspath(extractpath))
    except PermissionError:
        pass
##        print('Sysdump already unzipped.')

    zfile.close()
    
    print('Finished unzipping the bundle...')

    return workdir


##Use to open a file for any function
def openfile(file):
    print ('Reading file',file+'\n')
    fobj = open(file,encoding="utf8")
    return fobj

##Use to close a file for any function
def closefile(fobj):
    fobj.close()

##Connect to metrics database
def dbconnect(logfile):

    if (os.path.exists(logfile)):

        print('Connection to db succeeded...')
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
    
    filelist = []
    configfiles = []
    corefiles = []
    yamlfiles = []
    sqlfiles = []
    jsonfiles = []
    conffiles = []
    folderstoread = ['coredumps']
    
    
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
                                if(x.endswith('.sqlite')):
                                    sqlfiles.append(os.path.join(os.path.abspath(path),x))
                                else:
                                    if(x.endswith('.json')):
                                        jsonfiles.append(os.path.join(os.path.abspath(path),x))
                                    else:
                                        if(x.endswith('.conf')):
                                            conffiles.append(os.path.join(os.path.abspath(path),x))

    for logfile in filelist:
        print('Processing ',logfile)
        errorsandwarns(logfile)

    for logfile in yamlfiles:
        if(logfile.find('versions')!=-1 or logfile.find('npm_data_manager')!=-1):
            yamls(logfile)
    
    for logfile in configfiles:
        #print(logfile)
        configdetails(logfile)

    for logfile in jsonfiles:
        jsonparse(logfile)

    for logfile in conffiles:
        confiles(logfile)

##Get list of all core files
    for logfile in configfiles:
        for foldername in folderstoread:
            if foldername in logfile:
                corefiles.append(logfile)

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
            
    except FileNotFoundError:
        print(logfile,'File does not exist...\n')

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

#Function to get the version of the code
def codeversion(logfile):
    global version
    fobj = openfile(logfile)
    
    for i in fobj:
        if i.find('version:')!=-1:
            version = i.strip()
            
    return version

#Function to get the Storage layout
def layout(logfile):
    global layout
    fobj = openfile(logfile)

    for i in fobj:
        if i.find('layout:')!=-1:
            layout = i.strip()

    return layout

    
##Function to get details from yaml version files
def yamls(logfile):
    if (logfile.find('ver-appliance.yaml')!=-1):
        codeversion(logfile)
    elif (logfile.find('layout.yaml')!=-1):
        layout(logfile)

    
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

##Function to check existence of slab settings file
def bug288879(logfile):
    fobj  = openfile(logfile)

    fwrite = open(systemdetails,'a')
    fwrite.write('\n********BUG 288879********\n')
    fwrite.write('\n Please take a look at "https://bugzilla.nbttech.com/show_bug.cgi?id=288879"')
    fwrite.write('\n If the system has been upgraded from Eagle+ to later release the appliance will hit this bug.')
    fwrite.write('\n The file is slab_pool.conf and is not needed in Gripen and higher versions. \n')
    fwrite.write('\n The file is located at - '+logfile+'\n')

    fwrite.close()
    closefile(fobj)


##Function to parse JSON file
def jsonparse(logfile):
    if(logfile.find('hostgroup-settings.json')!=-1):
        hostgroups(logfile)

##Function to go through all .conf files
def confiles(logfile):
    if (logfile.find('slab_pool.conf')!=-1):
        bug288879(logfile)

        
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
    
    print('Enter the full path to sysdump :')
    path = input()

    while True:
        print('Enter valid case number :')
        casenum = input()

        if casenum.isdigit():
            break

    filename = str(casenum)+'_'+'errorsandwarns.txt'
    systemdetails = str(casenum)+'_'+'systemdetails.txt'
##    cpu = str(casenum)+'_'+'cpu.dat'
##    mem = str(casenum)+'_'+'mem.dat'
##    probe = str(casenum)+'_'+'probe.dat'
    cleanup(path,filename,systemdetails)
    workdir = unzip(path)
    navigatefolders(workdir)
        
##    movefiles(path)
##    cleanup()
    
main()
