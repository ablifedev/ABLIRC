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
GetOptions(\%opts,"sense=s","antisense=s","reads","o=s");

if(!defined($opts{sense}) || !defined($opts{antisense}) || !defined($opts{o}) )
{
	print <<"	Usage End.";

	Description:This programme is used for ~
		
		Version: $ver

	Usage:perl $0

		-sense               infile             must be given

		-antisense           infile             must be given

		-reads               default is filter region cluster,set to filter reads

		-o                             outfile            must be given

	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n";
###################################

my $sense=$opts{sense};	#get the content of parameter of -i
my $antisense=$opts{antisense};	#get the content of parameter of -i
my $out=$opts{o};	#get the content of parameter of -o

my %cluster;
open (SENSE,"$sense") || die "Can't open $sense\n";			#open a file as reading
while (<SENSE>) {
	chomp;
	my @line = split(/\t/,$_);
	next if (/^#/);
	next if (/^Gene:/);
	my $key = $line[1].":".$line[2].":".$line[3].":".$line[4].":".$line[5];
	if($opts{reads}){
		$key = $_;
	}
	$cluster{$key}="";
}
close(SENSE);


my $tag=0;
my ($previous,$after_filter)=(0,0);

open (OUT,">$out") || die "Can't creat $out\n";		#open a file as writing
open (ANTISENSE,"$antisense") || die "Can't open $antisense\n";			#open a file as reading
while (<ANTISENSE>) {
	chomp;
	my @line = split(/\t/,$_);
	if ($_!~/^#/ and $_!~/^Gene:/ and $_!~/^$/){
		my $key = $line[1].":".$line[2].":".$line[3].":".$line[4].":".$line[5];
		if($opts{reads}){
			$key = $_;
		}
		next if defined($cluster{$key});
	}
	print OUT $_,"\n";
}
close(ANTISENSE);
close(OUT);

# print $previous,"\t",$after_filter,"\n";

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

