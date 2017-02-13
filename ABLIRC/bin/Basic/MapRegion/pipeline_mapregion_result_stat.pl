#!/usr/bin/perl -w
# 
# Copyright (c)   AB_Life 2011
# Writer:         xuxiong <xuxiong19880610@163.com>
# Program Date:   2012.03.16
# Modifier:       xuxiong <xuxiong19880610@163.com>
# Last Modified:  2011.03.16
my $ver="1.0.0";

use strict;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);
use List::Util qw(first max maxstr min minstr reduce shuffle sum);

my %opts;
GetOptions(\%opts,"i=s","p=s","m=s","o=s");

if(!defined($opts{i}) || !defined($opts{p}) || !defined($opts{o}) )
{
	print <<"	Usage End.";

	Description:This programme is used for summarizing the statistics result of RNA-seq or ChIP-seq pipeline

	Example:perl $0 -i /data2/human/ChIP-seq_whu/A3_D2_H3K36me3_0319 -p _0319 -o stat_out_0319

		Version: $ver

	Usage:perl $0

    -i        indir(project directory)     must be given

    -p        postfix                     must be given

    -m        match                              ，default is "_Mapping_distribution.txt"

    -o        outfile                     must be given

	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n";
###################################
my $current_dir = `pwd`;chomp($current_dir);
#my $outdir = defined $opts{outdir} ? $opts{outdir} : "./";
#`mkdir -p $outdir` if (!-d $outdir) ;
#$outdir = "$current_dir/$outdir" if ($outdir!~/^\/|\~/) ;

my $indir=&AbsolutePath("dir",$opts{i});
my $postfix=$opts{p};
my $outfile = $opts{o};
my $match= "_Mapping_distribution.txt";
$match=$opts{m} if defined($opts{m});

my $clean_dir=(glob("$indir/clean.sh.*.qsub"))[0];

chdir($indir);
my @sample=();
&load_matched_file($indir,\@sample,"^\\S+$postfix\$");
# print "^\\S+$postfix\$";
map {$_=~s/$postfix$//g;} @sample;

my @map_region=();
# print "\n$sample[0]$postfix\n";
if (-d "$sample[0]$postfix") {
	@map_region=sort glob("$indir/*$postfix/*$match");
	# print "yes","\n";
}
else{
	&load_matched_file($indir,\@map_region,'$match$');
}
if (scalar(@sample)!=scalar(@map_region)){
	die("Some samples don't have mapping result file.");
}
my %map_region_stat=();
&read_mapped_region(\@map_region,\%map_region_stat) if (@map_region);

chdir($current_dir);
open (OUT,">$outfile") or die $!;


if (%map_region_stat) {
	print OUT join("\t",qw(Sample 5'UTR 3'UTR CDS Nc_exon Introns Intergenic Antisense)),"\n";
	for (my $i=0;$i<@{$map_region_stat{"intergenic"}};$i++) {
		$map_region_stat{"five_prime_UTR"}->[$i]=0 if (not defined $map_region_stat{"five_prime_UTR"}->[$i]) ;
		$map_region_stat{"three_prime_UTR"}->[$i]=0 if (not defined $map_region_stat{"three_prime_UTR"}->[$i]) ;
		$map_region_stat{"CDS"}->[$i]=0 if (not defined $map_region_stat{"CDS"}->[$i]) ;
		$map_region_stat{"noncoding_exon"}->[$i]=0 if (not defined $map_region_stat{"noncoding_exon"}->[$i]) ;
		$map_region_stat{"intron"}->[$i]=0 if (not defined $map_region_stat{"intron"}->[$i]) ;
		$map_region_stat{"intergenic"}->[$i]=0 if (not defined $map_region_stat{"intergenic"}->[$i]) ;
		$map_region_stat{"antisense"}->[$i]=0 if (not defined $map_region_stat{"antisense"}->[$i]) ;
		my $tmp = $sample[$i];
		$tmp=~s/\.fq$//;
		print OUT $tmp,"\t",$map_region_stat{"five_prime_UTR"}->[$i],"\t",
		$map_region_stat{"three_prime_UTR"}->[$i],"\t",$map_region_stat{"CDS"}->[$i],"\t",
		$map_region_stat{"noncoding_exon"}->[$i],"\t",$map_region_stat{"intron"}->[$i],"\t",$map_region_stat{"intergenic"}->[$i],"\t",
		$map_region_stat{"antisense"}->[$i],"\n";
	}
}
close OUT;

sub load_matched_file{
	my ($INDIR,$filenames_ref,$match)=@_;
	# print $INDIR;
	opendir(DIR,$INDIR) or die $!;
	my $tmp;
	while ($tmp=readdir(DIR)) {
		chomp $tmp;
		push @{$filenames_ref},$tmp if ($tmp=~/$match/) ;
	}
	@{$filenames_ref} = sort @{$filenames_ref};
#	print join ("\t",@{$filenames_ref}),"\n";
	close(DIR);
}

sub read_mapped_region{
	my ($file_list,$hash)=@_;
	foreach my $filename (@{$file_list}) {
		my $temp_sum=0;
		open(IN,$filename) or die $!;
		while (<IN>) {
			chomp;
			next if(/^#|^\+/);
			$temp_sum+=(split(/\s+/,$_))[1];
		}
		close IN;

		open(IN,$filename) or die $!;
		while (<IN>) {
			chomp;
			next if(/^#|^\+/);
			my @line=split(/\s+/,$_);
			push @{$hash->{$line[0]}},$line[1]."(".sprintf("%3.2f%%",$line[1]/$temp_sum*100).")";
		}
		close IN;
	}
#	print Dumper %{$hash};
}

sub AbsolutePath{
	my ($type,$input) = @_;
	my $return;
	if ($type eq 'dir'){
		my $pwd = `pwd`;
		chomp $pwd;
		chdir($input);
		$return = `pwd`;
		chomp $return;
		chdir($pwd);
	}
	elsif($type eq 'file'){
		my $pwd = `pwd`;
		chomp $pwd;
		my $dir=dirname($input);
		my $file=basename($input);
		chdir($dir);
		$return = `pwd`;
		chomp $return;
		$return .="\/".$file;
		chdir($pwd);
	}
	return $return;
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
