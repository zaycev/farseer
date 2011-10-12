# -*- coding: utf-8 -*-
import re

EMPTY_LINE_REGEX = re.compile("^\s*$")
COMMENT_REGEX = re.compile("^\s*\#.*$")
SPACES_REGEX = re.compile("\s+")
TRANSITIONS_REGEX = re.compile("\s*"+re.escape("->")+"\s*")


def Namespace(apptrees):
	ns = dict()
	for tree in apptrees:
		ns_name = tree.get("namespace")
		apps = tree.get("apps")
		if ns != None:
			for app in apps:
				fullname = "{0}.{1}".format(ns_name, app[0])
				ns[fullname] = app[1]
	return ns

def Workflow(conf, namespace):
	lines = conf.split("\n")
	services = []
	for line in lines:
		if not COMMENT_REGEX.match(line) \
		and not EMPTY_LINE_REGEX.match(line):
			mapped = parse_line(line, namespace)
			services.extend(mapped)
	return services

def parse_line(confline, namespace):
	confline = SPACES_REGEX.sub("", confline)
	serv_keys = TRANSITIONS_REGEX.split(confline)
	return [namespace[key] for key in serv_keys
			if key in namespace]
	
# print(parse_usrconf(work_pipe, {})):