DESCRIPTION
==========================================================
Python Tools / Wrappers that are used for the Political Speech project.

[speech_from_phrase.py]
- To be used directly from the command line or with run_python in make.py.
- Syntax:

    python speech_from_phrase.py "[two-word-phrase]" session_number "[output dir]" "[LN/GPO]"

    The third argument "[output dir]" is optional. The default is "../output".
    
    The fourth argument "[LN/GPO]" is only meaningful when session == 104: we have a choice of 
    Congressional Record Data to use in that case.
    
    The first argument "[two-word-phrase]" has to be a two-word-phrase separated by 1 space. This is a
    stemmed phrase that is used in the count files.
    
    The second argument has to be a session number between 43 and 110.
    
    Note: The ""s are important.
    
- Usage:
    An output file speech_[two-word-phrase]_session.txt will be produced in [output dir].
    
    The content is a list of speeches in the session specified which include the stemmed phrase specified. 
    
    Specifically, each output line contains:
    speechid, date of speech, phrasecount, speakerindex, speakername, chamber, state, party, speech.

    Note on speech output: Each of the matched phrase (original phrase before stemming) in each speech is 
        enclosed between "_START" and "_END" for easy identification.

NOTES
==========================================================