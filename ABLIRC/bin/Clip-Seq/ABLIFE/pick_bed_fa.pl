#!/usr/bin/perl -w
# 
# Copyright (c)   ABLife 2015
# Writer:         Cheng Chao


my $ver="1.0.0";

use strict;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);
use List::Util qw(first max maxstr min minstr reduce shuffle sum);

#Before writing your programme，you must write the detailed time、discriptions、parameter and it's explanation,Meanwhile,annotation your programme in English if possible.

my %opts;
GetOptions(\%opts,"bed=s","w=s","o=s","e=s","h" );

if(!defined($opts{bed}) )
{
	print <<"	Usage End.";

	Description:This programme is used for ~
		
		Version: $ver

	Usage:perl $0

		-bed         bed infile           must be given

		-w           whole genome         must be given

		-o           outfile              must be given

		-s           Force strandedness.  option(0|1,default is 1)

		-e           extend length        option(100)

	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n";
###################################

my $current_dir = `pwd`;chomp($current_dir);

my $bed=$opts{bed};
my $whole_genome=$opts{w};
my $outfile=defined $opts{o} ? $opts{o} : "$current_dir/$bed\_out.fa";
my $extend=defined $opts{e} ? $opts{e} : 100;
my $forcestrand=defined $opts{s} ? $opts{s} : 1;

my %genome=();
&load_FA($whole_genome,\%genome);
print "done load FA\n";
open(OUT,">$outfile")||die $!;
&load_bed_seq($bed,\%genome,\*OUT,$extend);
close OUT;

sub load_bed_seq{
	my ($infile,$Genome,$outfile_handle,$Window)=@_;
	my %peak = ();
	open (IN,"$infile") || die $!;
	while (<IN>) {
		chomp;
		next if (/^$/) ;
		next if (/^#/) ;
		next if (/^track/) ;
		my @line = split("\t",$_);
		# chr20   2135052 2135085 --      1.0     +
		next if (exists $peak{$line[0]}{$line[1]}{$line[2]}{$line[5]});
		# print $_,"\n";
		$peak{$line[0]}{$line[1]}{$line[2]}{$line[5]}=1;
		my ($start,$end,$strand) = ($line[1],$line[2],$line[5]);
		$start = $start-$Window;
		$start = 0 if $start < 0;
		$end = $end + $Window;
		my $cut_seq=substr($Genome->{$line[0]},$start,$end-$start+1);
		$cut_seq=&reverse_complement($cut_seq) if ($strand eq "-" && $forcestrand == 1) ;
		print $outfile_handle ">$line[0]\:$start\-$end\($strand\) $line[3]\n",$cut_seq,"\n";
	}
	close(IN);
}

sub load_FA{
	my ($infile,$chr_seq)=@_;
	open(FA,"$infile")||die "Can't open $infile\n";
	$/=">";
	while (<FA>) {
		chomp;
		next if (/^$/); 
		my ($name,$seq)=split(/\n/,$_,2);
		$name =~ s/\s+.+//;
		$seq =~ s/\s+//g;
		$chr_seq->{$name}=$seq;
	}
	$/="\n";
	close FA;
}

sub reverse_complement{
	my $seq=shift;
	$seq=uc($seq);
	$seq=~tr/ATGC/TACG/;
	my $reverse_seq=reverse($seq);
	return $reverse_seq;
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
