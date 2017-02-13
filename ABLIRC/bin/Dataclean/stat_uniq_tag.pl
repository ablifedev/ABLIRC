#!/usr/bin/perl -w
# 
# Copyright (c)   AB_Life 2011
# Writer:         xuxiong <xuxiong19880610@163.com>
# Program Date:   2011.
# Modifier:       xuxiong <xuxiong19880610@163.com>
# Last Modified:  2011.
my $ver="1.0.0";

use strict;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);

#Before writing your programme，you must write the detailed time、discriptions、parameter and it's explanation,Meanwhile,annotation your programme in English if possible.

my %opts;
GetOptions(\%opts,"q=s" );

if(!defined($opts{q}) )
{
	print <<"	Usage End.";

	Description:This programme is used for filtering uniq reads from bed file after alignment with bowtie
		
		Version: $ver

	Usage:perl $0

		-q           fq file         must be given

	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
#print "\nStart Time :[$Time_Start]\n\n";
###################################

my $fq=$opts{q};

my $total_count=0;
my $uniq_tag=0;
my %reads=();
open(FQ,$fq) or die $!;
while (<FQ>) {
	my $seq = <FQ>;
	chomp($seq);
	# print $seq,"\n";
	$uniq_tag++ if not defined($reads{$seq});
	$reads{$seq}=1;
	<FQ>;<FQ>;
	$total_count++;
}
close FQ;

print "$fq\t";
print "$total_count\t";
print $uniq_tag,"(",sprintf("%3.2f%%",$uniq_tag/$total_count*100),")\n";

###############Time_end###########
my $Time_End;
$Time_End = sub_format_datetime(localtime(time()));
#print "\nEnd Time :[$Time_End]\n\n";

###############Sub_format_datetime
sub sub_format_datetime {#Time calculation subroutine
    my($sec, $min, $hour, $day, $mon, $year, $wday, $yday, $isdst) = @_;
	$wday = $yday = $isdst = 0;
    sprintf("%4d-%02d-%02d %02d:%02d:%02d", $year+1900, $mon+1, $day, $hour, $min, $sec);
}

