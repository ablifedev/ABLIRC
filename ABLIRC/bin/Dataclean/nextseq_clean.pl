#!/usr/bin/perl -w
#
my $ver = "1.0";

use strict;
use warnings;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);
use List::Util qw(first max maxstr min minstr reduce shuffle sum);

#


my %opts;
GetOptions( \%opts, "samplename=s", "fq=s", "other=s", "o=s" );

if ( !defined( $opts{samplename} ) ) {
    print <<"	Usage End.";

	Description:This programme is used for

		Version: $ver

	Usage:perl $0

		-samplename       sample name           must be given
		-fq               raw fq file           must be given
		-other            other                 option, default is NULL
		-o                outdir                option, default is ./

	Usage End.

    exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime( localtime( time() ) );
print "\nStart Time :[$Time_Start]\n\n";
###################################

my $samplename = $opts{samplename};
my $fqfile     = $opts{fq};
my $other      = defined( $opts{other} ) ? $opts{other} : "cat";

my $current_dir = `pwd`;
chomp($current_dir);
my $outdir = defined( $opts{o} ) ? $opts{o} : "./";
`mkdir -p $outdir` if ( !-d $outdir );

$outdir = &AbsolutePath( "dir",  $outdir );
$fqfile = &AbsolutePath( "file", $fqfile );

chdir($outdir);

`rm -rf clean.sh*`;

if ( $fqfile =~ /\.gz$/ ) {
`cd $outdir && zcat $fqfile | cutadapt -a AGATCGGAAGAGC -m 17 -O 3 -e 0.1 -| $other | fastq_quality_trimmer -Q 33 -t 20 -l 16 | fastq_quality_filter -Q 33 -q 20 -p 70 | cutadapt -a N -m 16 -O 1 -N - | cutadapt -a GGGGGGGGGGGGGG -O 4 -e 0.1 -n 5 - | cutadapt -a AAAAAAAAAAAAAAA -m 16 -O 4 -e 0.1 - > $samplename\.fq && fastqc $samplename\.fq && rm -rf $samplename\.fq_fastqc.zip`;
}
else {
`cd $outdir && cat $fqfile | cutadapt -a AGATCGGAAGAGC -m 17 -O 3 -e 0.1 -| $other | fastq_quality_trimmer -Q 33 -t 20 -l 16 | fastq_quality_filter -Q 33 -q 20 -p 70 | cutadapt -a N -m 16 -O 1 -N - | cutadapt -a GGGGGGGGGGGGGG -O 4 -e 0.1 -n 5 - | cutadapt -a AAAAAAAAAAAAAAA -m 16 -O 4 -e 0.1 - > $samplename\.fq && fastqc $samplename\.fq && rm -rf $samplename\.fq_fastqc.zip`;
}

# `perl /public/bin/qsub-sge.pl --queue new.q --resource vf=10.0G --maxproc 50 clean.sh` ;

# # my $tempoutdir = "cleanData";
# # `mkdir -p $tempoutdir` if (!-d $tempoutdir) ;
# # `mv *clean_fq $tempoutdir`;
# # $tempoutdir = "FASTQC";
# # `mkdir -p $tempoutdir` if (!-d $tempoutdir) ;
# # `mv *_fastqc $tempoutdir`;

# `mkdir -p $cleandir`;
# `mv *clean_fq $cleandir`;
# `mkdir -p $cleandir/FASTQC`;
# `mv *_fastqc $cleandir/FASTQC`;

# ##stat cleanreads and raw reads
# `cd $cleandir/FASTQC && perl /users/chengc/work/Data-clean/cleanreads_stat.pl -i ./ -p _fastqc -o $cleandir/clean_stat && perl5.16 /users/chengc/work/Data-clean/fastqc_stat.pl `;


###############Time_end###########
my $Time_End;
$Time_End = sub_format_datetime( localtime( time() ) );
print "\nEnd Time :[$Time_End]\n\n";

sub AbsolutePath {    # Get the absolute path of the target directory or file
    my ( $type, $input ) = @_;
    my $return;
    if ( $type eq "dir" ) {
        my $pwd = `pwd`;
        chomp $pwd;
        chdir($input);
        $return = `pwd`;
        chomp $return;
        chdir($pwd);
    }
    elsif ( $type eq 'file' ) {
        my $pwd = `pwd`;
        chomp $pwd;
        my $dir  = dirname($input);
        my $file = basename($input);
        chdir($dir);
        $return = `pwd`;
        chomp $return;
        $return .= "\/" . $file;
        chdir($pwd);
    }
    return $return;
}

###############Sub_format_datetime
sub sub_format_datetime {    #Time calculation subroutine
    my ( $sec, $min, $hour, $day, $mon, $year, $wday, $yday, $isdst ) = @_;
    $wday = $yday = $isdst = 0;
    sprintf(
        "%4d-%02d-%02d %02d:%02d:%02d",
        $year + 1900,
        $mon + 1, $day, $hour, $min, $sec
    );
}
