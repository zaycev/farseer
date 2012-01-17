##-*- coding: utf-8 -*
#
#from sqlalchemy import Table, Column, Integer, Unicode, MetaData, create_engine
#from sqlalchemy.orm import mapper, create_session
#
#
#from apps.bi import JobRawTopic
#
#
#topic = JobRawTopic()
#
#
#
#
#wordColumns = ['english', 'korean', 'romanian']
#e = create_engine('sqlite://')
#metadata = MetaData(bind=e)
#
#t = Table('words', metadata, Column('id', Integer, primary_key=True),
#	*(Column(wordCol, Unicode(255)) for wordCol in wordColumns))
#metadata.create_all()
#mapper(Word, t)
#session = create_session(bind=e, autocommit=False, autoflush=True)
#
#w = Word()
#w.english = u'name'
#w.korean = u'이름'
#w.romanian = u'nume'
#
#session.add(w)
#session.commit()
#
#w = session.query(Word).filter_by(english=u'name').one()
#print w.romanian
#
#language = 'korean'
#print getattr(w, language)