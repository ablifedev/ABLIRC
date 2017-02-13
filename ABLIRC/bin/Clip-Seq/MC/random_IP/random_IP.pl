#!/usr/bin/perl

# Copyright (c)   AB_Life 2011
# Writer:         xuxiong <xuxiong19880610@163.com>
# Program Date:   2011.
# Modifier:       xuxiong <xuxiong19880610@163.com>
# Last Modified:  2011.

use strict;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);
use List::Util qw(first max maxstr min minstr reduce shuffle sum);
use warnings;

#Before writing your programmeyou must write the detailed timediscriptionsparameter and it's explanation,Meanwhile,annotation your programme in English if possible.

if (scalar(@ARGV)<1) {
	print "Usage:perl $0 geneID times length tag_len1 tag_len2 ......\n";
	print "\nFor example:\n";
	print "perl $Bin/$0 AT1G01010 500 1757 24 32 21 23 21 32 20 21 32\n\n";
	exit;
}
my $Gene_id = shift @ARGV;
my $times = shift @ARGV;
my $len = shift @ARGV;
my @tag_len=@ARGV;

my $start = 0;
my $end = $len;


my %MAX_HEIGHT=();
for (my $i=0;$i<$times ;$i++) {
	my $current_max_height=&random_peak_max_height($start,$end,\@tag_len);
	$MAX_HEIGHT{$current_max_height}++;
}

print "#########################\n";
print "Gene:",$Gene_id,"\n";
my %cumulative_p_value=();
my @keys =sort {$a <=> $b} keys %MAX_HEIGHT;
my $i=0;
foreach my $key_MAX_HEIGHT (@keys ) {
	print $key_MAX_HEIGHT,"\t",$MAX_HEIGHT{$key_MAX_HEIGHT},"\t",sprintf("%2.4f",$MAX_HEIGHT{$key_MAX_HEIGHT}/$times),"\t";
	$cumulative_p_value{$key_MAX_HEIGHT}=sprintf("%2.4f",sum(map {$MAX_HEIGHT{$_}/$times} @keys[$i..$#keys]));
	$i++;
	print $cumulative_p_value{$key_MAX_HEIGHT},"\n";
}

sub random_peak_max_height{ #(\$gene_start, \$gene_end, \@random_tag_length)
	my ($gene_start,$gene_end,$ref_array)=@_;
	my %pos = ();
	for (my $i=0; $i<=$#{$ref_array}; $i++) {
		my $random_start = $gene_start+int(rand($len-$ref_array->[$i]));
		my $random_end = $random_start+$ref_array->[$i]-1;
		map {$pos{$_}++} ($random_start..$random_end);
	}
	return max(values(%pos));
}