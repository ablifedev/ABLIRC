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

print ">diDEG: ",join(":",@basenames),"\n";

foreach my $sigfile (@DEG_GROUP){
	my $degbasename = basename($sigfile);
	$degbasename=~s/^_//;
	$degbasename=~s/_Sig_DEG.txt//;
	my $di_up_num = 0;
	my $di_down_num = 0;
	my $di_up = "_".$degbasename."-"."di_up_DEG.txt";
	my $di_down = "_".$degbasename."-"."di_down_DEG.txt";
	open (UP, ">$di_up") || die "$di_up:$!\n";			#to store the co up regulated gene
	print UP "Gene\t$degbasename:logFC\t$degbasename:logCPM\t$degbasename:PValue\t$degbasename:FDR\n";
	open (DOWN,">$di_down") || die "$di_down:$!\n";		#to store the co down regulated gene
	print DOWN "Gene\t$degbasename:logFC\t$degbasename:logCPM\t$degbasename:PValue\t$degbasename:FDR\n";
	open (IN,"<$sigfile") || die "$sigfile:$!";		#open the first DEG file
	while (<IN>) {
		chomp; next if (/^$/);
		my @line = split("\t",$_);
		if ($_  =~ /^Gene\s+/) {		#skip the first line
			next;
		} elsif($line[1]>=0){
			if($DEGUP{$line[0]}==1){
				$di_up_num++;
				print UP join("\t",@line[0..4]),"\n";
			}
		} elsif($line[1]<0){
			if($DEGDOWN{$line[0]}==1){
				$di_down_num++;
				print DOWN join("\t",@line[0..4]),"\n";
			}
		}
	}
	close (IN);
	close UP;
	close DOWN;
	print "$degbasename di_up number: $di_up_num \n";
	print "$degbasename di_down number: $di_down_num \n";
}


