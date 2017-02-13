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
GetOptions(\%opts,"gene_sense_peak=s","gene_antisense_peak=s" ,"o=s");

if(!defined($opts{gene_sense_peak}) || !defined($opts{gene_antisense_peak}) || !defined($opts{o}) )
{
	print <<"	Usage End.";

	Description:This programme is used for ~
		
		Version: $ver

	Usage:perl $0

		-gene_sense_peak               infile             must be given

		-gene_antisense_peak           infile             must be given

		-o                             outfile            must be given

	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n";
###################################

my $gene_sense_peak=$opts{gene_sense_peak};	#get the content of parameter of -i
my $gene_antisense_peak=$opts{gene_antisense_peak};	#get the content of parameter of -i
my $out=$opts{o};	#get the content of parameter of -o

my %cluster;
open (SENSE,"$gene_sense_peak") || die "Can't open $gene_sense_peak\n";			#open a file as reading
while (<SENSE>) {
	chomp;
	my @line = split(/\t/,$_);
	if ($line[0]=~/^>(\S+)/) {
		$cluster{$1}="";
	}
}
close(SENSE);


my $tag=0;
my ($previous,$after_filter)=(0,0);

open (OUT,">$out") || die "Can't creat $out\n";		#open a file as writing
open (ANTISENSE,"$gene_antisense_peak") || die "Can't open $gene_antisense_peak\n";			#open a file as reading
$/="Gene:";
while (<ANTISENSE>) {
	chomp;
	next if (/^$/) ;
	next if (/\#+/) ;
	$previous++;
	my @line = split(/\n/,$_);
	my $title="Gene:".shift(@line);
	my $last_line = pop @line;
	my @temp_cluster=();
	foreach my $temp_line (@line) {
		if ($temp_line=~/^>(\S+)/) {
			if (not defined($cluster{$1})) {
				$tag=1;
				push @temp_cluster,$temp_line;
			}
			else{
				$tag=0;
			}
		}
		else{
			if ($tag==1) {
				push @temp_cluster,$temp_line;
			}
		}
	}
	if (@temp_cluster) {
		$after_filter++;
		unshift @temp_cluster,$title;
		push @temp_cluster,$last_line;
		foreach my $tmp_line (@temp_cluster) {
			print OUT $tmp_line,"\n";
		}
	}
}
close(ANTISENSE);
close(OUT);

print $previous,"\t",$after_filter,"\n";

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

