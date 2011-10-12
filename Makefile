all:
	@protoc --python_out=./ protobuff.proto
	@protoc --proto_path=./ --python_out=./ apps/bi/bi.proto