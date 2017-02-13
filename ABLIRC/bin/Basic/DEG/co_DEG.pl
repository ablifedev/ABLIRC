#!/usr/bin/perl -w
# 
# Copyright (c)   A_B_Life 2011
# Writer:         Chrevan Chen <dongchen@ablife.cc>
# Program Date:   2011.9.12
# Modifier:       Chrevan Chen <dongchen@ablife.cc>
# Last Modified:  2011.9.12
my $ver="1.0.0";

use strict;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);

#Before writing your programme you must write the detailed timediscriptionsparameter and it's explanation,Meanwhile,annotation your programme in English if possible.

my %opts;
GetOptions(\%opts,"i=s","h");
if ( !defined($opts{i})) {
	print <<"	Usage End.";
	Description:This programme is used for selecting the co differentially expressed genes between two DEG files

		Version: $ver

	Usage:perl $0

		-i               infile name list(SIG)                      must be given

	Usage End.
	exit;
}

my @DEG_GROUP = split(/,/,$opts{i});

my $co_gene = "_"."co_DEG.txt";		#the co-DEG outfile name
my $co_up = "_"."co_up_DEG.txt";
my $co_down = "_"."co_down_DEG.txt";

#print `pwd`;
my $co_count = 0;		#co DEG count
my @temp = ();
my $co_up_num = 0;				#co up DEG count
my $co_down_num = 0;			#co down DEG count
#my $up_down_num = 0;
#my $down_up_num = 0;
#my %gene_down = ();
#my %gene_up = ();
# Gene    logFC   logCPM  PValue  FDR     leaf    silique Symbol  Description
my %DEGUP = ();
my %DEGDOWN = ();
my %info = ();
my @basenames = ();
foreach my $sigfile (@DEG_GROUP){
	my $degbasename = basename($sigfile);
	$degbasename=~s/^_//;
	$degbasename=~s/_Sig_DEG.txt//;
	push @basenames , $degbasename;
	open (IN,"<$sigfile") || die "$sigfile:$!";		#open the first DEG file
	while (<IN>) {
		chomp; next if (/^$/);
		my @line = split("\t",$_);
		if ($_  =~ /^Gene\s+/) {		#skip the first line
			next;
		} elsif($line[1]>=0){
			$DEGUP{$line[0]} = 0 if not defined($DEGUP{$line[0]});
			$DEGUP{$line[0]}++;
			@{$info{$line[0]}{$degbasename}} = ($line[1],$line[2],$line[3],$line[4]);
		} elsif($line[1]<0){
			$DEGDOWN{$line[0]} = 0 if not defined($DEGDOWN{$line[0]});
			$DEGDOWN{$line[0]}++;
			@{$info{$line[0]}{$degbasename}} = ($line[1],$line[2],$line[3],$line[4]);
		}
	}
	close (IN);
}

my $gn = scalar(@DEG_GROUP);

open (CO,">$co_gene") || die "$co_gene:$!\n";		#to store the co differentially regulated gene
print CO "Gene";
foreach my $degbasename (@basenames){
	print CO "\t$degbasename:logFC\t$degbasename:logCPM\t$degbasename:PValue\t$degbasename:FDR";
	}
print CO "\n";
open (UP, ">$co_up") || die "$co_up:$!\n";			#to store the co up regulated gene
print UP "Gene";
foreach my $degbasename (@basenames){
	print UP "\t$degbasename:logFC\t$degbasename:logCPM\t$degbasename:PValue\t$degbasename:FDR";
	}
print UP "\n";
open (DOWN,">$co_down") || die "$co_down:$!\n";		#to store the co down regulated gene
print DOWN "Gene";
foreach my $degbasename (@basenames){
	print DOWN "\t$degbasename:logFC\t$degbasename:logCPM\t$degbasename:PValue\t$degbasename:FDR";
	}
print DOWN "\n";

foreach my $gene (sort keys %info){
	if (defined($DEGUP{$gene}) && $DEGUP{$gene} == $gn){
		$co_count++;
		print CO $gene;
		foreach my $degbasename (@basenames){
			print CO "\t",join("\t",@{$info{$gene}{$degbasename}});
		}
		print CO "\n";

		$co_up_num++;
		print UP $gene;
		foreach my $degbasename (@basenames){
			print UP "\t",join("\t",@{$info{$gene}{$degbasename}});
		}
		print UP "\n";
	}
	if (defined($DEGDOWN{$gene}) && $DEGDOWN{$gene} == $gn){
		$co_count++;
		print CO $gene;
		foreach my $degbasename (@basenames){
			print CO "\t",join("\t",@{$info{$gene}{$degbasename}});
		}
		print CO "\n";

		$co_down_num++;
		print DOWN $gene;
		foreach my $degbasename (@basenames){
			print DOWN "\t",join("\t",@{$info{$gene}{$degbasename}});
		}
		print DOWN "\n";
	}
}


close (CO);
close (UP);
close (DOWN);

print "coUp: $co_up_num\n";
print "coDown: $co_down_num\n";
