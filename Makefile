all:
	@protoc --python_out=./ collector.proto
	@protoc --proto_path=./ --python_out=./ distr.bi/protocol.proto
clean:
	@rm -f *.pyc
	@rm -f */*.pyc
	@rm -f */*/*.pyc
	@rm -f */*/*/*.pyc
	@rm -f *.logfile
	@rm -rf *__pycache__
	@rm -f *_pb2.py
	@rm -f */*_pb2.py
	@rm -f */*/*_pb2.py
	@rm -f */*/*/*_pb2.py
	@rm -f */*/*/*/*_pb2.py