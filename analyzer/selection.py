## -*- coding: utf-8 -*-
#
#from sqlalchemy import func
#from analyzer.term import DbBase, UntaggedTerm, TaggedTerm
#from analyzer.acessdb import make_environment
#from options import DATABASE_CONFIG
#
#import logging
#import sys
#
#class SelectionRule(object):
#	def __init__(self):
#		self.triggered = 0
#	def apply(self, lexicon_term):
#		pass
#
#
#DEFAULT_SELECTION_RULES  = []
#
def selection(input_table_name="set_uterm",
			  output_table_name="set_features_1",
			  pos_tagging=False):
	pass
#
#	logging.debug("establish database connection")
#	term_class = TaggedTerm if pos_tagging else UntaggedTerm
#	class RawTerm(DbBase, term_class):
#		__tablename__ = input_table_name
#		__mapper_args__ = {"concrete": True}
#	class SelectedTerm(DbBase, term_class):
#		__tablename__ = output_table_name
#		__mapper_args__ = {"concrete": True}
#	db_engine, db_session = make_environment(DATABASE_CONFIG["repository"])
#
#
#	logging.debug("create or truncate output table")
#	DbBase.metadata.create_all(db_engine)
#	db_session.query(SelectedTerm).delete()
#
#
#	logging.debug("retrieving input termset size")
#	corpus_sz = db_session.query(func.count("id")).select_from(UntaggedTerm).scalar()
#	logging.debug("termset size is {0}".format(corpus_sz))
#
#
#	logging.debug("start retrieve raw terms")
#	for term in db_session.query(RawTerm).order_by("id").yield_per(128):
#		print term