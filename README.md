# sysdumpanalyzer-python
sysdumpanalyzer for AR11

What the script does?

The script extracts the sysdump file and reads all the logs and config files to gather system information and
also errors and warnings in the log files present in the sysdump.

The script when completed succesfully will generate 2 files and also unzip the sysdump for you to navigate later on

Text Files - xxxxx_errorsandwarns.txt and xxxxx_systemdetails.txt

What do the output files contain?

xxxxx_errorsandwarns.txt - Contains ERRORS, WARNINGS in all the logs files inside the sysdump
xxxxx_systemdetails.txt  - Contains system level details from the AR11 appliance

How do we run the script?

You can either use Python 2.x(x >=6) or Python 3.x to run the script. Please downloand the appropriate file as we have
separate files for Python 2.x and Python 3.x.

-- Place the script which you have downloaded in a folder
-- Run the script using python command
-- Enter the fullpath along with sysdump file name
-- Enter the case number associated with sysdump
-- Hit enter and let the script run

The output files should be created in the same location where the sysdump is located.

NOTE: The script will fail if you change the sysdump name. You can add Case_<casenumber>_sysydump<xxxxxx>.tgz but if the name is missing the actual sydump name provided by appliance, the script will fail.

 

