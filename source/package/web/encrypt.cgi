#!/usr/bin/perl -w

use CGI qw/:standard/;
use CGI::Carp qw(fatalsToBrowser);

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

$tmplhtml{'RESULT'} = "<br/>";

# is there an action?
$action = param ('action');
if ($action eq "mount") {
    # get the parameter
    $device = param ('path');
    $password = param ('password');
    $tmplhtml{'RESULT'} = "<br/><b>Result:<br/>";
    if (open (IN,"/usr/syno/sbin/mount.ecryptfs $device/\@LocalBackup\@ $device/LocalBackup -o ecryptfs_cipher=aes,ecryptfs_key_bytes=32,ecryptfs_passthrough=n,no_sig_cache,ecryptfs_enable_filename_crypto,passwd=$password 2>&1 |")) {
	while(<IN>) {
	    $tmplhtml{'RESULT'} = "$tmplhtml{'RESULT'}$_";
	}
    } else {
	$tmplhtml{'RESULT'} = "$tmplhtml{'RESULT'}$_";
    }
    $tmplhtml{'RESULT'} = "$tmplhtml{'RESULT'}</b><br/><br/>";
}
if ($action eq "unmount") {
    # get the parameter
    $device = param ('path');
    $tmplhtml{'RESULT'} = "<br/><b>Result:<br/>";
    my $result = "";
    if (open (IN,"/bin/umount $device 2>&1 |")) {
	while(<IN>) {
	    $result = "$result$_";
	}
	if (length ($result) > 0) {
	    $tmplhtml{'RESULT'} = "$tmplhtml{'RESULT'}$result";
	} else {
	    $tmplhtml{'RESULT'} = "$tmplhtml{'RESULT'}OK";
	}
    } else {
	$tmplhtml{'RESULT'} = "$tmplhtml{'RESULT'}error";
    }
    $tmplhtml{'RESULT'} = "$tmplhtml{'RESULT'}</b><br/><br/>";
}

# find the mounted devices
if (open (IN,"/bin/mount 2>&1 |")) {
    while(<IN>) {
	@tmp = split (" ");
	if ((substr (@tmp[2], 0, 10) eq "/volumeUSB") || (substr (@tmp[2], 0, 11) eq "/volumeSATA")) {
	    $path = @tmp[2];
	    if ((-e "$path/\@LocalBackup\@") && (-e "$path/LocalBackup")) {
		push (@drivesu, $path);
	    } else {
		if ($path =~ m/LocalBackup$/) {
		    push (@drivesm, $path);
		}
	    }
        }
    }
    close(IN);
}

# output
my $countu = @drivesu;
my $countm = @drivesm;
if (($countu+$countm) > 0) {
    if ($countu > 0) {
	$tmplhtml{'DRIVES'} = "\t\t<form action=\"encrypt.cgi\" method=\"post\">\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t<input type=\"hidden\" name=\"action\" value=\"mount\" />\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t<tr>\n\t\t\t\t<td>Device:</td>\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t\t<td><select name=\"path\">\n";
	foreach (sort (@drivesu)) {
	    $tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t\t<option>$_</option>\n";
	}
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t\t</select></td>\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t\t<td width=\"10px\"></td>\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t\t<td>Password:</td>\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t\t<td><input type=\"text\" name=\"password\" /></td>\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t\t<td width=\"10px\"></td>\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t\t<td><input type=\"submit\" value=\"  Mount  \" /> <small>(might take some seconds)</small></td>\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t</tr>\n\t\t</form>\n";
    }
    if ($countm > 0) {
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t<form action=\"encrypt.cgi\" method=\"post\">\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t<input type=\"hidden\" name=\"action\" value=\"unmount\" />\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t<tr>\n\t\t\t\t<td>Device:</td>\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t\t<td colspan=\"4\"><select name=\"path\">\n";
	foreach (sort (@drivesm)) {
	    $tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t\t<option>$_</option>\n";
	}
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t\t</select></td>\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t\t<td width=\"10px\"></td>\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t\t<td><input type=\"submit\" value=\"  Unmount  \" /></td>\n";
	$tmplhtml{'DRIVES'} = "$tmplhtml{'DRIVES'}\t\t\t</tr>\n\t\t</form>\n";
    }
} else {
    $tmplhtml{'DRIVES'} = "\t\t\t<tr><td>no drives connected</td></tr>\n";
}

if (open (IN, "encrypt.htmlt")) {
    while (<IN>) {
	s/==:([^:]+):==/$tmplhtml{$1}/g;
	print $_;
    }
    close (IN);
}
