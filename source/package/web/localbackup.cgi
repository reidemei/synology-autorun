#!/usr/bin/perl -w

use CGI qw/:standard/;
use CGI::Carp qw(fatalsToBrowser);
use File::Temp qw/ tempfile tempdir /;

print "Content-type: text/html\n\n";

# check authentication
if (open (IN,"/usr/syno/synoman/webman/modules/authenticate.cgi|")) {
    $user=<IN>;
    chop($user);
    close(IN);
}
if ($user ne "admin") {
    print "<HTML><HEAD><TITLE>Login Required</TITLE></HEAD><BODY>Please login as admin first, before using this webpage<br/><br/>";
    die;
}

# read the config
if (open (IN, "/var/packages/autorun/target/config")) {
    while (<IN>) {
	chomp;
	s/#.//;
	s/^\s+//;
	s/\s+$//;
	my ($var, $value) = split(/\s*=\s*/, $_, 2);
	$tmplhtml{$var}=$value;
    }
    close (IN);
}

# is there an action?
$action = param ('action');
if ($action eq "create") {
    # get the parameter
    $file = param ('file');
    $target = param ('target');
    $backup = param ('backup');
    $eject = param ('eject');
    $encrypt = param ('encrypt');
    $password = param ('password');
    # create the script
    if (open (OUT, ">$file")) {
	print OUT "#!/bin/sh\n";
	if ($encrypt eq "on") {
	    # store the password
	    my ($pwdir, $filename, $fh);
	    $pwdir = "/var/packages/autorun/target/passwords";
	    mkdir $pwdir unless -d $pwdir;
	    ($fh, $filename) = tempfile (DIR => $pwdir);
	    print $fh "$password";
	    close ($fh);
	    $filename = substr ($filename, length ($pwdir) + 1, length ($filename) - length ($pwdir) - 1);
	    print OUT "/var/packages/autorun/target/encryptbackup \"$filename\" \"$backup\" \"$target\" \"\$1\" ";
	} else {
	    print OUT "/var/packages/autorun/target/localbackup \"$backup\" \"$target\" \"\$1\" ";
	}
	if ($eject eq "on") {
	    print OUT "100\n";
	} else {
	    print OUT "0\n";
	}
	print OUT "exit \$?\n";
	close (OUT);
	chmod 777, $file;
    }
}
if ($action eq "delete") {
    $file = param ('file');
    unlink ($file);
}

# load the local backups
open(IN,"/etc/synolocalbkp.conf");
while(<IN>) {
    if (/^\[/) {
	($sname)=/\[([^\]]+)\]/;
    } else {
	($key,$value)=/\s+([^=]+)=(.*)$/;
	if ($key eq "dest_share") {
	    $value =~ s/[^a-zA-Z0-9]*//g;
	    if (substr ($value, 0, 8) eq "usbshare") {
		$backupsUSB{$sname}=substr ($value, 8);
		$backups{$sname}="-/volumeUSB$backupsUSB{$sname}/usbshare";
	    }
	    if (substr ($value, 0, 9) eq "satashare") {
		$backupsSATA{$sname}=$value;
		$backups{$sname}="-/volumeSATA/$value";
	    }
	}
    }
}
close(IN);

# find the mounted devices
if (open (IN,"/bin/mount 2>&1 |")) {
    while(<IN>) {
	@tmp = split (" ");
	if (substr (@tmp[2], 0, 10) eq "/volumeUSB") {
	    $pos = substr (@tmp[2], 10, index (@tmp[2], "/", 10)-10);
	    foreach $value (keys(%backupsUSB)) {
		if ($backupsUSB{$value} eq $pos) {
		    $backups{$value}=@tmp[2];
		}
	    }
	}
	if (substr (@tmp[2], 0, 11) eq "/volumeSATA") {
	    foreach $value (keys(%backupsSATA)) {
		$backups{$value}=@tmp[2];
	    }
	}
    }
    close(IN);
}

# output
foreach $value (sort (keys (%backups))) {
    $text = "";
    if ( substr ($backups{$value}, 0, 1) eq "-" ) {
	$backups{$value} = substr ($backups{$value}, 1);
	$text = "<td></td>\n\t\t\t<td></td>\n\t\t\t<td></td>\n\t\t\t<td></td>\n\t\t\t<td></td>\n\t\t\t<td></td>\n\t\t\t<td colspan=\"2\">device not connected</td>";
    } else {
	$text = " action=\"localbackup.cgi\" method=\"post\">\n\t\t\t\t<input type=\"hidden\" name=\"action\" value=\"create\" />\n\t\t\t\t<input type=\"hidden\" name=\"file\" value=\"$backups{$value}/$tmplhtml{'SCRIPT'}\" />\n\t\t\t\t<input type=\"hidden\" name=\"backup\" value=\"$value\" />\n\t\t\t\t<input type=\"hidden\" name=\"target\" value=\"$backups{$value}\" />\n\t\t\t\t<td align=\"center\"><input type=\"checkbox\" name=\"eject\" /></td>\n\t\t\t\t<td></td>\n\t\t\t\t<td align=\"center\"><input type=\"checkbox\" name=\"encrypt\" /></td>\n\t\t\t\t<td></td>\n\t\t\t\t<td align=\"center\"><input type=\"text\" size=\"15\" name=\"password\" /></td>\n\t\t\t\t<td>\n\t\t\t\t<td><input type=\"submit\" value=\"  Create  \"";
	if (-e "$backups{$value}/$tmplhtml{'SCRIPT'}") {
	    $text = "<form onsubmit=\"return commitOverwrite(\'$backups{$value}/$tmplhtml{'SCRIPT'}\')\"$text /></td>\n\t\t\t</form>\n\t\t\t<form action=\"localbackup.cgi\" method=\"post\" onsubmit=\"return commitDelete(\'$backups{$value}/$tmplhtml{'SCRIPT'}\')\">\n\t\t\t\t<input type=\"hidden\" name=\"action\" value=\"delete\" />\n\t\t\t\t<input type=\"hidden\" name=\"file\" value=\"$backups{$value}/$tmplhtml{'SCRIPT'}\" />\n\t\t\t\t<td><input type=\"submit\" value=\"  Delete  \" /></td>\n\t\t\t</form>";
	} else {
	    $text = "<form $text /></td><td></td>\n";
	}
    }
    $tmplhtml{'BACKUPS'} = "$tmplhtml{'BACKUPS'}\t\t<tr height=\"27\">\n\t\t\t<td><b>$value</b></td>\n\t\t\t<td></td>\n\t\t\t<td>$backups{$value}</td>\n\t\t\t<td></td>\n\t\t\t$text\n\t\t</tr>\n";
}

if (open (IN, "localbackup.htmlt")) {
    while (<IN>) {
	s/==:([^:]+):==/$tmplhtml{$1}/g;
	print $_;
    }
    close (IN);
}
