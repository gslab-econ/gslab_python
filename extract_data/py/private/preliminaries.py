#! /usr/bin/env python
import os, fnmatch, sys, datetime, getopt, re, mimetypes
from private.exceptionclasses import CustomError, CritError
import private.messages as messages


######################################################
# Logging
######################################################

def start_logging():
	try:
		LOGFILE = open('./extract_data.log','wb') 
	except:
		raise CritError(messages.crit_error_log % 'extract_data.log')
	time_begin = datetime.datetime.now().replace(microsecond=0)
	orig_stderr = sys.stderr
	sys.stderr = LOGFILE
	working_dir = os.getcwd()
	print >> LOGFILE, messages.time_logstart % (time_begin,working_dir)
    
	return LOGFILE

def end_logging(LOGFILE):
	time_end = datetime.datetime.now().replace(microsecond=0)
	print >> LOGFILE, messages.time_logend % time_end
	LOGFILE.close()


######################################################
# Classes
######################################################    

#defines a class of line objects to be read from each raw file
class lineclass(unicode):
    def __init__(self,contents):
        self.contents = contents
        
    #places fixed-width elements into cols of a 2d-list
    def fixedwidth(self,widths,fields):
        templist=[None]*fields
        for var in range(fields):
            templist[var]=(self.contents[(widths[var][0]-1):widths[var][1]])
            
        return templist

        
######################################################
# General Functions
######################################################    
def parse_command_options(arguments, LOGFILE):
    opts, extraparams = getopt.getopt(arguments,"o:r:")

    #read and parse options
    for option_switch, option_text in opts:
        if option_switch in ['-r', '--rawfolder']:
            rawfolder = option_text
        elif option_switch in ['-o', '--outfolder']:
            outfolder = option_text
        else: 
            raise CritError(messages.crit_error_badoption % (option_switch,option_text))
    #check if missing options
    if 'rawfolder' not in vars() or 'outfolder' not in vars():
        raise CritError(messages.crit_error_missingoption)
    #check if raw folder present
    if (os.path.isdir(rawfolder)):
        print >>LOGFILE, messages.note_rawdir % rawfolder
    else:
        raise CritError(messages.crit_error_norawfolder % rawfolder)
    #create output dir
    if not (os.path.isdir(outfolder)):
        try: 
            os.makedirs(outfolder)
            print >>LOGFILE, messages.note_outdir % outfolder
        except:
            raise CritError(messages.crit_error_outputdirfail % outfolder)

    return( {'raw': rawfolder, 'out': outfolder })

#enumerate all files in raw folder    
def locatefiles(name, root=os.curdir):
    path=os.path.abspath(root)
    filelist=os.listdir(path)
    for file in fnmatch.filter(filelist,name):
        #ignore hidden files in svn folder
        if not re.search("\.svn", file):
            yield os.path.join(path,file)



            
