#! /usr/bin/env perl
#Author: ChengChao
#Establish Date: 2015-4-22
#Revise: ChengChao
#Revise Date: 2015-4-22
my $version = "1.0";

use strict;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);
use FileHandle;
use Encode;
use Text::Markdown;

my %opts;
GetOptions( \%opts, "t=s", "d=s","o=s", "h" );

if (   !defined( $opts{t} )
	|| defined( $opts{h} ) )
{
	print <<"Usage End.";

		Version:$version

	Usage:perl $0

		-t		 template file		must be given;
		-d       report theme dir   default is /users/ablife/ReportParserTools/theme/report/
		-o       out dir            default is ./

Usage End.

	exit;
}

# input template file from terminal#
my $template_file= $opts{t};
# my $theme_dir= $opts{d} || "/users/ablife/ReportParserTools/theme/report/";
my $theme_dir= $opts{d} || "$Bin/../theme/report/";


##### Load Config Option ##############
my %config=();
&Get_config($template_file,\%config);

my $title = $config{"Title"};

##### Load Content       ##############

my $raw_content = &Get_content($template_file,"content");

##### Load timepoint     ##############
my $timepoint = &Get_content($template_file,"timepoint");
my $t = Text::Markdown->new;
my $timepointhtml = $t->markdown($timepoint);

##### read page break html     ##############
my $divide_html_file = $theme_dir."/divide.html";
my $breakhtml = &readhtml($divide_html_file);

my $theme_main_html_file = $theme_dir."/reportTemplate.html";
my $assets_dir = $theme_dir."/assets";

my $id = 0;
main();

#==============Subroutines===============#
sub Get_config {
	my ($file,$hash_ref) = @_;
	my $start_flag = 0;
	open (T,"<$file") or warn "Can't open $file!\n";
	while (<T>) {
		chomp;
		next if(/^\/\/\//);        #
		next if(/^\s*$/);
		s/\r//g;		#chomp the \r character
		if(/^\[\[ablife:config\]\]/){
			$start_flag=1;
			next;
		}
		if($start_flag==0){
			next;
		}elsif($start_flag==1){
			if(/^\[\[ablife:config\]\]/){
				next;
			}elsif(/^\[\[ablife:/){
				$start_flag=0;
				next;
			}
			my @line = split(/\s+/,$_,2);
			$line[1]=~s/\s*$//;
			$hash_ref->{$line[0]} = $line[1];
		}
	}
	close(T);
}

sub Get_content {
	my ($file,$tag) = @_;
	my $Content = "";
	my $start_flag = 0;
	open (T,"<$file") or warn "Can't open $file!\n";
	while (<T>) {
		next if(/^\/\/\//);        #
		s/\/\/\///g;         #
		# next if(/^\s*$/);
		s/\r//g;		#chomp the \r character
		if(/^\[\[ablife:$tag\]\]/){
			$start_flag=1;
			next;
		}
		if($start_flag==0){
			next;
		}elsif($start_flag==1){
			if(/^\[\[ablife:/){
				last;
			}
			$Content .= $_;
		}
	}
	close(T);
	return $Content;
}

# main
sub main{
	`rm -rf ./assets && cp -r $assets_dir .`;
	open MAIN, '>', "index.html";

	my $temp = "";
	my $html = "";
	my @line = split(/\n/,$raw_content);
	foreach my $eachline (@line){
		# print $eachline,"\n";
		next if $eachline=~/^\/\/\//;  #
		if($eachline=~/^\[ablife:(\w+)\](.*)/){
			#      markdown   html    。
			my $m = Text::Markdown->new;
    		my $temphtml = $m->markdown($temp);
    		$html .= $temphtml."\n";
    		$temp = "";
    		#  tag  ，
    		my $tag = $1;
    		my $info = $2;
    		if($tag eq "newpage"){
    			$html .= $breakhtml."\n";
    		}elsif($tag eq "table"){
    			$html .= &showtable($info);
    		}elsif($tag eq "img"){
    			$html .= &showimg($info);
    		}elsif($tag eq "dirimg"){
    			$html .= &showdirimg($info);
    		}elsif($tag eq "linkgroup"){
    			$html .= &showlinkgroup($info);
    		}
    		elsif($tag eq "dirgroupimg"){
    			$html .= &showdirgroupimg($info);
    		}
    		elsif($tag eq "imggroup"){
    			$html .= &showimggroup($info);
    		}
		}else{
			$temp .= $eachline."\n";
		}
	}
	my $m = Text::Markdown->new;
	my $temphtml = $m->markdown($temp);
	$html .= $temphtml."\n";
	$temp = "";
	# print $html;

	my $mainhtml = &readhtml($theme_main_html_file);
	$mainhtml =~s/\[ablife:title\]/$config{"Title"}/;
	$mainhtml =~s/\[ablife:institutions\]/$config{"Institutions"}/;
	$mainhtml =~s/\[ablife:reportdate\]/$config{"Reportdate"}/;
	$mainhtml =~s/\[ablife:timepoint\]/$timepointhtml/;
	$mainhtml =~s/\[ablife:content\]/$html/;
	print MAIN $mainhtml;
	close MAIN;
	# `cp -r $assets_dir .` if !(-d "./assets");

}


sub readhtml {
	my ($file) = @_;
	my $content;
	open(IN, $file) || warn "html file < $file > is not found \n";
	my @lines = <IN>;
	foreach my $LINE (@lines) {
		$content .= $LINE;
	}
	close(IN);
	return $content;
}


sub showtable {
	my ($Info)=@_;
	my $temp_html="";
	my ($file,$name_en,$name_zh,$md) = split(/\|\|\|/,$Info);

	$md = 10 if not defined($md);
	my $xs = $md+5;
	$xs = 12 if $xs > 12;


	$file =~s/<(\w+)>/$config{$1}/g;

	my $table_name=$file;
	$table_name=~s/.+\///;
	$table_name=~s/\.\w+$//;
	# $csvfile=decode("utf-8",$csvfile);
	# $csvfile=encode("gbk",$csvfile);
	# print $csvfile,"\n";
	#
	$file=decode("gbk",$file);


	open IN,"$file" or return 0;

	my $first = <IN>;
	# $first=decode("gbk",$first);
	# print $first;
	$first=~s/\n$//;

	my @title_array = split(/\t/,$first);
	my $t_col= scalar(@title_array);
	my $f_size = "inherit";
	$f_size = "smaller" if $t_col>=8;

	my @rest=();
	while(<IN>){
		chomp;
		next if (/^$/);
		# $_=decode("gbk",$_);
		# print $_;
		# $_=~s/(\([\d\.]+\%\))/\<br\>$1/g;
		# $_=~s/(\([\d\.]+\%\))/\ $1/g;
		$_=~s/(\([\d\.]+\%\))/\<br\>$1/g;   #20150722
		push @rest,$_;
	}
	close IN;

	$temp_html .= '<div class="tablediv"><a href="'.$file.'"><p class="table_info">'.$name_en.'</p></a>'."\n";
	$temp_html .= '<div><p class="table_info">'.$name_zh.'</p></div>'."\n";
	$temp_html .= <<HTML;
	<div class="row"><div class="col-xs-$xs col-md-$md center-block" style="float:none;font-size: $f_size;"><table class="table table-hover table-striped"><thead>
HTML
	$temp_html .= row_first('th', $first);
	$temp_html .= '</thead><tbody>';
	$temp_html .= row('td', $_) foreach @rest;
	$temp_html .= '</tbody></table></div></div></div>'."\n";
	return $temp_html;
}

sub row {
	my $t = "";
	my $elem = shift;
	my $line = shift;
	if ($line=~/^###/){
		return $t;
	}
	if ($line=~/^#/){
		$line=~s/#//g;
		my @cells = map {"<th>$_</th>"} split '\t', $line;
		$t .= '<tr class="tablehead">'. join("",@cells) ."</tr>\n";
	}else{
		my @cells = map {"<$elem>$_</$elem>"} split '\t', $line;
		$t .= '<tr>'. join("",@cells) ."</tr>\n";
	}
	return $t;
}

sub row_first {
	my $t = "";
	my $elem = shift;
	my $value = shift;
	$value=~s/#//g;
	my @line = split '\t', $value;
	my $c=1;
	my @cells = ();
	my $fe = shift @line;
	my $str = "";
	foreach my $e (@line){
		if($e ne ""){
			$str = "<$elem colspan=\"$c\">$fe</$elem>";
			push @cells,$str;
			$fe = $e;
			$c = 1;
		}else{
			$c++;
		}
	}
	$str = "<$elem colspan=\"$c\">$fe</$elem>";
	push @cells,$str;

	# my @cells = map {"<$elem>$_</$elem>"} split '\t', shift;
	$t .= '<tr>'. join("",@cells) ."</tr>\n";
	return $t;
}


sub showimg {
	my ($Info)=@_;
	my $temp_html="";
	my ($img,$name_en,$name_zh,$md) = split(/\|\|\|/,$Info);

	$md = 6 if not defined($md);
	my $xs = $md;
	$xs = 12 if $xs > 12;

	$img =~s/<(\w+)>/$config{$1}/g;

	my $img_name=$img;
	$img_name=~s/\S+\///;
	$img_name=~s/\.\w+$//;

	$id++;
	my $gid = "g".$id;

	# my $width=$w."px";
	# my $height=$h."px";
	# my $border_width=($w-2)."px";
	# my $border_height=($h-2)."px";
	$temp_html .= <<HTML;
	<div class="tablediv"><div class="row"><div class="col-xs-$xs col-md-$md center-block" style="float:none;"><a href="$img" data-lightbox="$gid" data-title="$name_en" class="thumbnail"><img src="$img" alt="$name_en" /></a></div></div>
HTML
	$temp_html .= '<div><p class="figure_info">'.$name_en.'</p></div>'."\n";
	$temp_html .= '<div><p class="figure_info">'.$name_zh.'</p></div>'."\n";
	$temp_html .= '</div>'."\n";

	return $temp_html;
}


sub showdirimg {
	my ($Info)=@_;
	my $temp_html="";
	my ($dir,$name,$md,$mdimg) = split(/\|\|\|/,$Info);

	$md = 10 if not defined($md);
	my $xs = $md;
	$xs = 12 if $xs > 12;

	$mdimg = 6 if not defined($mdimg);
	# my $xsimg = $mdimg;
	my $xsimg = 6;
	$xsimg = 12 if $xsimg > 12;

	my $img_count=0;
	my $cr = int(12/$mdimg);

	$dir =~s/<(\w+)>/$config{$1}/g;
	$id++;
	my $gid = "g".$id;

	$temp_html .= <<HTML;
		<div class="row">

	  <div class="panel panel-default col-xs-$xs col-md-$md center-block" style="float:none;padding:0px;">
    <div class="panel-heading" role="tab" id="headingOne">
      <div class="panel-title">
        <a data-toggle="collapse" data-parent="#accordion" href="#$gid" aria-expanded="true" aria-controls="$gid">
          $name
        </a>
      </div>
    </div>
    <div id="$gid" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="headingOne">
      <div class="panel-body">
		<div class="row">
HTML


	opendir(TMPDIR,$dir) or warn "dir < $dir > is not found \n";
		my $tmp_file;
		while ($tmp_file=readdir(TMPDIR)) {
			chomp $tmp_file;
			next if $tmp_file=~/^\./;
			# print $tmp_file,"\n";
			next if $tmp_file!~/$name/;
			next if $tmp_file!~/\.(png|jpg|gif|jpeg|bmp)/;
			# print $tmp_file,"\n";

			my $imgtitle=$tmp_file;
			$imgtitle=~s/\.(png|jpg|gif|jpeg|bmp)//;
			$tmp_file="$dir/$tmp_file";
			next if!(-f $tmp_file);

			$img_count++;

			$tmp_file=decode("gbk",$tmp_file);
			$temp_html .= <<HTML;
				<div class="col-xs-$xsimg col-md-$mdimg"><a href="$tmp_file" data-lightbox="$gid" data-title="$imgtitle" class="thumbnail"><img src="$tmp_file" alt="$imgtitle" /><div class="caption">$imgtitle</div></a></div>
HTML

			if($img_count%$cr==0){

				$temp_html .= '<div class="clearfix visible-xs-block visible-md-block visible-lg-block"></div>';
			}
		}

	close(DIR);


	$temp_html .= <<HTML;
	</div>
		</div>
      </div>
    </div>

  </div>
HTML


	return $temp_html;

}


sub showdirgroupimg {
	my ($Info)=@_;
	my $temp_html="";
	my ($dir,$name,$md,$mdimg) = split(/\|\|\|/,$Info);
	# print $name,"\n";

	$md = 10 if not defined($md);
	my $xs = $md;
	$xs = 12 if $xs > 12;

	$mdimg = 6 if not defined($mdimg);
	# my $xsimg = $mdimg;
	my $xsimg = 6;
	$xsimg = 12 if $xsimg > 12;

	my $img_count=0;
	my $cr = int(12/$mdimg);

	$dir =~s/<(\w+)>/$config{$1}/g;

	opendir(DIR,$dir) or return 0;

	my $tmp;
	my @dirs = readdir(DIR);
	foreach $tmp (sort @dirs){
	# while ($tmp=readdir(DIR)) {
		chomp $tmp;
		next if $tmp=~/^\./;
		my $tmp_dir = "$dir/$tmp";
		next if!(-d $tmp_dir);

		my $grouptitle=$tmp;
		$grouptitle=~s/\///;
		$grouptitle=decode("gbk",$grouptitle);
		$id++;
		my $gid = "g".$id;
		$img_count=0;

		$temp_html .= <<HTML;
			<div class="row">

				  <div class="panel panel-default col-xs-$xs col-md-$md center-block" style="float:none;padding:0px;">
			    <div class="panel-heading" role="tab" id="headingOne">
			      <div class="panel-title">
			        <a data-toggle="collapse" data-parent="#accordion" href="#$gid" aria-expanded="true" aria-controls="$gid">
			          $grouptitle
			        </a>
			      </div>
			    </div>
			    <div id="$gid" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="headingOne">
			  <div class="panel-body">
			<div class="row">
HTML


		opendir(TMPDIR,$tmp_dir) or warn "dir < $tmp_dir > is not found \n";
		my $tmp_file;
		while ($tmp_file=readdir(TMPDIR)) {
			chomp $tmp_file;
			next if $tmp_file=~/^\./;
			# print $tmp_file,"\n";
			next if $tmp_file!~/\.(png|jpg|gif|jpeg|bmp)/;
			if($name ne ""){
				next if $tmp_file!~/$name/i;
			}
			# print $tmp_file,"\n";

			my $imgtitle=$tmp_file;
			$imgtitle=~s/\.(png|jpg|gif|jpeg|bmp)//;
			$tmp_file="$tmp_dir/$tmp_file";
			next if!(-f $tmp_file);
			# print $tmp_file,"\n";
			$img_count++;

			$tmp_file=decode("gbk",$tmp_file);

			$temp_html .= <<HTML;
				<div class="col-xs-$xsimg col-md-$mdimg"><a href="$tmp_file" data-lightbox="$gid" data-title="$imgtitle" class="thumbnail"><img src="$tmp_file" alt="$imgtitle" /><div class="caption">$imgtitle</div></a></div>
HTML
			if($img_count%$cr==0){

				$temp_html .= '<div class="clearfix visible-xs-block visible-md-block visible-lg-block"></div>';
			}
		}
		closedir TMPDIR;
		$temp_html .= <<HTML;
			</div>
				</div>
		      </div>
		    </div>

		  </div>
HTML
	}
	closedir(DIR);
	return $temp_html;

}



sub showimggroup {
	my ($Info)=@_;
	my $temp_html="";
	my ($dir,$imgname,$md,$mdimg,$trim) = split(/\|\|\|/,$Info);

	$md = 10 if (not defined($md) or $md eq "");
	$trim = 0 if (not defined($trim) or $trim eq "");
	my $xs = $md;
	$xs = 12 if $xs > 12;

	$mdimg = 6 if (not defined($mdimg) or $mdimg eq "");
	# my $xsimg = $mdimg;
	my $xsimg = 6;
	$xsimg = 12 if $xsimg > 12;

	my $img_count=0;
	my $cr = int(12/$mdimg);

	$dir =~s/<(\w+)>/$config{$1}/g;
	$dir=decode("gb2312",$dir);
	opendir(DIR,$dir) or return 0;
	$id++;
	my $gid = "g".$id;

	$temp_html .= <<HTML;
		<div class="row">

			  <div class="panel panel-default col-xs-$xs col-md-$md center-block" style="float:none;padding:0px;">
		    <div class="panel-heading" role="tab" id="headingOne">
		      <div class="panel-title">
		        <a data-toggle="collapse" data-parent="#accordion" href="#$gid" aria-expanded="true" aria-controls="$gid">
		          $imgname
		        </a>
		      </div>
		    </div>
		    <div id="$gid" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="headingOne">
		  <div class="panel-body">
		<div class="row">
HTML
	my $tmp;
	my @dirs = readdir(DIR);
	foreach $tmp (sort @dirs){
	# while ($tmp=readdir(DIR)) {
		chomp $tmp;
		next if $tmp=~/^\./;
		my $tmp_dir = "$dir/$tmp";
		$tmp=decode("gb2312",$tmp);
		next if!(-d $tmp_dir);
		opendir(TMPDIR,$tmp_dir) or warn "dir < $tmp_dir > is not found \n";
		my $tmp_file;
		while ($tmp_file=readdir(TMPDIR)) {
			chomp $tmp_file;
			if ($tmp_file=~/$imgname/){
				next if $tmp_file!~/\.(png|jpg|gif|jpeg|bmp)$/;
				# print $tmp_file,"\n";

				my $imgtitle=$tmp_file;
				$imgtitle=~s/\.(png|jpg|gif|jpeg|bmp)//;
				$tmp_file="$tmp_dir/$tmp_file";
				$tmp_file=decode("gbk",$tmp_file);
				my $tmp2 = $tmp ;
				$tmp2=~s/_[0-9a-zA-Z]+$// if $trim == 1;

				$img_count++;
				$temp_html .= <<HTML;
				<div class="col-xs-$xsimg col-md-$mdimg"><a href="$tmp_file" data-lightbox="$gid" data-title="$imgtitle" class="thumbnail"><img src="$tmp_file" alt="$imgtitle" /><div class="caption">$tmp2</div></a></div>
HTML
				if($img_count%$cr==0){

					$temp_html .= '<div class="clearfix visible-xs-block visible-md-block visible-lg-block"></div>';
				}
			}
		}
		closedir TMPDIR;

	}
	closedir(DIR);
	$temp_html .= <<HTML;
			</div>
				</div>
		      </div>
		    </div>

		  </div>
HTML
	return $temp_html;

}



sub showlinkgroup {
	my ($Info)=@_;
	my $temp_html="";
	my ($dir,$linkname,$post) = split(/\|\|\|/,$Info);

	$dir =~s/<(\w+)>/$config{$1}/g;
	$dir=decode("gb2312",$dir);
	opendir(DIR,$dir) or return 0;
	$id++;

	my $tmp;
	my @dirs = readdir(DIR);
	foreach $tmp (sort @dirs){
	# while ($tmp=readdir(DIR)) {
		chomp $tmp;
		next if $tmp=~/^\./;
		my $tmp_dir = "$dir/$tmp";
		$tmp=decode("gb2312",$tmp);
		next if!(-d $tmp_dir);
		opendir(TMPDIR,$tmp_dir) or warn "dir < $tmp_dir > is not found \n";
		my $tmp_file;
		while ($tmp_file=readdir(TMPDIR)) {
			chomp $tmp_file;
			next if $tmp_file=~/^\./;
			if(-d "$tmp_dir/$tmp_file"){
				opendir(TMPDIR2,"$tmp_dir/$tmp_file");
				my $tmp_file2;
				while ($tmp_file2=readdir(TMPDIR2)) {
					chomp $tmp_file2;
					next if $tmp_file2=~/^\./;
					next if(-d "$tmp_dir/$tmp_file/$tmp_file2");
					if ($tmp_file2=~/$linkname/){
						my $linktitle=$tmp_file2;
						$tmp_file2="$tmp_dir/$tmp_file/$tmp_file2";
						$tmp_file2=decode("gbk",$tmp_file2);
						$temp_html .= <<HTML;
				<p><a href="$tmp_file2" target="_blank">$tmp $post</a></p>
HTML
					}
				}
				closedir TMPDIR2;
			}elsif ($tmp_file=~/$linkname/){
				my $linktitle=$tmp_file;
				$tmp_file="$tmp_dir/$tmp_file";
				$tmp_file=decode("gbk",$tmp_file);
				$temp_html .= <<HTML;
				<p><a href="$tmp_file" target="_blank">$tmp $post</a></p>
HTML
			}
		}
		closedir TMPDIR;

	}
	closedir(DIR);
	return $temp_html;

}


sub AbsolutePath{	   #
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
