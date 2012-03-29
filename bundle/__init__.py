# -*- coding: utf-8 -*-
import imp
import os
MODULE_EXTENSIONS = ('.py',)


def list_bundles():
	_, pathname, _ = imp.find_module("bundle")
	return set([("bundle.%s" % os.path.splitext(module)[0], "bundle/%s" % module)
				for module in os.listdir(pathname)
				if module.endswith(MODULE_EXTENSIONS) and module != "test.py"
				and module != "__init__.py"])

def get_bundles():
	for module_name, module_path in list_bundles():
		yield imp.load_source(module_name, module_path)

def get(key):
	for bundle in get_bundles():
		if bundle.BUNDLE_KEY == key:
			return bundle
	raise KeyError("Bundle with key %s not found" % key)


def install_test_datasets(bundles, datasets, test_size=32, place_dir="bundle/test"):

	import os
	import pickle
	import codecs
	import collector.models as cm

	if not os.path.exists(place_dir):
		os.makedirs(place_dir)

	def install_model_dataset(model, bundle, dataset):

		base_dir = os.path.join(place_dir, bundle.BUNDLE_KEY)
		if not os.path.exists(base_dir):
			os.makedirs(base_dir)

		objects = model.objects.filter(dataset=dataset).order_by("?")[0:test_size]
		objects_dir = os.path.join(base_dir, model.__name__)

		if not os.path.exists(objects_dir):
			os.makedirs(objects_dir)
		else:
			for fp in os.listdir(objects_dir):
				ffp = os.path.join(objects_dir, fp)
				print "\t ::remove %s" % ffp
				os.remove(ffp)

		for o in objects:
			f = codecs.open(os.path.join(objects_dir, "%s.pickle" % o.id), mode="w")
			f.write(pickle.dumps(o))
			f.close()

	for bundle, dataset in zip(bundles, datasets):

		install_model_dataset(cm.RawRiver, bundle, dataset)
		install_model_dataset(cm.RawDocument, bundle, dataset)


def iterate_test_objects(model, place_dir="bundle/test"):

	import os
	import codecs
	import pickle

	bundles = map(lambda dir: get(dir), os.listdir(place_dir))
	if not os.path.exists(place_dir):
		raise KeyError("There are no installed test datasets")
	else:
		for bundle in bundles:
			objects_dir = os.path.join(place_dir, bundle.BUNDLE_KEY, model.__name__)
			for fp in os.listdir(objects_dir):
				ffp = os.path.join(objects_dir, fp)
				f = codecs.open(ffp, mode="r")
				pickled = f.read()
				f.close()
				yield bundle, pickle.loads(pickled)