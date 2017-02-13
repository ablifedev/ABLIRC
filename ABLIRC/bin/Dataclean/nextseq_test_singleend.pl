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
GetOptions( \%opts, "samplename=s", "fq=s", "cleandir=s", "o=s" );

if ( !defined( $opts{samplename} ) ) {
    print <<"	Usage End.";

	Description:This programme is used for

		Version: $ver

	Usage:perl $0

		-samplename       sample name           must be given
		-fq               raw fq file           must be given
		-cleandir         cleandir              must be given
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
my $cleandir   = $opts{cleandir};

my $outdir = defined( $opts{o} ) ? $opts{o} : "./";
`mkdir -p $outdir` if ( !-d $outdir );

$outdir = &AbsolutePath( "dir",  $outdir );
$fqfile = &AbsolutePath( "file", $fqfile );

chdir($outdir);

`perl $Bin/stat_uniq_tag.pl -q $fqfile > $samplename\_uniqtag && ln -s -f $cleandir/$samplename\.fq_fastqc . && sh $Bin/gc_dup.sh $samplename\.fq && source $Bin/../../venv/venv-py2/bin/activate && python $Bin/seq_quality_stat.py --input $fqfile -o $samplename\_q30`;

###stat result
###stat result
#chdir("$outdir");
#`perl $Bin/stastics.pl $samp $cleandir/raw_stat $cleandir/clean_stat $cleandir/uniq_stat $cleandir/gc_dup $cleandir/q30`;
#
#`mv $cleandir/FASTQC .`;
#
#`cd $cleandir && mkdir -p tmp && mv *.sh *.sh.* *_stat tmp`;

###############Time_end###########
my $Time_End;
$Time_End = sub_format_datetime(localtime(time()));
print "\nEnd Time :[$Time_End]\n\n";

sub AbsolutePath {		# Get the absolute path of the target directory or file
	my ($type,$input) = @_;
	my $return;
	if ($type eq "dir"){
		my $pwd = `pwd`;
		chomp $pwd;
		chdir($input);
		$return = `pwd`;
		chomp $return;
		chdir($pwd);
	} elsif($type eq 'file') {
		my $pwd = `pwd`;
		chomp $pwd;
		my $dir=dirname($input);
		my $file=basename($input);
		chdir($dir);
		$return = `pwd`;
		chomp $return;
		$return .="\/".$file;
		chdir($pwd);
	}
	return $return;
}

###############Sub_format_datetime
sub sub_format_datetime {#Time calculation subroutine
    my($sec, $min, $hour, $day, $mon, $year, $wday, $yday, $isdst) = @_;
	$wday = $yday = $isdst = 0;
    sprintf("%4d-%02d-%02d %02d:%02d:%02d", $year+1900, $mon+1, $day, $hour, $min, $sec);
}
