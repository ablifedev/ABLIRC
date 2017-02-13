#! /usr/bin/env perl



use strict;
use warnings;
use Data::Dumper;

my ($gff_file,$chrlen_file) = @ARGV;

my %base_tag_p = ();
my %base_tag_n = ();

my $intergenic_result_file_p = "intergenic_p";
my $intergenic_result_file_n = "intergenic_n";

open OUT_P, ">$intergenic_result_file_p" || die;
open OUT_N, ">$intergenic_result_file_n" || die;
open GFF, $gff_file ;
while (<GFF>) {
	chomp;
	next if ( $_ =~ /^#/ );
	my @line = split( /\t/, $_ );
	next if($line[2]!~/mRNA|rRNA|tRNA|transcript/);
	if($line[6] eq "+"){
		for(my $i=$line[3];$i<=$line[4];$i++){
			$base_tag_p{$line[0]}->{$i}=1;
		}
	}
	if($line[6] eq "-"){
		for(my $i=$line[3];$i<=$line[4];$i++){
			$base_tag_n{$line[0]}->{$i}=1;
		}
	}


}
close GFF;

my $start_tmp=0;
my $end_tmp=0;
my $gene_region_start=0;
my $gene_region_end=0;
my $flag = 0;
my $p_count=0;
open CHRLEN, $chrlen_file || die;
while (<CHRLEN>) {

	#chr1	201139347
	chomp;
	my ( $chr, $len ) = split /\s+/;
	for(my $j=1;$j<=$len;$j++){
		if(!defined($base_tag_p{$chr}->{$j})){
			if($flag==0){
				$start_tmp = $j;
				$flag=1;
				$gene_region_end = $j-1;
				my $len = $gene_region_end - $gene_region_start + 1;
				# print OUT_P "$chr\tGENE\t$gene_region_start\t$gene_region_end\t$len\n" if($gene_region_end!=0);
			}else{
				next if $j!=$len;
				$end_tmp = $j ;
				$flag=0;
				my $len = $end_tmp - $start_tmp + 1;
				print OUT_P "$chr\tINTERGENIC\_$p_count\_p\t$start_tmp\t$end_tmp\t+\t$len\n";
				$p_count++;
			}
		}else{
			if($flag==1){
				$end_tmp = $j - 1 ;
				$flag=0;
				$gene_region_start = $j;
				my $len = $end_tmp - $start_tmp + 1;
				print OUT_P "$chr\tINTERGENIC\_$p_count\_p\t$start_tmp\t$end_tmp\t+\t$len\n";
				$p_count++;
			}else{
				next;
			}
		}

	}

}
close CHRLEN;

$start_tmp=0;
$end_tmp=0;
$gene_region_start=0;
$gene_region_end=0;
$flag = 0;
$p_count=0;

open CHRLEN, $chrlen_file || die;
while (<CHRLEN>) {

	#chr1	201139347
	chomp;
	my ( $chr, $len ) = split /\s+/;
	for(my $j=1;$j<=$len;$j++){
		if(!defined($base_tag_n{$chr}->{$j})){
			if($flag==0){
				$start_tmp = $j;
				$flag=1;
				$gene_region_end = $j-1;
				my $len = $gene_region_end - $gene_region_start + 1;
				# print OUT_N "$chr\tGENE\t$gene_region_start\t$gene_region_end\t$len\n" if($gene_region_end!=0);
			}else{
				next if $j!=$len;
				$end_tmp = $j ;
				$flag=0;
				my $len = $end_tmp - $start_tmp + 1;
				print OUT_N "$chr\tINTERGENIC\_$p_count\_n\t$start_tmp\t$end_tmp\t-\t$len\n";
				$p_count++;
			}
		}else{
			if($flag==1){
				$end_tmp = $j - 1 ;
				$flag=0;
				$gene_region_start = $j;
				my $len = $end_tmp - $start_tmp + 1;
				print OUT_N "$chr\tINTERGENIC\_$p_count\_n\t$start_tmp\t$end_tmp\t-\t$len\n";
				$p_count++;
			}else{
				next;
			}
		}

	}

}
close CHRLEN;

close OUT_P;
close OUT_N;
undef(%base_tag_p);
undef(%base_tag_n);

`cat intergenic_p intergenic_n > intergenic.txt`;