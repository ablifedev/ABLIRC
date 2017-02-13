#!/usr/bin/perl -w
# 
# Copyright (c)   ABLife 2011
# Writer:         Dong Chen <dongchen@ablife.cc>
# Program Date:   2012.03.16
# Modifier:       Dong Chen <dongchen@ablife.cc>
# Last Modified:  2011.03.16
my $ver="1.0.0";

use strict;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);
use List::Util qw(first max maxstr min minstr reduce shuffle sum);

my %opts;
GetOptions(\%opts,"inter=s","gff=s","o=s");

if(!defined($opts{inter})  )
{
	print STDERR  <<"	Usage End.";

	Description:This programme is used for changing the inter to gff file format
		Version: $ver

	Usage:perl $0

    -inter                  inter infile              must be given

    -gff                    gff outfile               option(inter.gff)

    -o                      outdir                    option(./)

	Usage End.

	exit;
}

my $inter = $opts{inter};
# my $gff = $opts{gff};
my $gff = defined($opts{gff}) ? $opts{gff} : "$inter\.gff";
my $outdir = defined($opts{o}) ? $opts{o} : "./";
my $i = 0;

open(IN,"<$inter") || die "Can't open $inter file!\n";
open(OUT,">$gff") || die "Can't create $gff file!\n";
while(<IN>) {
	chomp;
	next if(/^Chromosome/i);
	my @line = split("\t");
	$i++;
	print OUT $line[0],"\tABLife\tgene\t",join("\t",@line[1..2]),"\t.\t$line[3]\t0\t","ID=inter$i;Name=inter$i\n";
	print OUT $line[0],"\tABLife\ttranscript\t",join("\t",@line[1..2]),"\t.\t$line[3]\t0\t","ID=r$i;Name=r$i;Parent=inter$i\n";
	print OUT $line[0],"\tABLife\texon\t",join("\t",@line[1..2]),"\t.\t$line[3]\t0\t","ID=exon$i;Name=exon$i;Parent=r$i\n";
}
