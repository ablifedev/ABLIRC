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
GetOptions(\%opts,"peek=s","w=s","o=s","h" );

if(!defined($opts{peek}) )
{
	print <<"	Usage End.";

	Description:This programme is used for ~
		
		Version: $ver

	Usage:perl $0

		-peek        peek infile          must be given

		-w           whole genome         must be given

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

my $in_peek=$opts{peek};
my $whole_genome=$opts{w};
# my $in_gff=defined $opts{g} ? $opts{g}:"/data2/arabidopsis/TAIR10/GFF/TAIR10_GFF3_genes.gff";
my $outfile=defined $opts{o} ? $opts{o} : "$current_dir/$in_peek\_out";
# my $extend=defined $opts{e} ? $opts{e} : 0;

my %genome=();
&load_FA($whole_genome,\%genome);

open(OUT,">".$outfile)||die $!;
&load_peek($in_peek,\%genome,\*OUT);
close OUT;

sub load_peek{
	my ($infile,$Genome,$outfile_handle)=@_;
	my %gene = ();
	my $count = 0;
	my %gene_id;

	open (IN,"$infile") || die $!;
	while (<IN>) {
		chomp;
		next if (/^#/) ;
		my @line = split(/\t/);
		# print $line[0],"\t",$line[2],"\t",$line[3],"\t",$line[4],"\n";
		#NC_005810.1     83822   83902   -       81
		if($line[2] =~/^intron/){
			my $len=$line[4]-$line[3] + 1;
			# print $line[0],"\t",$line[2],"\t",$line[3],"\t",$line[4],"\n";
			my $cut_seq = substr($Genome->{$line[0]},$line[3],$len);
			my $range = join("-",$line[3],$line[4]);
			my $region = join(":",$line[0],$range);
			my $three;
			if($line[6] eq "+"){
				$three = join(" ",$region,"FORWARD");
			}elsif($line[6] eq "-"){
				$three = join(" ",$region,"REVERSE");
			}
			print $three,"\n";
			$line[8] =~ s/gene_id=(\w+\.\d+)/$1/;
			print $1,"\n";
			if(exists($gene_id{$1})){
				$gene_id{$1} = $gene_id{$1} + 1;
			}else{
				$gene_id{$1} = 1;
			}
			my $first = join("-",$1,$gene_id{$1});
			my $second = join("-",$line[3],$line[4]);
			my @title;
			push @title,$first;
			push @title,$second;
			push @title,$three;
			# push @title,$line[0];
			# push @title,@line[2..4];

			# print $cut_seq,"\n";
			# print $line[0],"\t",$line[2],"\t",$line[3],"\t",$line[4],"\n";
			# print $outfile_handle ">",join(":",@title),"\n",$cut_seq,"\n";
			print $outfile_handle ">",join(" | ",@title),"\n",$cut_seq,"\n";
		}
		# my $len = $line[4];
		# my $cut_seq=substr($Genome->{$line[0]},$line[1],$len);
		# $cut_seq=&reverse_complement($cut_seq) if ($line[3] eq "-") ;
		# print $outfile_handle ">",join(":",@line),"\n",$cut_seq,"\n";
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