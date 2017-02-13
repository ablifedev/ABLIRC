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

#print $outdir,"\n";
my $p_cut_off=0.01;

my %gene=();
my $n=0;
my %p=();
my %random_max_height=();
my $genename = "";
open (P,"<$p_value") or die "Can't open $p_value\n";
LABEL1: while (<P>) {
	chomp;
	$n++;
	next if ($n==1);
	if (/^\#+$/) {
		next if not (%p);
		my @random_height=sort {$a<=>$b} keys %p;
		foreach my $h (@random_height){
			if ($p{$h}<=$p_cut_off) {
				$random_max_height{$genename}=$h;
				%p=();
				next LABEL1;
			}
		}
		$random_max_height{$genename}=($random_height[-1]+1);
		%p=();
	}elsif($_=~/^Gene:(\S+)/){
		$genename = $1;
	}
	elsif($_!~/^Gene:/){
		my @line=split;
		$p{$line[0]}=$line[-1];
	}
	if (eof(P)) {
		my @random_height=sort {$a<=>$b} keys %p;
		foreach my $h (@random_height){
			if ($p{$h}<=$p_cut_off) {
				$random_max_height{$genename}=$h;
				last LABEL1;
			}
		}
		$random_max_height{$genename}=($random_height[-1]+1);
	}
}
close (P) ;


# print scalar(@random_max_height),"\n";
#exit;

open (OUT,">$out") || die "Can't creat $out\n";
open (GENE_PEAK,"<$gene_peak") || die "Can't open $gene_peak\n";	#open a file as reading
$/="Gene:";
my $gene_num=0;
my $peak_num=0;
my $tag=0;
while (<GENE_PEAK>) {
	chomp;
	next if (/^$/) ;
	next if (/^\#/) ;
	my @line=split(/\n/,$_);
	my @gene_pos=split("\t",shift(@line));
	my $gene = $gene_pos[3];
	my $last_line = pop(@line);
#	print $last_line,"\n";
	my $Random_Max_Height=$random_max_height{$gene};
	my @tmp=();
	foreach my $temp_line (@line) {
		if ($temp_line =~ /^>/) {
			my @temp_peak=split(/\t/,$temp_line);
			if ($temp_peak[-3]>=$Random_Max_Height) {
				$peak_num++;
				$tag=1;
				push @tmp,$temp_line;
			}
			else{
				$tag=0;
			}
		}
		else{
			if ($tag==1) {
				push @tmp,$temp_line;
			}
		}
	}
	if (@tmp) {
		$gene_num++;
		print OUT "Gene:",join("\t",@gene_pos),"\n";
		print OUT join("\n",@tmp),"\n";
#			print OUT join("\t",@conclud),"\n";
	}
}
close(GENE_PEAK);
close(OUT);

print "Cluster_num: ",$peak_num,"\nGene_num: ",$gene_num,"\n";
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
