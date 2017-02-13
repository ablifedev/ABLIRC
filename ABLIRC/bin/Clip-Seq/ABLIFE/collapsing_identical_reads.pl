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
GetOptions(\%opts,"uniq=s","o=s" );

if(!defined($opts{uniq}) || !defined($opts{o}) )
{
	print <<"	Usage End.";

	Description:This programme is used for collapsing reads with identical start (5’) and end (3’)
	coordinates in bed format on the same chromosome to a single observation 
		
		Version: $ver

	Usage:perl $0

		-uniq         infile          must be given

		-o            outfile         must be given

	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n";
###################################

my $uniq_bed=$opts{uniq};
my $out=$opts{o};

my %hash=();
open (IN,"$uniq_bed") || die "Can't open $uniq_bed\n";			#open uniq bed file
#Chr3    16756117        16756140        SBS_0010:3:1:2632:1080#0/1      0       +
#Chr5    26300979        26300999        SBS_0010:3:1:5659:1081#0/1      0       -
my $read_count=0;
while (<IN>) {
	chomp;
	my @line=split(/\s+/,$_);
	if (not exists($hash{$line[0]}{$line[1]}{$line[2]}{$line[5]}) ) {
		$hash{$line[0]}{$line[1]}{$line[2]}{$line[5]}->[0]="--";
		$hash{$line[0]}{$line[1]}{$line[2]}{$line[5]}->[1]=1;
		$read_count++;
	} else {
		$hash{$line[0]}{$line[1]}{$line[2]}{$line[5]}->[1]++;
	}
}
close(IN);

print "identical reads(without PCR bias):",$read_count,"\n";

open (OUT,">$out") || die "Can't creat $out\n";		#open a file as writing
foreach my $chr (sort keys %hash) {
	foreach my $start (sort {$a <=> $b} keys %{$hash{$chr}}) {
		foreach my $end (sort {$a <=> $b} keys %{$hash{$chr}{$start}}) {
			foreach my $strand (sort keys %{$hash{$chr}{$start}{$end}}) {
				print OUT $chr,"\t",$start,"\t",$end,"\t",join("\t",@{$hash{$chr}{$start}{$end}{$strand}}),"\t",$strand,"\n";
			}
		}
	}
}
close(OUT);

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

