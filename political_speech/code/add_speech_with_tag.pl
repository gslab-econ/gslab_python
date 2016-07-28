use Lingua::Stem::Snowball;

#########################################
# Main
#########################################

my $parameter_file     = "./temp_dir/input_param.txt";
my $stopwords_file     = "./temp_dir/external/stopWords.txt";
my $info_file          = "./temp_dir/speechid_descr_speaker.txt";
my $output_dir         = $ARGV[0];
my $speech_dir         = "./temp_dir/external/speeches";

(my $session, my $phrase_search) = &get_parameters($parameter_file);

my %speechid_list;
&get_speechid_list(\%speechid_list, $info_file);

my %stopword;
&get_stopwords(\%stopword, $stopwords_file);

my %speech_list;
&get_speech_list($speech_dir, \%speech_list, \%speechid_list, \%stopword, $session, $phrase_search);

my @words = split(/ /, $phrase_search);
my $output_file = $output_dir . "/speeches_" . $words[0] . "_" . $words[1] . "_" . $session . ".txt";
&add_speech(\%speech_list, $info_file, $output_file);

#########################################
# Functions
#########################################

sub get_parameters {
    my ($parameter_file) = @_;
    my (@words, $session, $phrase_search);
    open (INFILE, "< $parameter_file") || die("Can't find input file: $parameter_file");

    while (my $line = <INFILE>){
        chomp $line;
        @words = split(/ /, $line);
        if ($words[0] =~ /session/i) {
            $session = $words[1];
            $session =~ s/\s*$//;
            $session = int($session);
        }
        elsif ($words[0] =~ /phrase_search/i) {
            my $phrase1 = $words[1];
            $phrase1 =~ s/\s*$//;
            $phrase1 =~ s/^"//;
            my $phrase2 = $words[2];
            $phrase2 =~ s/\s*$//;
            $phrase2 =~ s/"$//;
            $phrase_search = $phrase1 . " " . $phrase2;
        }
    }

    close(INFILE);

    return ($session, $phrase_search);
}

sub get_speechid_list {
    my ($speechid_list, $info_file) = @_;

    open(INPUT, $info_file) || die ("Can't find your input file: $info_file.");
    my $line = <INPUT>;
    while ($line = <INPUT>){
        chomp $line;
        @sections = split(/\|/,$line);
        $speechid = int($sections[0]);
        $speechid_list -> {$speechid} = 0;
    }
    close(INPUT);
}

# Read stopwords from file
sub get_stopwords {
    my ($stopword, $stopwords_file) = @_;

    open (STOPWORD, $stopwords_file) || die ("Can't find input file: $stopwords_file.");
    while (my $line = <STOPWORD>){
        chomp $line;
        $stopword{$line} = 1;
    }
    close(STOPWORD);
}

sub get_speech_list {
    my ($speech_dir, $speech_list, $speechid_list, $stopword, $session, $phrase_search) = @_;
    my $input;
    if ($session >= 100) {
        $input = $speech_dir . "/speeches_" . $session . ".txt";
    }
    else {
        $input = $speech_dir . "/speeches_0" . $session . ".txt";
    }
    open(INPUT, $input) || die ("Can't find your input file $input.");

    my $line = <INPUT>;
    while ($line = <INPUT>){
        my $snowball = Lingua::Stem::Snowball->new( lang => 'en' );
        chomp $line;
        my @sections = split(/\|/,$line);
        my $speechid = int($sections[0]);
        my $speech = $sections[1];
        if (defined ($speechid_list -> {$speechid})) {
            # Construction of phrases for each speech.
            my $lastword = "";
            my $word = "";
            my $pos = 0;
            my $prepos = 0;
            my $str = "";

            # A word is any combination of consecutive letters or numbers not including spaces, commas, hyphens, etc.
            while ($speech =~ /([\w0-9]+)/g){
                $word = lc($1);
                if (not(defined($stopword{$word}))){
                    $word = $snowball->stem($word);
                    # If this isn't the first word of the speech then construct the phrase
                    if ($lastword ne ""){
                        $phrase = $lastword . " " . $word;
                        if ($phrase eq $phrase_search) {
                            $str = $str . substr($speech, $pos, $+[1] - $pos + 1) . "_END ";
                            substr $str, length($str) - ($+[1] - $prepos) - 6, 0, "_START ";
                        }
                        else {
                            $str = $str . substr($speech, $pos, $+[1] - $pos + 1);
                        }
                        $pos = $+[1] + 1;
                    }
                    $lastword = $word;
                    $prepos = $-[1];
                }
            }
            if ($pos <= length($speech)) {
                $str = $str . substr($speech, $pos, length($speech) - $pos + 1);
            }
            $speech_list -> {$speechid} = $str;
        }
    }
    close(INPUT);
}

sub add_speech {
    my ($speech_list, $info_file, $output_file) = @_;

    open(INPUT, "< $info_file") || die ("Can't find your input file: $info_file.");
    open(OUTPUT, "> $output_file") || die ("Can't open your ouput file: $output_file.");
    print OUTPUT "speechid|date|phrasecount|chamber|speakerindex|state|crname|party|speech\n";
    my $line = <INPUT>;
    while ($line = <INPUT>){
        chomp $line;
        @sections = split(/\|/,$line);
        $speechid = int($sections[0]);
        my $speech = $speech_list -> {$speechid};
        print OUTPUT "$line|$speech\n";
    }

    close(INPUT);
    close(OUTPUT);
}