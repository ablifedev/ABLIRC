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
use Bio::DB::Sam;
use YAML::XS qw(DumpFile LoadFile);

#Before writing your programmeyou must write the detailed time /discriptions /parameter and it's explanation,Meanwhile,annotation your programme in English if possible.

##v1.1



##v1.2

##v1.3


##v1.4

##v1.6



##v2.0.0





my %opts;
GetOptions( \%opts, "bam=s","name=s", "k=s", "gff=s", "w=s", "c=s","fa=s","o=s", "i=s", "r=s","l=s", "g=s","chr=s","start=s","end=s","bed=s","as=s","peak=s","dr=s","h" );

if (   !defined( $opts{bam} )
	|| !defined( $opts{name} )
	|| !defined( $opts{gff} )
	|| !defined( $opts{fa} )
	|| defined( $opts{h} ) )
{
	print <<"	Usage End.";

		Version:$ver

	Usage:perl $0

		-bam         bam file,ex:bam1[,bam2,bam3...]                        must be given;
		-name        sample name,ex:name1[,name2,name3]                     must be given;
		-k           kgXref file                     option;
		-c           chunk job number                     default is 1000;
		-gff         gff file                        must be given;
		-w           window                          default is 3000;
		-fa          fa file                          must be given;
		-o           out file                        default is draw;
		-l           log depth or not (0/1)          default is 0
		-i           will it be drawn if cluster have no genes,1 for yes,0 for no     default is 0;
		-g           draw whole genome, 0 or 1, -g and -r, only one can be set to '1', default is 1
		-r           draw region, 0 or 1, require -chr -start -end ,-g and -r, only one can be set to '1', default is 0
		-chr         -r:chromosome
		-start       -r:start
		-end         -r:end
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

my $kgXref_file              = $opts{k} if defined($opts{k});;
my $gff_file                 = $opts{gff};
my $window                   = 3000;
$window                   = $opts{w} if defined($opts{w});
my $out_file                 = "draw";
$out_file                 = $opts{o} if defined($opts{o});
my $fa_file                 = $opts{fa};
my $draw_intergenic_flag     = 0;
$draw_intergenic_flag     = $opts{i} if defined($opts{i});
my $log_flag     = 0;
$log_flag = $opts{l} if defined($opts{l});
my $chunk_jobs = 1000;
$chunk_jobs = $opts{c} if defined($opts{c});

my $depth_ratio = 1;
$depth_ratio = $opts{dr} if(defined($opts{dr}));

my $draw_genome_flag = 1;
my $draw_region_flag = 0;

$draw_genome_flag = $opts{g} if(defined($opts{g}));
$draw_region_flag = $opts{r} if(defined($opts{r}));

my $region_chr = $opts{chr} if(defined($opts{chr}));
my $region_start = $opts{start} if(defined($opts{start}));
my $region_end = $opts{end} if(defined($opts{end}));

if(defined($opts{r}) && not defined($opts{g})){
	$draw_genome_flag=0;
}

if($draw_genome_flag==1){
	if($draw_region_flag==1){
		print "-g and -r, only one can be set to '1'\n";
		exit;
	}
}else{
	if($draw_region_flag==1){
		if(!defined( $opts{chr} ) || !defined( $opts{start} ) || !defined( $opts{end} )){
			print "require -chr -start -end when -r is set to '1'\n";
			exit;
		}
	}else{
		print "-r must be set to '1' when -g is set to '0'\n";
		exit;
	}
}

# my $draw_junction_flag = 0;
# $draw_junction_flag = 1 if(defined($opts{bed}));
# my @junction_file_group = split(/,/,$opts{bed}) if(defined($opts{bed}));


#####main
my $sample_num = scalar(@bamfile_group);

my $chrlen_file = "$current_dir/chrlen";
`getChrLength.pl $fa_file $current_dir/chrlen` if (!-f "$current_dir/chrlen") ;
print "creat chrlength file: $current_dir/chrlen \n";

my %chromosome = ();
open CHRLEN, $chrlen_file || die;
while (<CHRLEN>) {
	chomp;
	my ( $chr, $len ) = split /\s+/;
	$chromosome{$chr} = $len;
}
close CHRLEN;

my %kgXref=();
&load_kgXref($kgXref_file,\%kgXref) if (defined $kgXref_file ) ;
my %gene=();
&load_gff($gff_file,\%gene,\%kgXref);

my %cluster_gene=();
if($draw_region_flag==1){
	&cluster_gene_selected(\%gene,\%cluster_gene,$window,$region_chr,$region_start,$region_end);
}else{
	&cluster_gene(\%gene,\%cluster_gene,$window);
}

&output_clustered_gene(\%cluster_gene,$out_file);

mkdir("$current_dir/batch_data");
my $yaml_file = "$current_dir/batch_data/cluster.yaml";
DumpFile($yaml_file,%cluster_gene);

my $batch_num = 0;
foreach my $CHRO (sort keys %cluster_gene) {
	mkdir("$current_dir/$CHRO");

	my $cluster_index_min = 0;
	my $cluster_index_max = 0;


	while($cluster_index_max<@{$cluster_gene{$CHRO}}){
		$batch_num++;
		my %tmp_hash=();
		$cluster_index_max = $cluster_index_min + $chunk_jobs;
		if($cluster_index_max>=@{$cluster_gene{$CHRO}}){
			$cluster_index_max = $#{$cluster_gene{$CHRO}}+1;
		}
		$tmp_hash{"chr"} = $CHRO;
		$tmp_hash{"index_start"} = $cluster_index_min;
		$tmp_hash{"index_end"} = $cluster_index_max-1;
		my $batch_file = "$current_dir/batch_data/batch_$batch_num.yaml";
		DumpFile($batch_file,%tmp_hash);
		$cluster_index_min = $cluster_index_max;
	}

}

print $batch_num,"\n";

my $SH = $out_file."_cmd.sh";

open(OUT,">$SH") || die $!;
for(my $b=1;$b<=$batch_num;$b++){
	my $batch_file = "$current_dir/batch_data/batch_$b.yaml";
	if(defined($opts{bed}) && defined($opts{as})){
		print OUT "cd $current_dir && perl5.16 $Bin/draw_genome_v2.0.4.pl -cluster $batch_file -bam $opts{bam} -name $opts{name} -fa $opts{fa} -l $log_flag -i $draw_intergenic_flag -bed $opts{bed} -as $opts{as} -dr $depth_ratio \&\&\n";
	}elsif(defined($opts{bed})){
		print OUT "cd $current_dir && perl5.16 $Bin/draw_genome_v2.0.4.pl -cluster $batch_file -bam $opts{bam} -name $opts{name} -fa $opts{fa} -l $log_flag -i $draw_intergenic_flag -bed $opts{bed} -dr $depth_ratio \&\&\n";
		}elsif(defined($opts{peak})){
		print OUT "cd $current_dir && perl5.16 $Bin/draw_genome_v2.0.4.pl -cluster $batch_file -bam $opts{bam} -name $opts{name} -fa $opts{fa} -l $log_flag -i $draw_intergenic_flag -peak $opts{peak} -dr $depth_ratio \&\&\n";
		}else{
		print OUT "cd $current_dir && perl5.16 $Bin/draw_genome_v2.0.4.pl -cluster $batch_file -bam $opts{bam} -name $opts{name} -fa $opts{fa} -l $log_flag -i $draw_intergenic_flag -dr $depth_ratio \&\&\n";
	}
}

#`perl /public/bin/qsub-sge.pl --queue all.q --resource vf=10.0G --maxproc 100 $SH`;
`perl $Bin/../../../public/qsub-sge.pl --usesge $usesge --queue $queue --maxproc $cpu $SH`;
# `sh $SH > log`;

sub load_kgXref{
	my ($infile,$hash_ref)=@_;
	open (IN ,"<$infile") || die "Can't open $!";
	while (<IN>) {
		chomp;
		my @line=split(/\t/,$_);
		my $geneID=$line[0];
		if ($geneID=~/([\w\.]+)/) {
			# $hash_ref->{$1}=join("\t",@line);
			$hash_ref->{$1}=$line[0].":".$line[4];
		}
		else{
			# $hash_ref->{$geneID}=join("\t",@line);
			$hash_ref->{$geneID}=$line[0].":".$line[4];
		}
	}
	close IN ;
	print "Done load kgXref\n";
}

sub load_gff{
	my ($GFF_INFILE,$hash,$kgXref)=@_;
	my @gene_content=();
	my $RNA_index=0;
	my $gene_start=0;
	my $CHROMOSOME="";
	open (IN,"$GFF_INFILE") || die $!;
	while (<IN>) {
		chomp;
		next if (/^\#/) ;
		my @line=split(/\t/,$_);
		next if ($line[2]=~/^protein$/ );
		if ($line[2]=~/^gene|pseudogene|transposable_element_gene$/ ) {
			if (@gene_content){
				foreach my $mRNA (@gene_content[1..$#gene_content]) {
					my $mRNAID="";
					if ($mRNA->[0]->[-1]=~/^ID=([\w|\.|\_|\-]+)\;/) {
						$mRNAID=$1 ;
						if (exists($kgXref->{$mRNAID})){
							push @{$mRNA->[0]},$kgXref->{$mRNAID};
						}else{
							push @{$mRNA->[0]},$mRNAID;
						}
					}
					@{$mRNA}[1..$#{$mRNA}]=sort {$a->[3]<=>$b->[3]} sort {$a->[2] cmp $b->[2]}  @{$mRNA}[1..$#{$mRNA}];
				}
#				&build_index(\@gene_content,$promoter,10000,$hash,$CHROMOSOME);
				push @{$hash->{$CHROMOSOME}},[@gene_content];
			}
			$RNA_index=0;
			($CHROMOSOME,$gene_start)=@line[0,3];
			@gene_content=();
			push @{$gene_content[$RNA_index]},[@line];
		}
		elsif($line[2]=~/^mRNA|miRNA|mRNA_TE_gene|ncRNA|pseudogenic_transcript|rRNA|snoRNA|snRNA|tRNA|transcript$/){
			$RNA_index++;
			push @{$gene_content[$RNA_index]},[@line];
		}
		elsif($line[2]=~/^chromosome|region|chr$/i){
			next;
		}
		else{
			push @{$gene_content[$RNA_index]},[@line];
		}
		if (eof(IN)) {
			if (@gene_content){
				foreach my $mRNA (@gene_content[1..$#gene_content]) {
					my $mRNAID="";
					if ($mRNA->[0]->[-1]=~/^ID=([\w|\.|\_|\-]+)\;/) {
						$mRNAID=$1 ;
						if (exists($kgXref->{$mRNAID})){
							push @{$mRNA->[0]},$kgXref->{$mRNAID};
						}else{
							push @{$mRNA->[0]},$mRNAID;
						}
					}
					@{$mRNA}[1..$#{$mRNA}]=sort {$a->[3]<=>$b->[3]} sort {$a->[2] cmp $b->[2]}  @{$mRNA}[1..$#{$mRNA}];
				}
				push @{$hash->{$CHROMOSOME}},[@gene_content];
				# print $hash->{$CHROMOSOME}->[1]->[0]->[0]->[3],"\n";
			}
		}
	}
	close(IN);
	&sort_gene($hash);
	print "Done load gff\n";
}

sub sort_gene{
	my $hash_ref=shift;
	foreach my $TEMP_CHRO (keys %{$hash_ref}) {
		@{$hash_ref->{$TEMP_CHRO}}= sort {$a->[0]->[0]->[3]<=>$b->[0]->[0]->[3] or $a->[0]->[0]->[4]<=>$b->[0]->[0]->[4] } @{$hash_ref->{$TEMP_CHRO}};
	}
}

sub cluster_gene_selected{
	my ($gene_ref,$gene_cluster_ref,$size,$chr,$start,$end)=@_;
	my $gene_index = 0;
	my $cluster_index=0;
	my $cluster_start = $start;
	my $cluster_end = $cluster_start + $size - 1;
	@{$gene_cluster_ref->{$chr}->[$cluster_index]->{"gene"}} = ();
	while(defined($gene_ref->{$chr}->[$gene_index]->[0]->[0]->[3])){
		if ($gene_ref->{$chr}->[$gene_index]->[0]->[0]->[4]>=$cluster_start) {
			if($gene_ref->{$chr}->[$gene_index]->[0]->[0]->[3]<$cluster_start){
				$cluster_start = $gene_ref->{$chr}->[$gene_index]->[0]->[0]->[3];
			}
			last;
		}else{
			$gene_index++;
		}
	}
	LABEL1: for ( my $i = 1 ; $i > 0 ; $i++ ){
		my $temp_RNA = $gene_ref->{$chr}->[$gene_index];
		if($cluster_end>=$end){
			# print "now 5\n";
			# if($cluster_index==0){
				@{$gene_cluster_ref->{$chr}->[$cluster_index]->{"gene"}} = ();
				while(defined($gene_ref->{$chr}->[$gene_index]->[0]->[0]->[3])){
					$temp_RNA = $gene_ref->{$chr}->[$gene_index];
					if ($temp_RNA->[0]->[0]->[3]>=$cluster_start && $temp_RNA->[0]->[0]->[3]<=$cluster_end) {
						push @{$gene_cluster_ref->{$chr}->[$cluster_index]->{"gene"}},[@{$temp_RNA}];
						$gene_index++;
					}else{
						last;
					}
				}

			# }
			
			$gene_cluster_ref->{$chr}->[$cluster_index]->{"cluster_start"}=$cluster_start;
			# $gene_cluster_ref->{$chr}->[$cluster_index]->{"cluster_end"}=$end;
			$gene_cluster_ref->{$chr}->[$cluster_index]->{"cluster_end"}=$cluster_end;
			last LABEL1;
		}
		# print "$cluster_start\t$cluster_end\n";
		if(not defined($gene_ref->{$chr}->[$gene_index]->[0]->[0]->[3])){
			# print "now 4\n";
			$gene_cluster_ref->{$chr}->[$cluster_index]->{"cluster_start"}=$cluster_start;
			$gene_cluster_ref->{$chr}->[$cluster_index]->{"cluster_end"}=$cluster_end;
			$cluster_index++;
			@{$gene_cluster_ref->{$chr}->[$cluster_index]->{"gene"}} = ();
			$cluster_start = $cluster_end + 1;
			$cluster_end = $cluster_start + $size - 1;
			next LABEL1;
		}

		# print $temp_RNA->[0]->[0]->[3],"\n";
		# print $temp_RNA->[0]->[0]->[4],"\n";
		# print "$cluster_start\t$cluster_end\n";
		if ($temp_RNA->[0]->[0]->[3]>=$cluster_start && $temp_RNA->[0]->[0]->[4]<=$cluster_end) {
			push @{$gene_cluster_ref->{$chr}->[$cluster_index]->{"gene"}},[@{$temp_RNA}];
			$gene_index++;
			# print "now 1\n";
		}elsif($temp_RNA->[0]->[0]->[3]>=$cluster_start && $temp_RNA->[0]->[0]->[3]<=$cluster_end && $temp_RNA->[0]->[0]->[4]>$cluster_end){
			$cluster_end = $temp_RNA->[0]->[0]->[4];
			push @{$gene_cluster_ref->{$chr}->[$cluster_index]->{"gene"}},[@{$temp_RNA}];
			$gene_index++;
			# print "now 2\n";
			# print "$cluster_start\t$cluster_end\n";
		}elsif($temp_RNA->[0]->[0]->[3]>$cluster_end){
			# print "now 3\n";
			$gene_cluster_ref->{$chr}->[$cluster_index]->{"cluster_start"}=$cluster_start;
			$gene_cluster_ref->{$chr}->[$cluster_index]->{"cluster_end"}=$cluster_end;
			# print "$chr\t$cluster_start\t$cluster_end\n";
			$cluster_start = $cluster_end + 1;
			$cluster_end = $cluster_start + $size - 1;
			$cluster_index++;
			@{$gene_cluster_ref->{$chr}->[$cluster_index]->{"gene"}} = ();
		}

	}
	print "Done cluster gene\n";
}

sub cluster_gene{
	my ($gene_ref,$gene_cluster_ref,$size)=@_;
	foreach my $chr (sort keys %chromosome){
		my $gene_index = 0;
		my $cluster_index=0;
		my $cluster_start = 1;
		my $cluster_end = $cluster_start + $size - 1;
		@{$gene_cluster_ref->{$chr}->[$cluster_index]->{"gene"}} = ();
		LABEL1: for ( my $i = 1 ; $i > 0 ; $i++ ){
			# print "$chr\t$cluster_index\n";
			my $temp_RNA = $gene_ref->{$chr}->[$gene_index];
			if($cluster_end>=$chromosome{$chr}){
				# print "now 5\n";
				# if($cluster_index==0){
					# print "now 6\n";
					@{$gene_cluster_ref->{$chr}->[$cluster_index]->{"gene"}} = ();
					while(defined($gene_ref->{$chr}->[$gene_index]->[0]->[0]->[3])){
						$temp_RNA = $gene_ref->{$chr}->[$gene_index];
						if ($temp_RNA->[0]->[0]->[3]>=$cluster_start && $temp_RNA->[0]->[0]->[3]<=$cluster_end) {
							push @{$gene_cluster_ref->{$chr}->[$cluster_index]->{"gene"}},[@{$temp_RNA}];
							$gene_index++;
						}else{
							last;
						}
					}

				# }
				
				$gene_cluster_ref->{$chr}->[$cluster_index]->{"cluster_start"}=$cluster_start;
				# $gene_cluster_ref->{$chr}->[$cluster_index]->{"cluster_end"}=$chromosome{$chr};
				$gene_cluster_ref->{$chr}->[$cluster_index]->{"cluster_end"}=$cluster_end;
				last LABEL1;
			}
			# print "$cluster_start\t$cluster_end\n";
			if(not defined($gene_ref->{$chr}->[$gene_index]->[0]->[0]->[3])){
				# print "now 4\n";
				$gene_cluster_ref->{$chr}->[$cluster_index]->{"cluster_start"}=$cluster_start;
				$gene_cluster_ref->{$chr}->[$cluster_index]->{"cluster_end"}=$cluster_end;
				$cluster_index++;
				@{$gene_cluster_ref->{$chr}->[$cluster_index]->{"gene"}} = ();
				$cluster_start = $cluster_end + 1;
				$cluster_end = $cluster_start + $size - 1;
				next LABEL1;
			}
			
			# print $temp_RNA->[0]->[0]->[3],"\n";
			# print $temp_RNA->[0]->[0]->[4],"\n";
			# print "$cluster_start\t$cluster_end\n";
			if ($temp_RNA->[0]->[0]->[3]>=$cluster_start && $temp_RNA->[0]->[0]->[4]<=$cluster_end) {
				push @{$gene_cluster_ref->{$chr}->[$cluster_index]->{"gene"}},[@{$temp_RNA}];
				$gene_index++;
				# print "now 1\n";
			}elsif($temp_RNA->[0]->[0]->[3]>=$cluster_start && $temp_RNA->[0]->[0]->[3]<=$cluster_end && $temp_RNA->[0]->[0]->[4]>$cluster_end){
				$cluster_end = $temp_RNA->[0]->[0]->[4];
				push @{$gene_cluster_ref->{$chr}->[$cluster_index]->{"gene"}},[@{$temp_RNA}];
				$gene_index++;
				# print "now 2\n";
				# print "$cluster_start\t$cluster_end\n";
			}elsif($temp_RNA->[0]->[0]->[3]>$cluster_end){
				# print "now 3\n";
				$gene_cluster_ref->{$chr}->[$cluster_index]->{"cluster_start"}=$cluster_start;
				$gene_cluster_ref->{$chr}->[$cluster_index]->{"cluster_end"}=$cluster_end;
				# print "$chr\t$cluster_start\t$cluster_end\n";
				$cluster_start = $cluster_end + 1;
				$cluster_end = $cluster_start + $size - 1;
				$cluster_index++;
				@{$gene_cluster_ref->{$chr}->[$cluster_index]->{"gene"}} = ();
			}

		}
	}
	print "Done cluster gene\n";
}

sub output_clustered_gene{
	my ($cluster_ref,$OUTFILE)=@_;
	open(OUT,">".$OUTFILE."_cluster.gff") || die $!;
	foreach my $TEMP_CHRO (sort keys %{$cluster_ref}) {
		# print $TEMP_CHRO,"\n";
		for(my $cluster_index=0;$cluster_index<@{$cluster_ref->{$TEMP_CHRO}};$cluster_index++) {
			my $s_tmp = $cluster_ref->{$TEMP_CHRO}->[$cluster_index]->{"cluster_start"};
			my $e_tmp = $cluster_ref->{$TEMP_CHRO}->[$cluster_index]->{"cluster_end"};
			print OUT ">$TEMP_CHRO\_cluster$cluster_index\t$s_tmp\t$e_tmp\n";
			# print $TEMP_CHRO,"\t",$cluster_index,"\n";
			# print scalar(@{$cluster_ref->{$TEMP_CHRO}->[$cluster_index]->{"gene"}}),"\n";
			if(scalar(@{$cluster_ref->{$TEMP_CHRO}->[$cluster_index]->{"gene"}})>0){
				foreach my $gene (@{$cluster_ref->{$TEMP_CHRO}->[$cluster_index]->{"gene"}}) {
					foreach my $RNA (@{$gene}) {
						foreach my $temp_line (@{$RNA}) {
							print OUT join("\t",@{$temp_line}),"\n";
						}
					}
				}
			}else{
				#do nothing!
			}
		}
	}
	close OUT;
	print "Done output cluster\n";
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
