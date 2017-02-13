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
GetOptions(\%opts,"w=s","t=s","o=s","h" );

if(!defined($opts{w}) || !defined($opts{t}) || !defined($opts{o})  )
{
	print <<"	Usage End.";

	Description:This programme is used for ~
		
		Version: $ver

	Usage:perl $0

		-w           fa file         must be given

		-t           target fa file         must be given

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

my $fa=$opts{w};
my $t_fa=$opts{t};
my $outfile=$opts{o};

my @t_len=();

open(OUT,">".$outfile)||die $!;

open(TFA,"$t_fa")||die "Can't open $t_fa\n";
while(<TFA>){
	chomp;
	next if(/^>/);
	my $len = length($_);
	push @t_len,$len;
}

close TFA;

my @fa=();

open(FA,"$fa")||die "Can't open $fa\n";
$/=">";
while (<FA>) {
	chomp;
	next if (/^$/); 
	my ($name,$seq)=split(/\n/,$_,2);
	$name =~s/\s+.+//;
	$seq=~s/\s+//g;
	push @fa,$seq;
}
$/="\n";
close FA;

my $seq_num = scalar(@fa);

my $count = 0;
for(my $i=0;$i<10;$i++){
	foreach my $lenoft (@t_len){
		my $rand_gene = int(rand($seq_num));

		if(length($fa[$rand_gene])<=$lenoft){
			print OUT ">bgseq_$count\n",$fa[$rand_gene],"\n";
		}else{
			my $range = length($fa[$rand_gene])-$lenoft+1;
			my $point = int(rand($range));
			# print $point,"\n";
			my $new_seq = substr($fa[$rand_gene],$point,$lenoft);
			print OUT ">bgseq_$count\n",$new_seq,"\n";
		}

		$count++;
	}
}

close OUT;

# sub load_gff{
# 	my ($infile,$Genome,$outfile_handle)=@_;
# 	my %gene = ();
# 	open (IN,"$infile") || die $!;
# 	while (<IN>) {
# 		chomp;
# 		next if (/^#/) ;
# 		my @line = split(/\t/);
# 		next if $line[2]!~/^gene$/;
# 		$line[-1]=~m/^ID=(\S+);/;
# 		my $gene_name = $1;
# 		my $len = $line[4]-$line[3]+1;
# 		my $cut_seq=substr($Genome->{$line[0]},$line[3],$len);
# 		$cut_seq=&reverse_complement($cut_seq) if ($line[6] eq "-") ;
# 		print $outfile_handle ">$gene_name\n",$cut_seq,"\n";
# 		# print $outfile_handle ">$gene_name\n",$cut_seq,"\n" if $gene[3]!~/^YP_r/;
# 		# NC_005810.1	RefSeq	gene	21	461	.	-	.	ID=YP_0001;Name=fldA1;Note=fldA1
# 	}
# 	close(IN);
# }

# sub load_FA{
# 	my ($infile,$Len,$outfile_handle)=@_;
# 	open(FA,"$infile")||die "Can't open $infile\n";
# 	$/=">";
# 	while (<FA>) {
# 		chomp;
# 		next if (/^$/); 
# 		my ($name,$seq)=split(/\n/,$_,2);
# 		$seq=~s/\s+//g;
# 		if(length($seq)<=$Len){
# 			print $outfile_handle ">$name\n",$seq,"\n";
# 		}else{
# 			my $range = length($seq)-$Len+1;
# 			my $point = int(rand($range));
# 			print $point,"\n";
# 			my $new_seq = substr($seq,$point,$Len);
# 			print $outfile_handle ">$name\n",$new_seq,"\n";
# 		}
# 	}
# 	$/="\n";
# 	close FA;
# }

# sub reverse_complement{
# 	my $seq=shift;
# 	$seq=uc($seq);
# 	$seq=~tr/ATGC/TACG/;
# 	my $reverse_seq=reverse($seq);
# 	return $reverse_seq;
# }

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
