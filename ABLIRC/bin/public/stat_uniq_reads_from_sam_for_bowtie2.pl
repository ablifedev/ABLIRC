#!/usr/bin/perl -w
# 
# Copyright (c)   AB_Life 2012
# Writer:         CHENGCHAO <chaocheng@ablife.cc>
# Program Date:   2012.
# Modifier:       CHENGCHAO <chaocheng@ablife.cc>
# Last Modified:  2012.
my $ver="1.0.0";

use strict;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);

#Before writing your programme，you must write the detailed time、discriptions、parameter and it's explanation,Meanwhile,annotation your programme in English if possible.
##stat uniq reads from sam for bowtie2.


my %opts;
GetOptions(\%opts,"i=s","o=s" );

if(!defined($opts{i}) || !defined($opts{o}))
{
	print <<"	Usage End.";

	Description:This programme is used for filtering uniq reads from bed file after alignment with bowtie
		
		Version: $ver

	Usage:perl $0

		-i           infile          must be given

		-o           outfile         must be given

	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n";
###################################

my $in=$opts{i};	#get the content of parameter of -i
my $out=$opts{o};	#get the content of parameter of -o

#HWUSI-EAS1879:76:FC:8:1:6975:944#0/1	0	NC_008471.1	13065048	1	35M	*	0	0	ATGTCATTCCGTAGTATAGTTCGTGACATGAGGGA	KKMIHIJRRTTRRTPRRWVXXX_____YYYYY___	AS:i:0	XS:i:0	XN:i:0	XM:i:0	XO:i:0	XG:i:0	NM:i:0	MD:Z:35	YT:Z:UU

open (OUT,">$out") || die "Can't creat $out\n";		#open a file as writing
open (IN,"$in") || die "Can't open $in\n";			#open a file as reading

my ($sum, $uniq, $xnd, $other) = (0,0,0,0); 
my $header;
while (<IN>){
	my ($a, $b) = (0, 0);
	chomp;
	if ($_ =~ /^\@/){
		print OUT "$_\n";
		$header ++;
	}
	else {$sum ++};
	$a = 1 if (/AS:i/);
	$b = 1 if (/XS:i/);
	if ($a ==1 ){
		if ($b == 0){
			$uniq ++;
			print OUT "$_\n";
		}
		if ($b == 1){
			$xnd ++;
		}
	}
	elsif ($a == 0){
		$other ++;
	#header number will counted in this list
	}
}


close(IN);
close(OUT);

my $total_count = $uniq + $xnd;
print "input sam is : $in\n";
print "output uniq sam is : $out\n";
print "Input_data_count:\t$sum\n";
print "total_mapped_reads_count:\t",$total_count,"(",sprintf("%3.2f%%",$total_count/$sum*100),")\n";
print "uniq_mapped_reads_count:\t",$uniq,"(",sprintf("%3.2f%%",$uniq/$sum*100),")\n";
print "multiple_mapped_reads_count:\t",$xnd,"(",sprintf("%3.2f%%",$xnd/$sum*100),")\n";
if ($total_count>0) {
	print "uniq_mapped_reads_count/total_mapped_reads_count:$uniq/$total_count(",sprintf("%3.2f%%",$uniq/$total_count*100),")\n";
	print "multiple_mapped_reads_count/total_mapped_reads_count:$xnd/$total_count(",sprintf("%3.2f%%",$xnd/$total_count*100),")\n";
}
###############Time_end###########
my $Time_End;
$Time_End = sub_format_datetime(localtime(time()));
print "\nEnd Time :[$Time_End]\n\n";

###############Sub_format_datetime
sub sub_format_datetime {#Time calculation subroutine
    my($sec, $min, $hour, $day, $mon, $year, $wday, $yday, $isdst) = @_;
	$wday = $yday = $isdst = 0;
    sprintf("%4d-%02d-%02d %02d:%02d:%02d", $year+1900, $mon+1, $day, $hour, $min, $sec);
}

