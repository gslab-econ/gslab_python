#! /usr/bin/env python
import sys, datetime, time, os, codecs
from private.preliminaries import start_logging, parse_command_options, end_logging, locatefiles
from private.custom import Custom_globals, Custom_prelims, Custom_proc, Custom_wrapup
from private.exceptionclasses import CustomError, CritError
import private.messages as messages
   
def main():
    #define variables; prepare output file
    LOGFILE = start_logging()
    options = parse_command_options(sys.argv[1:], LOGFILE)
    rawfilelist = locatefiles('*', options['raw'])
    globals = Custom_globals()
    prelims = Custom_prelims(globals,options['out'], LOGFILE)
    
    #loop over each file in raw directory
    for rawfile_path in rawfilelist:
        timestart = time.clock()
        
        print >> LOGFILE, messages.note_reading % rawfile_path
        rawfile=codecs.open(rawfile_path, 'rU', encoding='utf-8')
        
        #loop over each line in each file, and process
        try: 
            for line in rawfile:
                Custom_proc(line,globals,prelims,options,LOGFILE)
        except:
            raise CritError(messages.crit_error_readfail)
        
        rawfile.close()
        timeend = time.clock()
        print >>LOGFILE, messages.time_filetime % (os.path.basename(rawfile_path),
                                                   str("%.2f" % (timeend - timestart)))

    #close output file; summarize extraction
    Custom_wrapup(globals,options['out'],prelims,LOGFILE)
    end_logging(LOGFILE)

if __name__=="__main__":
    main()  
  