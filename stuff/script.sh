
TORSOCKS_CONF_FILE=torsocks.conf torsocks wget 14.1.0.1/file.txt -O client/file-\"`date +%R:%S.%N`\"-over-torsocks.txt

