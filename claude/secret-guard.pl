#!/usr/bin/env perl
# Reads a diff on stdin; exits 1 if an added line looks like a credential.
# Catches Atlassian API tokens, AWS access keys, JWTs, private keys, and password values (letters+digits, 8+ chars) after -p / pwd= / password=.
# Branch names like jira/ABE-5320-porsche-dealer are not matched (no digit inside the token, or followed by '-').
my $bad = 0;
while (<STDIN>) {
    next unless /^\+/ && !/^\+\+\+/;
    if (/ATATT3|AKIA[0-9A-Z]{12}|eyJ[A-Za-z0-9_-]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----/
        || /(?:\s-p|pwd=|PWD=|[Pp]assword[=:]\s*)(?=[A-Za-z0-9@#\$%^&*_+=\/.!]*\d)(?=[A-Za-z0-9@#\$%^&*_+=\/.!]*[A-Za-z])[A-Za-z0-9@#\$%^&*_+=\/.!]{8,}(?![\w-])/) {
        print "secret-guard: $_"; $bad = 1;
    }
}
exit $bad;
