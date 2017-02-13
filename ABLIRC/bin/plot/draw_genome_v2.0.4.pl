#!/usr/bin/perl
my $ver = "v1.1";

# Copyright (c)   ABLife 2013
# Writer:         Cheng Chao
# Program Date:   2013.6.12
# Version:        v1.0
# Modifier:       
# Last Modified:  

use strict;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);
use List::Util qw(first max maxstr min minstr reduce shuffle sum);
use GD::Simple;
use GD;
use warnings;
use Getopt::Long;
use FileHandle;
# use threads;
# use threads::shared;
use Bio::DB::Sam;
use YAML::XS qw(DumpFile LoadFile);

#Before writing your programmeyou must write the detailed time /discriptions /parameter and it's explanation,Meanwhile,annotation your programme in English if possible.

##v1.1



##v1.2

##v1.3


##v1.4

##v1.6




my %opts;
GetOptions( \%opts, "bam=s","name=s","cluster=s","fa=s", "i=s", "l=s","bed=s","dr=s","as=s","peak=s","h" );

if (   !defined( $opts{bam} )
	|| !defined( $opts{name} )
	|| !defined( $opts{fa} )
	|| !defined( $opts{i} )
	|| !defined( $opts{cluster} )
	|| defined( $opts{h} ) )
{
	print <<"	Usage End.";

		Version:$ver

	Usage:perl $0
		-cluster         cluster                        must be given;
		-bam         bam file,ex:bam1[,bam2,bam3...]                        must be given;
		-name        sample name,ex:name1[,name2,name3]                     must be given;
		-fa          fa file                          must be given;
		-l           log depth or not (0/1)          default is 0
		-i           will it be drawn if cluster have no genes,1 for yes,0 for no     must be given;
		-bed         junctions file list, ex:bed1[,bed2,bed3...]
		-as         junctions file list, ex:as1[,as2,as3...]
		-peak         peak file list, ex:peak1[,peak2,peak3...]
		-dr          depth scale zoom in ratio, default is 1

	Usage End.

	exit;
}

#############Time_start#############
my $start_time = time();

my $Time_Start;
$Time_Start = sub_format_datetime( localtime( time() ) );
print "\nStart Time :[$Time_Start]\n\n";
####################################
my $current_dir = `pwd`;chomp($current_dir);

# my $sam_file                 = $opts{sam};
my @bamfile_group            = split(/,/,$opts{bam});
my @name_group               = split(/,/,$opts{name});
if(scalar(@bamfile_group) != scalar(@name_group)){
	print "sam file number must be same with name number!\n";
	exit;
}

my $cluster_file              = $opts{cluster};
my $fa_file                 = $opts{fa};
my $draw_intergenic_flag     = $opts{i};
my $log_flag     = 0;
$log_flag = $opts{l} if defined($opts{l});

my $depth_ratio_set = 1;
$depth_ratio_set = $opts{dr} if(defined($opts{dr}));
my $depth_ratio = $depth_ratio_set;

my $draw_peak_flag = 0;
$draw_peak_flag = 1 if(defined($opts{peak}));
my @peak_file_group = split(/,/,$opts{peak}) if(defined($opts{peak}));

my $draw_junction_flag = 0;
$draw_junction_flag = 1 if(defined($opts{bed}));
my @junction_file_group = split(/,/,$opts{bed}) if(defined($opts{bed}));

my $draw_as_flag = 0;
$draw_as_flag = 1 if(defined($opts{as}));
my @as_file_group = split(/,/,$opts{as}) if(defined($opts{as}));


#####main
my $sample_num = scalar(@bamfile_group);
my @sam = ();
for(my $s=0;$s<$sample_num;$s++){
	next if $bamfile_group[$s]=~/none$/ ;
	$sam[$s] = Bio::DB::Sam->new(-fasta=>"$fa_file",
                                 -bam  =>"$bamfile_group[$s]");
}


my %as       = ();
if($draw_as_flag==1){
	&load_as();
}

my %junction       = ();
if($draw_junction_flag==1){
	&load_junction();
}

my %peak       = ();
if($draw_peak_flag==1){
	&load_peak();
}


my $yaml_file = "$current_dir/batch_data/cluster.yaml";
my %cluster_gene=LoadFile($yaml_file);
my %batch=LoadFile($cluster_file);

my $batch_num = 0;
for(my $index=$batch{"index_start"};$index<=$batch{"index_end"};$index++){
	&run($batch{"chr"},$index);
}


sub run{
	my ($CHRO,$cluster_index) = @_;
	chdir("$current_dir/$CHRO");
	if($draw_intergenic_flag==0){
		if(@{$cluster_gene{$CHRO}->[$cluster_index]->{"gene"}}==0){
			return;
		}
	}
	my $this_cluster_start = $cluster_gene{$CHRO}->[$cluster_index]->{"cluster_start"};
	my $this_cluster_end   = $cluster_gene{$CHRO}->[$cluster_index]->{"cluster_end"};
	my $this_cluster       = $cluster_gene{$CHRO}->[$cluster_index]->{"gene"};
	my $base_name          = "$CHRO\_cluster$cluster_index\_$this_cluster_start\_$this_cluster_end.png";
	&draw($CHRO,$this_cluster,$this_cluster_start,$this_cluster_end,$base_name);
}

sub load_as {
	for(my $s=0;$s<$sample_num;$s++){
		####read as file：as
		my $start_j          = 0;
		my $end_j            = 0;
		my $as_file = $as_file_group[$s];
		open AS, $as_file || die;
# chr22   23634825        23651611        +       ES      0.03    20      576     uc002zww.3
		while (<AS>) {
			chomp;
			next if ( $_ =~ /^track/i );
			my @line = split /\t/ ;
			$start_j = $line[1];
			$end_j   = $line[2];
			my $chr= $line[0];
			my $key = "$line[0]\:$line[1]\:$line[2]";
			my $type = $line[4];
			my $modelgene = $line[-1];
			my $value="$type\:$modelgene";
			$as{$chr}->[$s]->{$key}=$value;
		}
		close AS;


		print "done reading AS $name_group[$s]...", "\n\n";
	}
}


sub load_junction {
	for(my $s=0;$s<$sample_num;$s++){
		####read junction file：bed
		my $start_j          = 0;
		my $end_j            = 0;
		my $junction_file = $junction_file_group[$s];
		open SJ, $junction_file || die;

		while (<SJ>) {

			#chr20   199843  204678  JUNC00000001    24      -       199843  204678  255,0,0 2       65,70   0,4765
			#chr20   275722  276146  JUNC00000015    3       +       275722  276146  255,0,0 2       64,69   0,355
			chomp;
			next if ( $_ =~ /^track/i );
			my ( $chr, $left, $right, $feature, $readsNum, $strand, $thickStart, $thickEnd, 
				$itemRgb, $blockCount, $blockSizes, $blockStarts) = split /\t/ ;
			my ( $leftsize, $rightsize ) = ( split /\,/, $blockSizes )[ 0 .. 1 ];
			$start_j = $left + $leftsize;
			$end_j   = $right - $rightsize + 1;
			my $key = "$chr\:$start_j\:$end_j";
			my $asvalue="";
			if(defined($as{$chr}->[$s]->{$key})){
				$asvalue=$as{$chr}->[$s]->{$key};
			}
			if ( !defined( $junction{$chr}->[$s]->{$strand}->{$start_j} ) ) {
				$junction{$chr}->[$s]->{$strand}->{$start_j} = "$end_j\-$readsNum\-$asvalue";
			}else{
				$junction{$chr}->[$s]->{$strand}->{$start_j} .= "\t$end_j\-$readsNum\-$asvalue";
			}
		}
		close SJ;


		print "done reading SJ $name_group[$s]...", "\n\n";
	}
}

sub load_peak {
	for(my $s=0;$s<$sample_num;$s++){
		####read peak file：bed
		my $start_j          = 0;
		my $end_j            = 0;
		my $peak_file = $peak_file_group[$s];
		next if $peak_file eq "none";
		my %peakid=();
		open PEAK, $peak_file || die;

		while (<PEAK>) {

			#chr1	21102083	21102150	3	3	+
			chomp;
			next if ( $_ =~ /^#/i );
            my @line = split(/\t/);
			my ( $chr, $left, $right, $id, $other1, $strand) = @line[0..5] ;
			my $key="$chr\_$left\_$right\_$strand\_$id";
			next if defined($peakid{$key});
			$peakid{$key}=1;
			# my ( $chr, $id, $left, $right, $strand, $other1) = split /\t/ ;
			# $id=~s/^>//;
			$start_j = $left;
			$end_j   = $right;

			if ( !defined( $peak{$chr}->[$s]->{$strand}->{$start_j} ) ) {
				$peak{$chr}->[$s]->{$strand}->{$start_j} = "$end_j\-$key";
			}else{
				$peak{$chr}->[$s]->{$strand}->{$start_j} .= "\t$end_j\-$key";
			}
		}
		close PEAK;


		print "done reading PEAK $name_group[$s]...", "\n\n";
	}
}

# sub load_as {
# 	for(my $s=0;$s<$sample_num;$s++){
# 		####read as file：as
# 		my $start_j          = 0;
# 		my $end_j            = 0;
# 		my $as_file = $as_file_group[$s];
# 		open AS, $as_file || die;
# # chr22   23634825        23651611        +       ES      0.03    20      576     uc002zww.3
# 		while (<AS>) {
# 			chomp;
# 			next if ( $_ =~ /^track/i );
# 			my @line = split /\t/ ;
# 			$start_j = $line[1];
# 			$end_j   = $line[2];
# 			my $chr= $line[0];
# 			my $strand = $line[3];
# 			my $type = $line[4];
# 			my $modelgene = $line[-1];
# 			if ( !defined( $as{$chr}->[$s]->{$start_j} ) ) {
# 				$as{$chr}->[$s]->{$start_j} = "$end_j\:$type\:$modelgene";
# 			}else{
# 				$as{$chr}->[$s]->{$start_j} .= "\t$end_j\:$type\:$modelgene";
# 			}
# 		}
# 		close AS;


# 		print "done reading AS $name_group[$s]...", "\n\n";
# 	}
# }

sub draw {
	my ($chr,$cluster,$Cluster_start,$Cluster_end,$BASE_NAME)=@_;
	open (OUT,">$BASE_NAME") or die $!;
	
	##load this cluster reads and count depth
	my %base_p = ();    #positive
	my %base_n = ();    #negative
	my $left_block  = 0;
	my $middle_block= 0;
	my $right_block = 0;
	my $len = 0;
	for(my $s=0;$s<$sample_num;$s++){
		next if $bamfile_group[$s]=~/none$/ ;
		my @alignments = $sam[$s]->get_features_by_location(-seq_id => $chr,
                                                            -start  => $Cluster_start,
                                                            -end    => $Cluster_end);
		for my $a (@alignments) {
			# print $a,"\n";
			my $seqname  = $a->name;
			my $start  = $a->start;
			my $end    = $a->end;
			my $strand = $a->strand;
			# print $seqid,"\n";
			# if($seqname=~/\#\w+:2$/){
			# 	$strand=0-$strand;
			# 	# print $seqid,"\n";
			# }
			my $cigar     = $a->cigar_str;
			next if ( $cigar !~ /^\d+M$/ && $cigar !~ /\d+M\d+N\d+M/ && $cigar !~ /\d+M\d+D\d+M/ && $cigar !~ /\d+M\d+I\d+M/);
			# next if $cigar =~ /^\d+M\d+N\d+M$/;
			

			# if($draw_junction_flag==1){
			# 	next if $cigar =~ /^\d+M\d+N\d+M$/;
			# }

			# print "$chr\t$start\t$end\t$strand\n";

			# if($strand==1){
			# 	for(my $i=$start;$i<=$end;$i++){
			# 		$base_p{$chr}->{$s}->{$i} = 0 if not defined($base_p{$chr}->{$s}->{$i});
			# 		$base_p{$chr}->{$s}->{$i} ++; 
			# 	}
			# }else{
			# 	for(my $i=$start;$i<=$end;$i++){
			# 		$base_n{$chr}->{$s}->{$i} = 0 if not defined($base_n{$chr}->{$s}->{$i});
			# 		$base_n{$chr}->{$s}->{$i} ++; 
			# 	}
			# }

			if($strand==1){
				if($cigar =~ m/^(\d+)M$/){
					$len = $1;

					for ( my $i = $start ; $i < $start + $len ; $i++ ) {
						$base_p{$chr}->{$s}->{$i} = 0 if not defined($base_p{$chr}->{$s}->{$i});
						$base_p{$chr}->{$s}->{$i} ++; 
					}
				}elsif($cigar =~ /(\d+)M(\d+)N(\d+)M/){
					$left_block = $1;
					$middle_block = $2;
					$right_block = $3;
					for ( my $i = $start ; $i < $start + $left_block ; $i++ ) {
						$base_p{$chr}->{$s}->{$i} = 0 if not defined($base_p{$chr}->{$s}->{$i});
						$base_p{$chr}->{$s}->{$i} ++; 
					}
					for ( my $i = $start + $left_block + $middle_block ; $i < $start + $left_block + $middle_block + $right_block ; $i++ ) {
						$base_p{$chr}->{$s}->{$i} = 0 if not defined($base_p{$chr}->{$s}->{$i});
						$base_p{$chr}->{$s}->{$i} ++; 
					}
				}elsif($cigar =~ /(\d+)M(\d+)I(\d+)M/){
					$left_block = $1;
					$middle_block = $2;
					$right_block = $3;
					for ( my $i = $start ; $i < $start + $left_block + $right_block ; $i++ ) {
						$base_p{$chr}->{$s}->{$i} = 0 if not defined($base_p{$chr}->{$s}->{$i});
						$base_p{$chr}->{$s}->{$i} ++; 
					}
				}elsif($cigar =~ /(\d+)M(\d+)D(\d+)M/){
					$left_block = $1;
					$middle_block = $2;
					$right_block = $3;
					for ( my $i = $start ; $i < $start + $left_block ; $i++ ) {
						$base_p{$chr}->{$s}->{$i} = 0 if not defined($base_p{$chr}->{$s}->{$i});
						$base_p{$chr}->{$s}->{$i} ++; 
					}
					for ( my $i = $start + $left_block + $middle_block ; $i < $start + $left_block + $middle_block + $right_block ; $i++ ) {
						$base_p{$chr}->{$s}->{$i} = 0 if not defined($base_p{$chr}->{$s}->{$i});
						$base_p{$chr}->{$s}->{$i} ++; 
					}
				}
			}else{
				if($cigar =~ m/^(\d+)M$/){
					$len = $1;

					for ( my $i = $start ; $i < $start + $len ; $i++ ) {
						$base_n{$chr}->{$s}->{$i} = 0 if not defined($base_n{$chr}->{$s}->{$i});
						$base_n{$chr}->{$s}->{$i} ++; 
					}
				}elsif($cigar =~ /(\d+)M(\d+)N(\d+)M/){
					$left_block = $1;
					$middle_block = $2;
					$right_block = $3;
					for ( my $i = $start ; $i < $start + $left_block ; $i++ ) {
						$base_n{$chr}->{$s}->{$i} = 0 if not defined($base_n{$chr}->{$s}->{$i});
						$base_n{$chr}->{$s}->{$i} ++; 
					}
					for ( my $i = $start + $left_block + $middle_block ; $i < $start + $left_block + $middle_block + $right_block ; $i++ ) {
						$base_n{$chr}->{$s}->{$i} = 0 if not defined($base_n{$chr}->{$s}->{$i});
						$base_n{$chr}->{$s}->{$i} ++; 
					}
				}elsif($cigar =~ /(\d+)M(\d+)I(\d+)M/){
					$left_block = $1;
					$middle_block = $2;
					$right_block = $3;
					for ( my $i = $start ; $i < $start + $left_block + $right_block ; $i++ ) {
						$base_n{$chr}->{$s}->{$i} = 0 if not defined($base_n{$chr}->{$s}->{$i});
						$base_n{$chr}->{$s}->{$i} ++; 
					}
				}elsif($cigar =~ /(\d+)M(\d+)D(\d+)M/){
					$left_block = $1;
					$middle_block = $2;
					$right_block = $3;
					for ( my $i = $start ; $i < $start + $left_block ; $i++ ) {
						$base_n{$chr}->{$s}->{$i} = 0 if not defined($base_n{$chr}->{$s}->{$i});
						$base_n{$chr}->{$s}->{$i} ++; 
					}
					for ( my $i = $start + $left_block + $middle_block ; $i < $start + $left_block + $middle_block + $right_block ; $i++ ) {
						$base_n{$chr}->{$s}->{$i} = 0 if not defined($base_n{$chr}->{$s}->{$i});
						$base_n{$chr}->{$s}->{$i} ++; 
					}
				}
			}



		}
	}

	$depth_ratio = $depth_ratio_set;

	my $left=350;
	my $top=100;
	my $scale=1;
	my $scale_height=5000;
	my $scale_width=8000;
	my $Width=$scale_width/$scale+2*$left;

	my $cluster_Length=abs($Cluster_end-$Cluster_start);
	my $ratio=$scale_width/$cluster_Length;

	my $RNA_line_height=0.02;
	my $depth_height=0.0006;
	# if($duplicates_filter_flag!=1){$depth_height=0.0003;}
	
	my $RNA_count=sum(map {$#{$_}} @{$cluster});
	# print "RNA-COUNT:$RNA_count\n";

	my @max_depth_p = ();
	my @max_depth_n = ();
	my $total_depth = 0;
	for(my $sa=0;$sa<$sample_num;$sa++){
		$max_depth_p[$sa] = &max_depth($chr,$Cluster_start,$Cluster_end,$sa,\%base_p);
		$total_depth+=$max_depth_p[$sa];
		$max_depth_n[$sa] = &max_depth($chr,$Cluster_start,$Cluster_end,$sa,\%base_n);
		$total_depth+=$max_depth_n[$sa];
	}

	if($total_depth>2000){
		$depth_ratio=$depth_ratio/($total_depth/2000);
	}


	$depth_height = $depth_height * $depth_ratio;

	### count RNA_index number
	my $RNA_index=0;
	my $temp_end=10e10;

	foreach my $temp_gene (@{$cluster}) {
		foreach my $temp_RNA (@{$temp_gene}) {
			next if ($temp_RNA->[0]->[2]=~/^gene|pseudogene|transposable_element_gene$/) ;
			$RNA_index-- if ($temp_RNA->[0]->[3] > $temp_end+100*$scale/$ratio) ;
			$RNA_index++;
			$temp_end = $temp_RNA->[-1]->[4];
		}
	}
	# print "RNA-INDEX:$RNA_index\n";

	my $Height=($RNA_index*$RNA_line_height+($total_depth+10)*$depth_height+0.11+0.04*$sample_num)*$scale_height/$scale+2*$top+$top;
	my $img = GD::Simple->new($Width,$Height);

	# print "$Height\n";
	# my $img = new GD::Image($Width,$Height);

	$img->font(gdSmallFont);
	my @rgb=();
	my $index;



	#############draw_RNA_frame##################
	@rgb=(234,255,234);
	$index = $img->translate_color(@rgb);
	$img->fgcolor($index);
	$img->bgcolor($index);
	$img->penSize(1,1);
	$img->rectangle(0,0,$left*2+$scale_width/$scale,$top+$top+$RNA_line_height*$RNA_index*$scale_height/$scale);
	# print "done draw RNA_frame\n";
	#############draw grid#####################
	$img->penSize(3,3);
	my $count = 0;

	for (my $i=$Cluster_start;$i<=$Cluster_end ;$i+=int($cluster_Length*0.01)) {
		if($count%10==0){
			$img->penSize(2,2);
			@rgb=(255,180,180);
			$index = $img->translate_color(@rgb);
			$img->fgcolor($index);
			$img->moveTo($left+($i-$Cluster_start)*$ratio/$scale,0);
			$img->lineTo($left+($i-$Cluster_start)*$ratio/$scale,$Height);
			$count++;
		}else{
			@rgb=(222,222,255);
			$index = $img->translate_color(@rgb);
			$img->fgcolor($index);
			$img->moveTo($left+($i-$Cluster_start)*$ratio/$scale,0);
			$img->lineTo($left+($i-$Cluster_start)*$ratio/$scale,$Height);
			$count++;
		}
	}
	# print "done draw grid\n";

	$img->fontsize(40);
	$RNA_index=0;
	$temp_end=10e10;

	foreach my $temp_gene (@{$cluster}) {
#		foreach my $temp_RNA (@{$temp_gene}[1..$#{$temp_gene}]) {
		foreach my $temp_RNA (@{$temp_gene}) {
#			next if ($temp_RNA->[0]->[2]=~/^mRNA|miRNA|mRNA_TE_gene|ncRNA|pseudogenic_transcript|rRNA|snoRNA|snRNA|tRNA|transcript$/) ;
			next if ($temp_RNA->[0]->[2]=~/^gene|pseudogene|transposable_element_gene$/) ;
				if ($temp_RNA->[0]->[6] eq "+"){
					@rgb=(140,0,130);
					$index = $img->translate_color(@rgb);
					$img->fgcolor($index);
					@rgb=(140,0,130);
					$index = $img->translate_color(@rgb);
					$img->bgcolor($index);
				}else{
					@rgb=(1,1,118);
					$index = $img->translate_color(@rgb);
					$img->fgcolor($index);
					@rgb=(1,1,118);
					$index = $img->translate_color(@rgb);
					$img->bgcolor($index);
				}
			$RNA_index-- if ($temp_RNA->[0]->[3] > $temp_end+100*$scale/$ratio) ;
			$img->penSize(5,5);
			######draw RNA information###########
			# $img->fgcolor('blue');
			$img->moveTo($left+($temp_RNA->[0]->[3]-$Cluster_start)*$ratio/$scale,$top+($RNA_line_height*$RNA_index+0.009)*$scale_height/$scale);
			$img->angle(0);
			$img->font('Times:italic');
			# $img->string(join(":",@{$temp_RNA->[0]}[-1,3,4]));
			$img->string(@{$temp_RNA->[0]}[-1]);
			######draw mRNA|ncRNA length#########
			# $img->fgcolor('blue');
			$img->penSize(3,3);
			$img->line($left+($temp_RNA->[0]->[3]-$Cluster_start)*$ratio/$scale,$top+($RNA_line_height*$RNA_index+0.015)*$scale_height/$scale,$left+($temp_RNA->[0]->[4]-$Cluster_start)*$ratio/$scale,$top+($RNA_line_height*$RNA_index+0.015)*$scale_height/$scale);

			######draw each CDS|three_prime_UTR|five_prime_UTR|ncExon########
			foreach my $temp_exon (@{$temp_RNA}[1..$#{$temp_RNA}]) {
				# print join("\t",@{$temp_exon}),"\n";
				$img->penSize(1,1);
				my $utr_heigth = 0;
				next if ($temp_exon->[2]=~/^intron$/) ;
				if ($temp_RNA->[0]->[2]=~/^mRNA$/) {
					next if ($temp_exon->[2]=~/^exon|start_codon|stop_codon$/) ;
				}
				if ($temp_exon->[2]=~/^three_prime_UTR|five_prime_UTR$/) {
					# print $temp_exon->[2],"\n";
					$utr_heigth = 0.002;
				}else {
					# print $temp_exon->[2],"\n";
					$utr_heigth = 0;
				}
				my $exon_x1=int(($temp_exon->[3]-$Cluster_start)*$ratio/$scale+0.5);
				my $exon_x2=int(($temp_exon->[4]-$Cluster_start)*$ratio/$scale+0.5);
				# print $left+$exon_x1,"\t",$top+($RNA_line_height*$RNA_index+0.01+$utr_heigth)*$scale_height/$scale,"\t",$left+$exon_x2,"\t",$top+($RNA_line_height*$RNA_index+0.02-$utr_heigth)*$scale_height/$scale,"\n";
				$img->rectangle($left+$exon_x1,$top+($RNA_line_height*$RNA_index+0.01+$utr_heigth)*$scale_height/$scale,$left+$exon_x2,$top+($RNA_line_height*$RNA_index+0.02-$utr_heigth)*$scale_height/$scale);
			}
			#####mark the transcript direction#####
			if ($temp_RNA->[0]->[6] eq "+") {
				@rgb=(140,0,130);
				$index = $img->translate_color(@rgb);
				$img->fgcolor($index);
				$img->bgcolor($index);
				$img->penSize(1,1);
				my $poly = new GD::Polygon;
				$poly->addPt($left+($temp_RNA->[0]->[4]-$Cluster_start)*$ratio/$scale,$top+($RNA_line_height*$RNA_index+0.01)*$scale_height/$scale);
				$poly->addPt($left+($temp_RNA->[0]->[4]-$Cluster_start)*$ratio/$scale+15,$top+($RNA_line_height*$RNA_index+0.015)*$scale_height/$scale);
				$poly->addPt($left+($temp_RNA->[0]->[4]-$Cluster_start)*$ratio/$scale,$top+($RNA_line_height*$RNA_index+0.02)*$scale_height/$scale);
				$img->polygon($poly);
			}else{
				@rgb=(1,1,118);
				$index = $img->translate_color(@rgb);
				$img->fgcolor($index);
				$img->bgcolor($index);
				$img->penSize(1,1);
				my $poly = new GD::Polygon;
				$poly->addPt($left+($temp_RNA->[0]->[3]-$Cluster_start)*$ratio/$scale,$top+($RNA_line_height*$RNA_index+0.01)*$scale_height/$scale);
				$poly->addPt($left+($temp_RNA->[0]->[3]-$Cluster_start)*$ratio/$scale-15,$top+($RNA_line_height*$RNA_index+0.015)*$scale_height/$scale);
				$poly->addPt($left+($temp_RNA->[0]->[3]-$Cluster_start)*$ratio/$scale,$top+($RNA_line_height*$RNA_index+0.02)*$scale_height/$scale);
				$img->polygon($poly);
			}
			$RNA_index++;
			$temp_end = $temp_RNA->[-1]->[4];
		}
	}

	# print "done draw RNA\n";

	#############draw x-axis#####################
	$img->penSize(5,5);
	@rgb=(0,0,139);
	$index = $img->translate_color(@rgb);
	$img->fgcolor($index);
	# $img->fgcolor('darkblue');
	# print "pass\n";
	$img->angle(0);
	my $locate=$RNA_line_height*$RNA_index+0.02+$top*$scale/$scale_height;


	$img->moveTo($left-220,$top+0.5*$RNA_line_height*$RNA_index*$scale_height/$scale);
	$img->fontsize(50);
	$img->font('Times:italic');
	$img->string("Genes");

	$img->moveTo($left-300,$top+$locate*$scale_height/$scale-25);
	$img->fontsize(35);
	$img->font('Times:italic');
	$img->string("Scale\n$chr");

	@rgb=(0,0,0);
	$index = $img->translate_color(@rgb);
	$img->fgcolor($index);
	# $img->fgcolor('black');
	$count = 0;

	for (my $i=$Cluster_start;$i<=$Cluster_end ;$i+=int($cluster_Length*0.01)) {
		if($count%10==0){
			$img->moveTo($left+($i-$Cluster_start)*$ratio/$scale,$top+$locate*$scale_height/$scale);
			$img->lineTo($left+($i-$Cluster_start)*$ratio/$scale,$top+($locate-0.01)*$scale_height/$scale);
			$img->moveTo($left+($i-$Cluster_start)*$ratio/$scale-10,$top+($locate+0.015)*$scale_height/$scale);
			$img->angle(0);
	#		$img->fontsize(40);
			$img->font('Times:italic');
			$img->string($i);
			$count++;
		}else{
			$img->moveTo($left+($i-$Cluster_start)*$ratio/$scale,$top+$locate*$scale_height/$scale);
			$img->lineTo($left+($i-$Cluster_start)*$ratio/$scale,$top+($locate-0.005)*$scale_height/$scale);
			$count++;
		}
	}
	$img->moveTo($left,$top+$locate*$scale_height/$scale);
	$img->lineTo($left+$cluster_Length*$ratio/$scale,$top+$locate*$scale_height/$scale);

	# print "done draw x-axis\n";

	$locate+=0.015;

	for(my $sa=0;$sa<$sample_num;$sa++){
		############draw depth ######################
		# print "x border:",$top+$locate*$scale_height/$scale,"\n";
		my $gap_axis_depth = 0.04;

		##draw x-axis
		# print "$max_depth_p\t$max_depth_n\n";
		my $zero_depth_locate = $locate + $gap_axis_depth + $max_depth_p[$sa]*$depth_height;
		$locate = $zero_depth_locate + $max_depth_n[$sa]*$depth_height;
		$img->moveTo($left,$top+$zero_depth_locate*$scale_height/$scale);
		@rgb=(0,128,0);
		$index = $img->translate_color(@rgb);
		$img->fgcolor($index);
		# $img->fgcolor('green');
		$img->penSize(1,1);
		$img->lineTo($left+$cluster_Length*$ratio/$scale,$top+$zero_depth_locate*$scale_height/$scale);


		##draw y-axis
		@rgb=(0,0,0);
		$index = $img->translate_color(@rgb);
		$img->fgcolor($index);
		# $img->fgcolor('black');
		$img->penSize(3,3);
		my $tmp_count = 0;

		for (my $k=$zero_depth_locate;$k>=$zero_depth_locate-$max_depth_p[$sa]*$depth_height;$k-=3*$depth_height/$depth_ratio) {
			$img->moveTo($left-80,$top+$k*$scale_height/$scale);
			$img->angle(180);
			$img->line(15);
			if($tmp_count%5==0){
				$img->line(10);
				$img->moveTo($left-210,$top+($k+0.003)*$scale_height/$scale);
				$img->angle(0);
				$img->fontsize(40);
				$img->font('Times:italic');
				$img->string(int(($zero_depth_locate-$k)/$depth_height+0.5));
			}
			$tmp_count++;
		}
		$img->moveTo($left-60,$top+$zero_depth_locate*$scale_height/$scale-30);
		$img->angle(0);
		$img->fontsize(50);
		$img->font('Times:italic');
		$img->string("+");

		$tmp_count = 1;
		for (my $k=$zero_depth_locate+3*$depth_height/$depth_ratio;$k<=$zero_depth_locate+$max_depth_n[$sa]*$depth_height;$k+=3*$depth_height/$depth_ratio) {
			$img->moveTo($left-80,$top+$k*$scale_height/$scale);
			$img->angle(180);
			$img->line(15);
			if($tmp_count%5==0){
				$img->line(10);
				$img->moveTo($left-210,$top+($k+0.003)*$scale_height/$scale);
				$img->angle(0);
				$img->fontsize(40);
				$img->font('Times:italic');
				$img->string(int(($k-$zero_depth_locate)/$depth_height+0.5));
			}
			$tmp_count++;
		}
		$img->moveTo($left-50,$top+$zero_depth_locate*$scale_height/$scale+50);
		$img->angle(0);
		$img->fontsize(50);
		$img->font('Times:italic');
		$img->string("-");

		$img->moveTo($left-80,$top+$zero_depth_locate*$scale_height/$scale);
		$img->angle(90);
		$img->line($max_depth_n[$sa]*$depth_height*$scale_height/$scale);
		$img->moveTo($left-80,$top+$zero_depth_locate*$scale_height/$scale);
		$img->angle(270);
		$img->line($max_depth_p[$sa]*$depth_height*$scale_height/$scale);
		$img->angle(0);


		$img->penSize(5,5);
		@rgb=(0,0,139);
		$index = $img->translate_color(@rgb);
		$img->fgcolor($index);
		# $img->fgcolor('darkblue');
		$img->angle(0);
		$img->moveTo($Width-$left,$top+$zero_depth_locate*$scale_height/$scale-100);
		$img->fontsize(40);
		$img->font('Times:italic');
		$img->string($name_group[$sa]);

		##draw depth
		my $maxdepth=0;
		for(my $j=$Cluster_start;$j<=$Cluster_end;$j++){
			my $start_x=$left+($j-$Cluster_start)*$ratio/$scale;
			my $start_y=$top+$zero_depth_locate*$scale_height/$scale;
			my $thisdepth_p = $base_p{$chr}->{$sa}->{$j};
			my $thisdepth_n = $base_n{$chr}->{$sa}->{$j};
			my $end_y_p = $top+($zero_depth_locate-$thisdepth_p*$depth_height)*$scale_height/$scale;
			my $end_y_n = $top+($zero_depth_locate+$thisdepth_n*$depth_height)*$scale_height/$scale;

			$img->penSize(2,2);


			@rgb=(255,186,250);
			@rgb=(255,102,102) if $name_group[$sa]=~/RIP/i;
			$index = $img->translate_color(@rgb);
			$img->fgcolor($index);
			$img->moveTo($start_x,$start_y);
			$img->lineTo($start_x,$end_y_p);

			@rgb=(127,127,254);
			@rgb=(0,102,204) if $name_group[$sa]=~/RIP/i;


			$index = $img->translate_color(@rgb);
			$img->fgcolor($index);
			$img->moveTo($start_x,$start_y);
			$img->lineTo($start_x,$end_y_n);


			if($thisdepth_p+$thisdepth_n>$maxdepth){
				$maxdepth=$thisdepth_p+$thisdepth_n;
			}
		}
		if($maxdepth>20){
			print $BASE_NAME,"\t$maxdepth\n";
		}
		# print "done draw depth\n";

		##draw junctions
		if($draw_junction_flag==1){
			my $floor_height = 0.01;
			my @floor_p = ();
			my @floor_n = ();
			$floor_p[0]=0;
			$floor_n[0]=0;
			for(my $j=$Cluster_start;$j<=$Cluster_end;$j++){
				if(defined($junction{$chr}->[$sa]->{"+"}->{$j})){
					$img->penSize(3,3);

					# @rgb=(0,140,94);

					@rgb=(222,49,99);
					$index = $img->translate_color(@rgb);
					$img->fgcolor($index);
					$img->bgcolor(undef);

					my @start_junction = split /\s+/, $junction{$chr}->[$sa]->{"+"}->{$j};
					foreach my $i (@start_junction) {
						my ( $j_e, $j_r,$j_as ) = split /\-/, $i;
						next if $j_r<2;
						my $floor_noadd_flag = 0;
						my $j_floor = 0;
						my $floor=0;
						for($floor=0;$floor<@floor_p;$floor++){
							if($j>=$floor_p[$floor]){
								$j_floor = $floor;
								$floor_p[$floor] = $j_e;
								$floor_noadd_flag = 1;
							}
						}
						if($floor_noadd_flag == 0){
							$j_floor = $floor;
							$floor_p[$floor] = $j_e;
						}
						my $j_s = $j;
						my $j_m = int(($j_e - $j_s)/2) + $j_s;
						my $j_s_x = $left+($j_s-$Cluster_start)*$ratio/$scale;
						my $j_s_y = $top+($zero_depth_locate-$j_floor*$floor_height-0.003)*$scale_height/$scale;
						my $j_e_x = $left+($j_e-$Cluster_start)*$ratio/$scale;
						my $j_e_y = $top+($zero_depth_locate-$j_floor*$floor_height-0.003)*$scale_height/$scale;
						my $cx = $left+($j_m-$Cluster_start)*$ratio/$scale;
						my $cy = $top+($zero_depth_locate-$j_floor*$floor_height-0.003)*$scale_height/$scale;
						$img->line($j_s_x,$j_s_y-0.007*$scale_height/$scale,$j_s_x,$j_s_y+0.003*$scale_height/$scale);
						$img->line($j_e_x,$j_e_y-0.007*$scale_height/$scale,$j_e_x,$j_e_y+0.003*$scale_height/$scale);
						$img->line($j_s_x,$j_s_y,$j_e_x,$j_e_y);
						#junction reads num
						$img->moveTo($cx-25,$cy);
						$img->angle(0);
						$img->fontsize(30);
						$img->font('Times:bold');
						$img->string("$j_r $j_as");
					}
				}
				if(defined($junction{$chr}->[$sa]->{"-"}->{$j})){
					$img->penSize(3,3);

					# @rgb=(120,0,98);
					# @rgb=(193,140,0);

					@rgb=(0,117,94);
					$index = $img->translate_color(@rgb);
					$img->fgcolor($index);
					$img->bgcolor(undef);
					
					my @start_junction = split /\s+/, $junction{$chr}->[$sa]->{"-"}->{$j};
					foreach my $i (@start_junction) {
						my ( $j_e, $j_r,$j_as ) = split /\-/, $i;
						next if $j_r<2;
						my $floor_noadd_flag = 0;
						my $j_floor = 0;
						my $floor=0;
						for($floor=0;$floor<@floor_n;$floor++){
							if($j>=$floor_n[$floor]){
								$j_floor = $floor;
								$floor_n[$floor] = $j_e;
								$floor_noadd_flag = 1;
							}
						}
						if($floor_noadd_flag == 0){
							$j_floor = $floor;
							$floor_n[$floor] = $j_e;
						}
						my $j_s = $j;
						my $j_m = int(($j_e - $j_s)/2) + $j_s;
						my $j_s_x = $left+($j_s-$Cluster_start)*$ratio/$scale;
						my $j_s_y = $top+($zero_depth_locate+$j_floor*$floor_height+0.003)*$scale_height/$scale;
						my $j_e_x = $left+($j_e-$Cluster_start)*$ratio/$scale;
						my $j_e_y = $top+($zero_depth_locate+$j_floor*$floor_height+0.003)*$scale_height/$scale;
						my $cx = $left+($j_m-$Cluster_start)*$ratio/$scale;
						my $cy = $top+($zero_depth_locate+$j_floor*$floor_height+0.01)*$scale_height/$scale;
						$img->line($j_s_x,$j_s_y-0.003*$scale_height/$scale,$j_s_x,$j_s_y+0.007*$scale_height/$scale);
						$img->line($j_e_x,$j_e_y-0.003*$scale_height/$scale,$j_e_x,$j_e_y+0.007*$scale_height/$scale);
						$img->line($j_s_x,$j_s_y,$j_e_x,$j_e_y);
						#junction reads num
						$img->moveTo($cx-25,$cy);
						$img->angle(0);
						$img->fontsize(30);
						$img->font('Times:bold');
						$img->string("$j_r $j_as");
					}
				}
			}
		}

		##draw peak
		if($draw_peak_flag==1){
			my $floor_height = 0.02;
			my @floor_p = ();
			my @floor_n = ();
			$floor_p[0]=0;
			$floor_n[0]=0;
			for(my $j=$Cluster_start;$j<=$Cluster_end;$j++){
				if(defined($peak{$chr}->[$sa]->{"+"}->{$j})){
					$img->penSize(5,5);

					# @rgb=(0,140,94);


					@rgb=(0,117,94);
					$index = $img->translate_color(@rgb);
					$img->fgcolor($index);
					$img->bgcolor(undef);

					my @start_peak = split /\s+/, $peak{$chr}->[$sa]->{"+"}->{$j};
					foreach my $i (@start_peak) {
						my ( $j_e, $j_r ) = split /\-/, $i;

						my $floor_noadd_flag = 0;
						my $j_floor = 0;
						my $floor=0;
						for($floor=0;$floor<@floor_p;$floor++){
							if($j>=$floor_p[$floor]){
								$j_floor = $floor;
								$floor_p[$floor] = $j_e;
								$floor_noadd_flag = 1;
							}
						}
						if($floor_noadd_flag == 0){
							$j_floor = $floor;
							$floor_p[$floor] = $j_e;
						}
						my $j_s = $j;
						my $j_m = int(($j_e - $j_s)/2) + $j_s;
						my $j_s_x = $left+($j_s-$Cluster_start)*$ratio/$scale;
						my $j_s_y = $top+($zero_depth_locate-$j_floor*$floor_height-0.003)*$scale_height/$scale;
						my $j_e_x = $left+($j_e-$Cluster_start)*$ratio/$scale;
						my $j_e_y = $top+($zero_depth_locate-$j_floor*$floor_height-0.003)*$scale_height/$scale;
						my $cx = $left+($j_m-$Cluster_start)*$ratio/$scale;
						my $cy = $top+($zero_depth_locate-$j_floor*$floor_height-0.003)*$scale_height/$scale;
						$img->line($j_s_x,$j_s_y-0.007*$scale_height/$scale,$j_s_x,$j_s_y+0.003*$scale_height/$scale);
						$img->line($j_e_x,$j_e_y-0.007*$scale_height/$scale,$j_e_x,$j_e_y+0.003*$scale_height/$scale);
						$img->line($j_s_x,$j_s_y,$j_e_x,$j_e_y);
						#peak reads num
						$img->moveTo($cx-25,$cy);
						$img->angle(0);
						$img->fontsize(30);
						$img->font('Times:bold');
						# $img->string("$j_r");
						print $BASE_NAME,"\t",$name_group[$sa],"\tpeak\n";
					}
				}
				if(defined($peak{$chr}->[$sa]->{"-"}->{$j})){
					$img->penSize(5,5);

					# @rgb=(120,0,98);
					# @rgb=(193,140,0);


					@rgb=(222,49,99);
					$index = $img->translate_color(@rgb);
					$img->fgcolor($index);
					$img->bgcolor(undef);
					
					my @start_peak = split /\s+/, $peak{$chr}->[$sa]->{"-"}->{$j};
					foreach my $i (@start_peak) {
						my ( $j_e, $j_r ) = split /\-/, $i;
						# next if $j_r<2;
						my $floor_noadd_flag = 0;
						my $j_floor = 0;
						my $floor=0;
						for($floor=0;$floor<@floor_n;$floor++){
							if($j>=$floor_n[$floor]){
								$j_floor = $floor;
								$floor_n[$floor] = $j_e;
								$floor_noadd_flag = 1;
							}
						}
						if($floor_noadd_flag == 0){
							$j_floor = $floor;
							$floor_n[$floor] = $j_e;
						}
						my $j_s = $j;
						my $j_m = int(($j_e - $j_s)/2) + $j_s;
						my $j_s_x = $left+($j_s-$Cluster_start)*$ratio/$scale;
						my $j_s_y = $top+($zero_depth_locate+$j_floor*$floor_height+0.003)*$scale_height/$scale;
						my $j_e_x = $left+($j_e-$Cluster_start)*$ratio/$scale;
						my $j_e_y = $top+($zero_depth_locate+$j_floor*$floor_height+0.003)*$scale_height/$scale;
						my $cx = $left+($j_m-$Cluster_start)*$ratio/$scale;
						my $cy = $top+($zero_depth_locate+$j_floor*$floor_height+0.01)*$scale_height/$scale;
						$img->line($j_s_x,$j_s_y-0.003*$scale_height/$scale,$j_s_x,$j_s_y+0.007*$scale_height/$scale);
						$img->line($j_e_x,$j_e_y-0.003*$scale_height/$scale,$j_e_x,$j_e_y+0.007*$scale_height/$scale);
						$img->line($j_s_x,$j_s_y,$j_e_x,$j_e_y);
						#peak reads num
						$img->moveTo($cx-25,$cy);
						$img->angle(0);
						$img->fontsize(30);
						$img->font('Times:bold');
						# $img->string("$j_r");
						print $BASE_NAME,"\t",$name_group[$sa],"\tpeak\n";
					}
				}
			}
		}

		# ##draw AS
		# if($draw_as_flag==1){
		# 	for(my $j=$Cluster_start;$j<=$Cluster_end;$j++){
		# 		if(defined($as{$chr}->[$sa]->{$j})){
		# 			$img->penSize(5,5);

		# 			# @rgb=(0,140,94);



		# 			$index = $img->translate_color(@rgb);
		# 			$img->fgcolor($index);
		# 			$img->bgcolor(undef);

		# 			my @start_as = split /\s+/, $as{$chr}->[$sa]->{$j};
		# 			foreach my $i (@start_as) {
		# 				my ( $j_e, $j_t, $j_g ) = split /\:/, $i;
						


		# 				my $j_s_x = $left+($j_s-$Cluster_start)*$ratio/$scale;
		# 				my $j_s_y = $top+$zero_depth_locate*$scale_height/$scale;
		# 				my $j_e_x = $left+($j_e-$Cluster_start)*$ratio/$scale;
		# 				my $j_e_y = $top+$zero_depth_locate*$scale_height/$scale;


		# 				$img->line($j_s_x,0,$j_s_x,$Height);
		# 				$img->line($j_e_x,0,$j_e_x,$Height);
		# 				$img->line($j_s_x,$j_s_y-100,$j_e_x,$j_e_y-100);
		# 				#as reads num
		# 				$img->moveTo($cx-25,$cy);
		# 				$img->angle(0);
		# 				$img->fontsize(30);
		# 				$img->font('Times:bold');
		# 				$img->string($j_t);
		# 				$img->moveTo($cx-25,$cy+50);
		# 				$img->string($j_g);
		# 			}
		# 		}
		# 	}
		# }
	}
	binmode OUT;
	print OUT $img->png;
	close OUT;
	# print "Done draw $BASE_NAME\n";
	undef(%base_p);
	undef(%base_n);
}




sub max_depth {
	my ( $chr, $start, $end, $sa, $base) = @_;
	my @basenum = ();
	for ( my $j = $start ; $j <= $end ; $j++ ) {
		$base->{$chr}->{$sa}->{$j} = 0 if not defined($base->{$chr}->{$sa}->{$j});
		push @basenum, $base->{$chr}->{$sa}->{$j};
	}
	return -1 unless (@basenum);
	my $max_value = shift @basenum;
	foreach (@basenum) {
		if ( $_ > $max_value ) {
			$max_value = $_;
		}
	}
	return log($max_value)/log(2) if($log_flag==1 && $max_value!=0);
	return $max_value if($log_flag==0 || $max_value==0);
}


############Time_end#############
my $Time_End;
$Time_End = sub_format_datetime( localtime( time() ) );
print "\nEnd Time :[$Time_End]\n\n";

my $time_used = time() - $start_time;
my $h         = $time_used / 3600;
my $m         = $time_used % 3600 / 60;
my $s         = $time_used % 3600 % 60;
printf( "\nAll Time used : %d hours\, %d minutes\, %d seconds\n\n", $h, $m,
	$s );

#######Sub_format_datetime#######
sub sub_format_datetime {    #Time calculation subroutine
	my ( $sec, $min, $hour, $day, $mon, $year, $wday, $yday, $isdst ) = @_;
	$wday = $yday = $isdst = 0;
	sprintf(
		"%4d-%02d-%02d %02d:%02d:%02d",
		$year + 1900,
		$mon + 1, $day, $hour, $min, $sec
	);
}
