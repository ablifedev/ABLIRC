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
use List::Util qw(first max maxstr min minstr reduce shuffle sum);

#Before writing your programme，you must write the detailed time、discriptions、parameter and it's explanation,Meanwhile,annotation your programme in English if possible.

my %opts;
GetOptions(\%opts,"w=s","g=s","o=s","h" );

if(!defined($opts{w}) || !defined($opts{g}) )
{
	print <<"	Usage End.";

	Description:This programme is used for ~
		
		Version: $ver

	Usage:perl $0

		-w           whole genome         must be given

		-g           gff infile           must be given

		-o           outfile              must be given

	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n";
###################################

my $current_dir = `pwd`;chomp($current_dir);

my $whole_genome=$opts{w};
my $in_gff=$opts{g};
my $outfile=$opts{o} || "gene.fa";

my %genome=();
&load_FA($whole_genome,\%genome);

open(OUT,">".$outfile)||die $!;
&load_gff($in_gff,\%genome,\*OUT);
close OUT;

sub load_gff{
	my ($infile,$Genome,$outfile_handle)=@_;
	my %gene = ();
	open (IN,"$infile") || die $!;
	while (<IN>) {
		chomp;
		next if (/^#/) ;
		my @line = split(/\t/);
		next if $line[2]!~/^gene$/;
		$line[-1]=~m/ID=([\w\.\-\:]+)/;
		my $gene_name = $1;
		my $len = $line[4]-$line[3]+1;
		my $cut_seq=substr($Genome->{$line[0]},$line[3],$len);
		$cut_seq=&reverse_complement($cut_seq) if ($line[6] eq "-") ;
		print $outfile_handle ">$gene_name\n",$cut_seq,"\n";
		# print $outfile_handle ">$gene_name\n",$cut_seq,"\n" if $gene_name!~/^YP_r/;
		# NC_005810.1	RefSeq	gene	21	461	.	-	.	ID=YP_0001;Name=fldA1;Note=fldA1
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
		$name =~s/\s+.+//;
		$seq=~s/\s+//g;
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