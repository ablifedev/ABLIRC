#!/usr/bin/perl -w
# 
# Copyright (c)   AB_Life 2011
# Writer:         xuxiong <xuxiong19880610@163.com>
# Program Date:   2011.06.28
# Modifier:       xuxiong <xuxiong19880610@163.com>
# Last Modified:  2011.06.28
my $ver="1.0.0";

use strict;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);
use List::Util qw(first max maxstr min minstr reduce shuffle sum);

#Before writing your programmeyou must write the detailed timediscriptionsparameter and it's explanation,Meanwhile,annotation your programme in English if possible.

my %opts;
GetOptions(\%opts,"gene_peak=s","p_value=s","o=s" );

if(!defined($opts{gene_peak}) || !defined($opts{p_value}) || !defined($opts{o})  )
{
	print <<"	Usage End.";

	Description:This programme is used for 
		
		Version: $ver

	Usage:perl $0

		-gene_peak           infile          must be given

		-p_value             infile          must be given

		-o                   outfile         must be given

	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n";
###################################

my $gene_peak=$opts{gene_peak};
my $p_value=$opts{p_value};
my $out=$opts{o};


my %p=();
open (P,"<$p_value") or die "Can't open $p_value\n";
while(<P>){
	chomp;
	next if (/^#/);
	my @line = split(/\t/);
	$p{$line[1]} = $line[2];
}
close (P) ;

# Gene:   826207  827522  ENSG00000225880.5       -
# >chr1_3 chr1    826769  826795  3       -
# >chr1_4 chr1    826819  826822  3       -
# >chr1_5 chr1    826822  826827  4       -
# >chr1_6 chr1    826827  826829  5       -
# >chr1_7 chr1    826829  826843  6       -
# >chr1_8 chr1    826843  826852  5       -
# >chr1_9 chr1    826852  826853  4       -
# >chr1_10        chr1    826853  826855  3       -


open (OUT,">$out") || die "Can't creat $out\n";
open (GENE_PEAK,"<$gene_peak") || die "Can't open $gene_peak\n";	#open a file as reading
my $gid = "";
my $gline = "";
my $flag = 0;
while (<GENE_PEAK>) {
	chomp;
	next if (/^$/) ;
	next if (/^\#/) ;
	my @line = split(/\t/);
	if (/^Gene:/){
		$gid = $line[3];
		$gline = $_;
		$flag = 0;
		next;
	}elsif(/^>/){
		next if (not defined($p{$gid}));
		if ($line[4] >= $p{$gid}){
			if ($flag == 0){
				print OUT $gline,"\n";
				$flag = 1;
			}
			print OUT $_,"\n";
		}
	}
}
close(GENE_PEAK);
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
