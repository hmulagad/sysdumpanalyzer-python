import os
import re
import sqlite3
import tarfile
import shutil
import stat

global filename
global systemdetails
filename = 'errorsandwarns.txt'
systemdetails = 'systemdetails.txt'


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

    print('Removing prior',filename)

    for fname in os.listdir(cwd):
        if fname.endswith('.txt'):
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


#Directory walk of the extracted bundle
def navigatefolders():
    
    cwd = os.getcwd()
    filelist = []
    configfiles = []
    
    for fdname in os.listdir(cwd):
        if os.path.isdir(fdname):
            for path,subdirs,files in os.walk(os.path.abspath(fdname)):
                for x in files:
                    if (x.endswith('.txt')):
                        configfiles.append(os.path.join(os.path.abspath(path),x))
                    else:
                        if (x.endswith('.log') or x.endswith('.out')):
                            filelist.append(os.path.join(os.path.abspath(path),x))

    for logfile in filelist:
        print('Processing ',logfile)
        errorsandwarns(logfile)
    
    for logfile in configfiles:
        #print(logfile)
        configdetails(logfile)

##Function to search for all Errors and Warnings in log files
def errorsandwarns(logfile):

    searchstrings = ['ERROR','WARN','FATAL','DBA-DBW-E','DBA-PCX-E','DBA-SQL-E','DBA-DSP-E','DBA-ATS-E']
    ##'DBA-DBW-W','DBA-PCX-W','DBA-SQL-W','DBA-DSP-W','DBA-ATS-W' - Warnings for ASX, add if needed

    try:
        fobj = open(logfile)
        fwrite = open(filename,'a')
        fwrite.write('\n'+'******Errors and Warnings in file '+ str(logfile)+'******' + '\n\n')

        for i in fobj:
            for string in searchstrings:
                if string in i.strip():
                    fwrite.write(i)

        fobj.close()
        fwrite.close()
            
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
        
##Main function
def main():

    cleanup()
    
    print('Enter the full path to AS bundle zip file :')
    path = raw_input()

    unzip(path)
    navigatefolders()
    
main()
