#! /usr/bin/env python
import subprocess, shutil, os, sys
gslab_make_path = os.getenv('gslab_make_path')
subprocess.call('svn export --force -r 18315 ' + gslab_make_path + ' "' + os.path.dirname(os.path.realpath(__file__)) + '/gslab_make"', shell = True)
from gslab_make.py.get_externals import *
from gslab_make.py.make_log import *
from gslab_make.py.run_program import *
from gslab_make.py.dir_mod import *
    
def find_speech(output_dir):
    set_option(makelog = "./temp_dir/make.log", external = "", temp = "", output = "")
    start_make_logging()

    # GET EXTRA EXTERNALS
    get_externals('./temp_dir/externals.txt', './temp_dir/external')

    # ANALYSIS
    run_stata(program = os.path.dirname(os.path.realpath(__file__)) + '/get_info.do')
    run_perl(program = os.path.dirname(os.path.realpath(__file__)) + '/add_speech_with_tag.pl', args = output_dir)
    
    end_make_logging()    
            
def create_input_param(phrase_search, session):     
    PARAM = open('./temp_dir/input_param.txt', 'wb')
    session = int(session)
    print >> PARAM, 'session', session
    print >> PARAM, 'phrase_search "%s"' % phrase_search    
    PARAM.close()

def create_external_list(session, crtype):
    EXTERNAL = open('./temp_dir/externals.txt', 'wb') 
    data_rev = 17963
        
    print >> EXTERNAL, "%s\t%%svn%%/lib/stata/gslab_misc\t*\t./lib/stata/gslab_misc\t\"\"\"\"\t" % data_rev
    print >> EXTERNAL, "%s\t%%svn%%/lib/third_party/stata_tools\t*\t./lib/third_party/stata_tools	\"\"\"\"\t" % data_rev
    print >> EXTERNAL, "%s\t%%svn%%/raw/StopWord Lists/data/\tstopWords_Snowball.txt\t./\tstopWords.txt\t\"\"\"\"\t" % data_rev
    
    session = int(session)
    
    if (session < 100):
        print >> EXTERNAL, "%s\t%%svn%%/derived/LN CR Full Counts/output/\tbyspeech_2gram_0%s.txt\t./counts/\t\"\"\"\"\t" \
            % (data_rev, session)
        print >> EXTERNAL, "%s\t%%svn%%/derived/LN CR Parsed/output/descr/\tdescr_0%s.txt\t./descr/\t\"\"\"\"\t" \
            % (data_rev, session)
        print >> EXTERNAL, "%s\t%%svn%%/derived/LN CR Parsed/output/speeches/\tspeeches_0%s.txt\t./speeches/\t\"\"\"\"\t" \
            % (data_rev, session)
        print >> EXTERNAL, "%s\t%%svn%%/derived/LN CR SpeakerMapping/output/\t0%s_SpeakerMap.txt\t./speakermap\t\"\"\"\"\t" \
            % (data_rev, session)
    elif (crtype == "LN"):
        print >> EXTERNAL, "%s\t%%svn%%/derived/LN CR Full Counts/output/\tbyspeech_2gram_%s.txt\t./counts/\t\"\"\"\"\t" \
            % (data_rev, session)
        print >> EXTERNAL, "%s\t%%svn%%/derived/LN CR Parsed/output/descr/\tdescr_%s.txt\t./descr/\t\"\"\"\"\t" \
            % (data_rev, session)
        print >> EXTERNAL, "%s\t%%svn%%/derived/LN CR Parsed/output/speeches/\tspeeches_%s.txt\t./speeches/\t\"\"\"\"\t" \
            % (data_rev, session)
        print >> EXTERNAL, "%s\t%%svn%%/derived/LN CR SpeakerMapping/output/\t%s_SpeakerMap.txt\t./speakermap\t\"\"\"\"\t" \
            % (data_rev, session)
    else:
        print >> EXTERNAL, "%s\t%%svn%%/derived/GPO CR Full Counts/output/\tbyspeech_2gram_%s.txt\t./counts/\t\"\"\"\"\t" \
            % (data_rev, session)
        print >> EXTERNAL, "%s\t%%svn%%/derived/GPO CR Parsed/output/descr/\tdescr_%s.txt\t./descr/\t\"\"\"\"\t" \
            % (data_rev, session)
        print >> EXTERNAL, "%s\t%%svn%%/derived/GPO CR Parsed/output/speeches/\tspeeches_%s.txt\t./speeches/\t\"\"\"\"\t" \
            % (data_rev, session)
        print >> EXTERNAL, "%s\t%%svn%%/derived/GPO CR SpeakerMapping/output/\t%s_SpeakerMap.txt\t./speakermap\t\"\"\"\"\t" \
            % (data_rev, session)  
            
    EXTERNAL.close()
    
def check_session(session):
    try:
        session = int(session)       
    except:
        print 'The second argument should be a session number.'
        shutil.rmtree(os.path.dirname(os.path.realpath(__file__)) + '/gslab_make')
        sys.exit(1)
    if (session < 43) or (session > 110):
        print 'Session should be a number between 43 and 110'
        shutil.rmtree(os.path.dirname(os.path.realpath(__file__)) + '/gslab_make')
        sys.exit(1)
    return session
    
def check_phrase(phrase_search):
    words = phrase_search.split(' ')
    if len(words) != 2:
        print "The first argument should be a two-word phrase, separated by one space."
        shutil.rmtree(os.path.dirname(os.path.realpath(__file__)) + '/gslab_make')
        sys.exit(1)

def check_output_dir(output_dir):
    if not os.path.isdir(output_dir):
        print "The third argument should be an existing output directory."
        shutil.rmtree(os.path.dirname(os.path.realpath(__file__)) + '/gslab_make')
        sys.exit(1)
        
def check_crtype(session, crtype):
    if (session != 104):
        print 'Warning: session <> 104'        
        if (crtype != "GPO") and (crtype != "LN"):
            print "Warning: Invalid CR type (GPO / LN)"            
        print "Default CR type will be used: session < 105: LN / session >= 105: GPO"
        if session < 105: 
            crtype = "LN"
        else:
            crtype = "GPO"
            
    return crtype        
        
def main():
    if (len(sys.argv) < 3) or (len(sys.argv) > 5):
        print 'Error: Please make sure to enter all arguments.'
        print 'Arguments should be, in order: "[phrase search]" [session] "[output_dir]" "[LN/GPO]".'
        print '"[output_dir]" argument is optional - the default is "../output".'
        print '"[LN/GPO]" argument is only meaningful when session = 104: type of Congressional Record data.'
        shutil.rmtree(os.path.dirname(os.path.realpath(__file__)) + '/gslab_make')
        sys.exit(2)

    phrase_search = sys.argv[1]
    check_phrase(phrase_search)
    session = sys.argv[2]
    session = check_session(session)
    if len(sys.argv) == 3:
        output_dir = "../output"
    else:
        output_dir = sys.argv[3]
    check_output_dir(output_dir)    
 
    if len(sys.argv) < 5:
        if session < 105: 
            crtype = "LN"
        else:
            crtype = "GPO"
    
    if len(sys.argv) == 5:
        crtype = check_crtype(session, sys.argv[4])
    
    if not os.path.isdir('./temp_dir'):
        os.makedirs('./temp_dir')
    create_input_param(phrase_search, session)
    create_external_list(session, crtype)
    find_speech(output_dir)      
    shutil.rmtree('./temp_dir')
    shutil.rmtree(os.path.dirname(os.path.realpath(__file__)) + '/gslab_make')
    
main()
        
