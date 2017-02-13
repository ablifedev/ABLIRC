#! /usr/bin/env perl
# remove the overlapped peaks between EZH2 and IgG


use strict;
use warnings;
use Data::Dumper;

my ($exp, $ctrl) = @ARGV;

my %ctrl = read_data($ctrl);

my %non_peak=();
my %peak;
open IN, '<', $exp or die "Cannot open experimental data $exp:$!\n";
while(<IN>){
	chomp;
	if($_=~ /^\>/){
		#chr	cluster_start	cluster_end	clusterid	length	strand	maxposition	max_depth	total_bases
		# >sensepeak_1	chr1	855563	855566	4	+	855563	3	12
		my @row = split(/\t/);
		foreach my $s (keys %{$ctrl{$row[1]}}){
			foreach my $e (keys %{$ctrl{$row[1]}{$s}}){
				foreach my $d(keys %{$ctrl{$row[1]}{$s}{$e}}){
					if( $row[5] eq $d && $row[2]==$s && $row[3] == $e){
						
						if($row[7] <= 4*$ctrl{$row[1]}{$s}{$e}{$row[5]}){
						
							$non_peak{$row[1]}{$row[2]}{$row[3]}{$row[5]}++;
						
						}
						
					}elsif($row[5] eq $d && (($s >= $row[2] && $s <= $row[3]) || ($e >= $row[2] && $e <= $row[3]) || ($row[2] >= $s && $row[2] <= $e) || ($row[3] >= $s && $row[3] <= $e))){
						
						$non_peak{$row[1]}{$row[2]}{$row[3]}{$row[5]}++;
						
						}
					}
				}
				}
			}
		
		}

close IN;

# print "Peak_ID\tCHR\tSTART\tEND\tDEPTH\tHEIGHT\tDIRECTION\n";
print "#Chr\tStart\tEnd\tPeakID\tBases\tStrand\tLength\tmaxHeight\tSummit\n";
open IN, '<', $exp or die "Cannot open experimental data $exp:$!\n";
while(<IN>){
	chomp;
	if($_=~ /^\>/){
		my @line = split(/\t/);
		$line[0]=~s/^>//;
		my $length = $line[3]-$line[2]+1;
		if (not exists $non_peak{$line[1]}{$line[2]}{$line[3]}{$line[5]}){
			#chr	cluster_start	cluster_end	clusterid	length	strand	maxposition	max_depth	total_bases
		# >sensepeak_1	chr1	855563	855566	4	+	855563	3	12
			print $line[1],"\t",$line[2],"\t",$line[3],"\t",$line[0],"\t",$line[8],"\t",$line[5],"\t",$length,"\t",$line[7],"\t",$line[6],"\n" unless (exists $peak{$line[1]}{$line[2]}{$line[3]}{$line[5]});
			$peak{$line[1]}{$line[2]}{$line[3]}{$line[5]}++;
		}
	}
	
	
}
close IN;



sub read_data{
	
	my $data=shift @_;
	
	my %hash;
	
	open (IN, '<', $data) or die "Where is the input $data:$!\n";
	
	while(<IN>){
		
		chomp;
		
		if($_=~ /^\>/){
			
			my @row= split(/\t/);
			# >chr1_378524	chr1	821725	821800	6	5	821749	-
			
			# $hash{$row[1]}{$row[2]}{$row[3]}{$row[7]}=$row[4];

			#chr	cluster_start	cluster_end	clusterid	length	strand	maxposition	max_depth	total_bases
			# >sensepeak_1	chr1	855563	855566	4	+	855563	3	12

			$hash{$row[1]}{$row[2]}{$row[3]}{$row[5]}=$row[7];
			
			
		}
		
	}
		
	close IN;
	return %hash;
}
