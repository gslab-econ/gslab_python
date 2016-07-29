version 12
set more off
adopath + ./temp_dir/external/lib/stata/gslab_misc/ado
loadglob using ./temp_dir/input_param.txt

program main
    find_speechid
    add_descr
    add_speaker
end

program find_speechid
    local sessionstr: display %03.0f $session
    insheet using ./temp_dir/external/counts/byspeech_2gram_`sessionstr'.txt, delimiter("|") clear
    keep if phrase == "$phrase_search"
    save ./temp_dir/speech, replace
end

program add_descr
    local sessionstr: display %03.0f $session
    insheet using ./temp_dir/external/descr/descr_`sessionstr'.txt, delimiter("|") clear
    keep speechid parsedspeakerindex date
    mmerge speechid using ./temp_dir/speech, type(1:1) unmatched(using) ukeep(phrasecount)
    assert _merge == 3
    drop _merge    
    save ./temp_dir/speech_descr, replace
end

program add_speaker
    local sessionstr: display %03.0f $session
    insheet using ./temp_dir/external/speakermap/`sessionstr'_SpeakerMap.txt, clear delim("|")
    drop parsedname
    save ./temp_dir/speakermap, replace
    use ./temp_dir/speech_descr, clear
    mmerge parsedspeakerindex using ./temp_dir/speakermap, type(n:1) unmatched(master)
    drop if _merge != 3
    drop _merge parsedspeakerindex    
    format speechid %16.0f
    save_data ./temp_dir/speechid_descr_speaker.txt, replace outsheet delim("|") noquote ///
        key(speechid date phrasecount chamber speakerindex state crname party)
end

* Execute
main
