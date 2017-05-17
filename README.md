# sysdumpanalyzer-python
sysdumpanalyzer for AR11

What the script does?

The script extracts the sysdump file and reads all the logs and config files to gather system information and
also errors and warnings in the log files present in the sysdump.

The script when completed succesfully will generate 5 files - 2 .txt files and 3 .dat files

Text Files - xxxxx_errorsandwarns.txt and xxxxx_systemdetails.txt
Dat Files - xxxxx_mem.dat, xxxxx_cpu.dat, xxxxx_probe.dat

What do the output files contain?

xxxxx_errorsandwarns.txt - Contains ERRORS, WARNINGS in all the logs files inside the sysdump
xxxxx_systemdetails.txt  - Contains system level details from the AR11 appliance

xxxxx_mem.dat - Use this file to plot Memory values as charts (comma separated values) 
xxxxx_cpu.dat - Use this file to plot CPU values as charts (comma separated values) 
xxxxx_probe.dat - Use this file to plot PROBE values as charts (comma separated values) 

The script does not currently plot any charts. You can use utilities like gnuplot and use the above .dat files
to plot the details you need.

How do we run the script?

You can either use Python 2.x(x >=7) or Python 3.x to run the script. Please downloand the appropriate file as we have
separate files for Python 2.x and Python 3.x.

-- Place the script which you have downloaded in a folder (DO NOT PLACE THE SCRIPT IN THE SAME LOCATION AS SYSDUMPS)
-- Run the script using python command
-- Enter the fullpath along with sysdump file name
-- Enter the case number associated with sysdump
-- Hit enter and let the script run

The output files should be created in the same location where the sysdump is located


