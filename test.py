#!/usr/bin/python3
import re
import time
import urllib.request

while True:
	req = urllib.request.Request("https://www.nationstates.net/cgi-bin/api.cgi?q=happenings;filter=founding")
	req.add_header("User-Agent", "pyNSrecruit/0.1 (South Jarvis)")
	resp = urllib.request.urlopen(req)
	if resp.status == 200:
		data = resp.read().decode("utf-8")
		happenings = re.finditer(r"<!\[CDATA\[(.*)\]\]>", data)
		for happening in happenings:
			happeningString = happening.group(1)
			nation = re.search(r"@@(.*)@@", happeningString).group(1)
			print(nation)
			break #Nested loops with breaks... I forsee problems...
	else:
		print("WARNING: Got a funny response code - {0}".format(resp.status))
	time.sleep(1)
