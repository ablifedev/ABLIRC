#!/usr/bin/perl -w
#
# Copyright (c)   AB_Life 2015
# Writer:         Cheng Chao
# Program Date:   2015.
my $ver="1.0.0";

use strict;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);
use List::Util qw(first max maxstr min minstr reduce shuffle sum);

#Before writing your programme，you must write the detailed time、discriptions、parameter and it's explanation,Meanwhile,annotation your programme in English if possible.

my %opts;
GetOptions(\%opts,"exp=s","t=s","symbol=s","o=s","tpm","species","h" );

if(!defined($opts{exp}) || !defined($opts{t}))
{
	print <<"	Usage End.";

	Description:This programme is used for ~

		Version: $ver

	Usage:perl $0

		-exp               exp file         must be given

		-symbol            stat genesymbol?(0/1)                 option,default is 0(no)

		-t                 totle gene number         must be given

		-o                 outfile                   must be given

		-tpm                   TPM,   RPKM

		-species             species，   gene



	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n";
###################################

my $current_dir = `pwd`;chomp($current_dir);

my $exp_file=$opts{exp};
my $total_count=$opts{t};
my $out_file=$exp_file."_expressed_gene_stat.txt";
$out_file=$opts{o} if defined($opts{o});
my $symbol=0;
$symbol=$opts{symbol} if defined($opts{symbol});

open(OUT,">".$out_file)||die $!;


# print $sample1,"\n";
my %sample_hash=();
my $max=2;
my %rpkm=();

open(EXP,"$exp_file")||die "Can't open $exp_file\n";
while(<EXP>){
	chomp;
	my @line=split(/\t/);
	# Gene 	 Chromosome 	logConc	logFC	p.value	Tair_Gene
	if(/^Gene\s+/ or /^ID\s+/){
		for(my $i=1;$i<scalar(@line);$i++){
			last if($line[$i] =~/Symbol/i) ;
			$sample_hash{$line[$i]}=$i;
			$max=$i;
		}
		last;
	}
}
close EXP;

if($opts{tpm} && $opts{species}){
	print OUT "Sample\tTotal Species\tExpressed Species(TPM>0)(%) a\tExpressed Species(TPM>=1)(%) b\n";
	}else{
print OUT "Sample\tTotal genes in genome\tExpressed genes(RPKM>0)(%) a\tExpressed genes(RPKM>=1)(%) b\n";

	}


if($symbol==0){
	foreach my $sample (sort keys %sample_hash){
		my $num = $sample_hash{$sample} + 1;
		$num = "\$".$num;
		$rpkm{$sample}{"0"}=`more $exp_file | awk -F '\\t' '$num>0' | awk -F '\\t' '{print \$1}' | sort | uniq | wc -l`;
		chomp($rpkm{$sample}{"0"});
		$rpkm{$sample}{"0"}-=1;
		$rpkm{$sample}{"1"}=`more $exp_file | awk -F '\\t' '$num>=1' | awk -F '\\t' '{print \$1}' | sort | uniq | wc -l`;
		chomp($rpkm{$sample}{"1"});
		$rpkm{$sample}{"1"}-=1;
		print OUT $sample,"\t",$total_count,"\t",$rpkm{$sample}{"0"},"(",sprintf("%3.2f%%",$rpkm{$sample}{"0"}/$total_count*100),")\t",$rpkm{$sample}{"1"},"(",sprintf("%3.2f%%",$rpkm{$sample}{"1"}/$rpkm{$sample}{"0"}*100),")\n";
	}
}

if($symbol!=0){
	foreach my $sample (sort keys %sample_hash){
		my $num = $sample_hash{$sample} + 1;
		$num = "\$".$num;
		my $sym_num = $max+2;
		# print $sym_num,"\n";
		$sym_num = "\$".$sym_num;
		$rpkm{$sample}{"0"}=`more $exp_file | awk -F '\\t' '$num>0' | awk -F '\\t' '{print $sym_num}' | sort | uniq | wc -l`;
		chomp($rpkm{$sample}{"0"});
		$rpkm{$sample}{"0"}-=1;
		$rpkm{$sample}{"1"}=`more $exp_file | awk -F '\\t' '$num>=1' | awk -F '\\t' '{print $sym_num}' | sort | uniq | wc -l`;
		chomp($rpkm{$sample}{"1"});
		$rpkm{$sample}{"1"}-=1;
		print $rpkm{$sample}{"0"},"\n";
		# print OUT $sample,"\t",$total_count,"\t",$rpkm{$sample}{"0"},"(",sprintf("%3.2f%%",$rpkm{$sample}{"0"}/$total_count*100),")\t",$rpkm{$sample}{"1"},"(",sprintf("%3.2f%%",$rpkm{$sample}{"1"}/$rpkm{$sample}{"0"}*100),")\n";
	}
}

if($opts{tpm} && $opts{species}){
print OUT "\t\ta    species  <br>species     \tb TPM     1 species <br> TPM   0 species   \n";

	}else{
print OUT "\t\ta    gene     <br>    gene     \tb RPKM     1 gene <br> RPKM   0 gene   \n";

	}

close OUT;

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
