# -*- coding: utf-8 -*-
import imp
import os
MODULE_EXTENSIONS = ('.py',)


def list_moduules():
	_, pathname, _ = imp.find_module("bundle")
	return set([("bundle.%s" % os.path.splitext(module)[0], "bundle/%s" % module)
				for module in os.listdir(pathname)
				if module.endswith(MODULE_EXTENSIONS)
				and module != "__init__.py"])

def get_bundles():
	for module_name, module_path in list_moduules():
		yield imp.load_source(module_name, module_path)

def get_bundle(key):
	for bundle in get_bundles():
		if bundle.BUNDLE_KEY == key:
			return bundle
	raise KeyError("Bundle with key %s not found" % key)
