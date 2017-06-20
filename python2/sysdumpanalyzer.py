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
####################################################################################################################

import os
import re
import sqlite3
import tarfile
import shutil
import stat

def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)

##Delete all previously extracted folders
def cleanup():

    cwd = os.getcwd()

    print('Deleting folders...')
    
    for fdname in os.listdir(cwd):
        if os.path.isdir(os.path.abspath(fdname)):
            print('Deleting folder',os.path.abspath(fdname))
            shutil.rmtree(os.path.abspath(fdname),ignore_errors=False,onerror=del_rw)


    for fname in os.listdir(cwd):
        if fname.endswith('.txt') or fname.endswith('.dat'):
            os.remove(fname)

##Unzip the diag bundle zip file
def unzip(filepath):

    print('Unzipping bundle..')
    
    zfile = tarfile.open(filepath)
    zfile.extractall()
    zfile.close()

    print('Finished unzipping the bundle...')

##Use to open a file for any function
def openfile(file):
    print ('Reading file',file+'\n')
    fobj = open(file)
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

##Function to get cpu data sorted by time
def cpudata(conn,c):

        c.execute("select datetime(timestamp,'unixepoch','localtime') as datetime, avg(total) as average, avg(idle) as idle from cpu group by datetime(timestamp,'unixepoch') order by datetime(timestamp,'unixepoch')")
        list = c.fetchall()

        fwrite = open(cpu,'a')
        fwrite.write('(datetime , total , idle) \n')
        for x in range(0,len(list)):
            fwrite.write(str(list[x]).strip('()')+'\n')
        fwrite.close()
        
        return list

##Function to get memory data sorted by time
def memdata(conn,c):

        c.execute("SELECT datetime(timestamp,'unixepoch','localtime') as datetime,memfree,cached,active FROM memory order by datetime(timestamp,'unixepoch')")
        list = c.fetchall()

        fwrite = open(mem,'a')
        fwrite.write('(datetime, memfree, cached, active) \n')
        for x in range(0,len(list)):
            fwrite.write(str(list[x]).strip('()')+'\n')
        fwrite.close()
        
        return list

##Function to get probe data sorted by time
def probedata(conn,c):

    c.execute("select datetime(timestamp, 'unixepoch', 'localtime') as datetime, tcp_opened_connections_rate, tcp_active_connections_rate, tcp_timeout_connections_rate, tcp_closed_connections_rate, udp_started_flows_rate, udp_active_flows_rate, udp_timeout_flows_rate, tcp_connections_duration, udp_flows_duration, http_response_body_size, http_response_rate, http_request_body_size, http_request_rate, http_dropped_url_objects_rate, ssl_conns, ssl_conns_with_errors, ssl_handshake_success, ssl_bad_certificate, ssl_missing_key, ssl_non_rsa, ssl_session_restored, ssl_session_cache_hit, ssl_session_cache_miss, ssl_session_cache_max_entries, ssl_cert_cache_hit, ssl_cert_cache_miss, ssl_cert_cache_max_entries, ssl_gap_in_conn, packets_received, packets_dropped from probe order by timestamp")
    list = c.fetchall()

    fwrite = open(probe,'a')
    fwrite.write('(datetime, tcp_opened_connections_rate, tcp_active_connections_rate, tcp_timeout_connections_rate, tcp_closed_connections_rate, udp_started_flows_rate, udp_active_flows_rate, udp_timeout_flows_rate, tcp_connections_duration, udp_flows_duration, http_response_body_size, http_response_rate, http_request_body_size, http_request_rate, http_dropped_url_objects_rate, ssl_conns, ssl_conns_with_errors, ssl_handshake_success, ssl_bad_certificate, ssl_missing_key, ssl_non_rsa, ssl_session_restored, ssl_session_cache_hit, ssl_session_cache_miss, ssl_session_cache_max_entries, ssl_cert_cache_hit, ssl_cert_cache_miss, ssl_cert_cache_max_entries, ssl_gap_in_conn, packets_received, packets_dropped) \n')
    for x in range(0,len(list)):
        fwrite.write(str(list[x]).strip('()')+'\n')
    fwrite.close()
        
    return list

    
#Directory walk of the extracted bundle and build list for config,log,core files
def navigatefolders():
    
    cwd = os.getcwd()
    filelist = []
    configfiles = []
    corefiles = []
    yamlfiles = []
    sqlfiles = []
    jsonfiles = []
    conffiles = []
    folderstoread = ['coredumps']
    
    
    for fdname in os.listdir(cwd):
        if os.path.isdir(fdname):
            for path,subdirs,files in os.walk(os.path.abspath(fdname)):
                for x in files:
                    if ((x.endswith('.txt')) or (x.find('manage.log')!=-1)):
                        configfiles.append(os.path.join(os.path.abspath(path),x))
                    else:
                        if (x.endswith('.log') or x.endswith('.out')):
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
        if logfile.find('versions')!=-1:
            yamls(logfile)
    
    for logfile in configfiles:
        #print(logfile)
        configdetails(logfile)

##Get list of all core files
    for logfile in configfiles:
        for foldername in folderstoread:
            if foldername in logfile:
                corefiles.append(logfile)

    coredetails(corefiles)

    for logfile in sqlfiles:
        print(logfile)
        conn, c = dbconnect(logfile)

        if ((conn != ' ') and (c !=' ')):
            cpudata(conn,c)
            memdata(conn,c)
            probedata(conn,c)
            
            dbclose(conn)

##Function to write core file count and list to systemdetails file
def coredetails(cdmpfiles):
    fwrite = open(systemdetails,'a')
    fwrite.write('\n***** Core Files summary ***** \n')    

    cdmpcnt = len(cdmpfiles)
    fwrite.write('Total Number of cores: '+str(cdmpcnt)+'\n')
    fwrite.write('--For backtrace on latest core file please look in errorsandwarns.txt \n')

    for logfile in cdmpfiles:
        fwrite.write('\n')
        fwrite.write(logfile[logfile.index('coredump'):])
    
    fwrite.close()

    if len(cdmpfiles)!= 0:
        cdmpfiles.sort()
        crdmpltst = cdmpfiles[-1]

        backtraceltst(crdmpltst)


##Write first 70 lines backtrace from latest core file
def backtraceltst(crdmpltst):
    n = 100
    fobj = openfile(crdmpltst)

    fwrite = open(filename,'a')

    fwrite.write('\n***** backtrace details ***** \n')
    fwrite.write(crdmpltst)
    fwrite.write('\n')

    for i in range(1,n):
        line = fobj.readline()
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

def codeversion(logfile):
    global version
    fobj = openfile(logfile)
    
    for i in fobj:
        if i.find('version:')!=-1:
            version = i.strip()
            
    return version
    
##Function to get details from yaml version files
def yamls(logfile):
    if (logfile.find('ver-appliance.yaml')!=-1):
        codeversion(logfile)

##Function to check if dbperf module is enabled or disabled - Gripen or later
def dbperfen(logfile):
    fobj = openfile(logfile)
    lines = fobj.readlines()

    fwrite = open(systemdetails,'a')
    fwrite.write('\n***** DB Module *****\n')
    
    tmp = str(lines[-1])
    
    if tmp.find('enable'):
        fwrite.write('Is dbperf module enabled : True \n')
        fwrite.write(tmp+'\n')
    else:
        fwrite.write('Is dbperf module enabled : False \n')
        fwrite.write(tmp+'\n')

    fwrite.close()
    closefile(fobj)

    
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
                                    if(logfile.find('manage.log')!=-1):
                                        dbperfen(logfile)

##Function to move files to location where the bundle is present
def movefiles(path):
    cwd = os.getcwd()
    dst = os.path.abspath(os.path.dirname(path))
    
    for file in os.listdir(os.getcwd()):
        filelist = (os.path.join(os.path.abspath(file),dst))
        if ((file.endswith('.txt') or file.endswith('.dat')) and (file.find('probe')!=-1 or file.find('mem')!=-1 or file.find('cpu')!=-1 or file.find('errorsandwarns')!=-1 or file.find('systemdetails')!=-1)):
            try:
                print('Moving '+os.path.abspath(file)+' to '+dst)
                shutil.move(os.path.abspath(file),dst)
            except IOError:
                 print(file+' already exists...Removing file')
                 os.remove(os.path.join(dst,file))
                 shutil.move(os.path.abspath(file),dst)

                
##Main function
def main():
    global filename
    global systemdetails
    global cpu
    global mem
    global probe
    
    cleanup()
    
    print('Enter the full path to AS bundle zip file :')
    path = raw_input()

    while True:
        print('Enter valid case number :')
        casenum = raw_input()

        if casenum.isdigit():
            break

    filename = str(casenum)+'_'+'errorsandwarns.txt'
    systemdetails = str(casenum)+'_'+'systemdetails.txt'
    cpu = str(casenum)+'_'+'cpu.dat'
    mem = str(casenum)+'_'+'mem.dat'
    probe = str(casenum)+'_'+'probe.dat'
    
    unzip(path)
    navigatefolders()
        
    movefiles(path)
    cleanup()
    
main()
