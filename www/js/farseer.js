var Farseer = {
	Collector: Object
};

Farseer.Collector.call = function(address, func, make_args, callback) {
	return function() {
		var _this = $(this);
		var _html = _this.html();
		_this.html("<img src='/www/loader.gif'/>");

		_this.attr("disabled", "disabled");
		$.ajax({
			method: "GET",
			url: "/apps/collector/api/v0/service/call.json",
			dataType: "json",
			data: {
				address: address,
				func: func,
				args: $.toJSON(make_args())
			},
			success: function(data){
				_this.html();
				_this.html("<img src='/www/icons/tick.png'/>");
				setTimeout(function(){
					_this.attr("disabled", false);
					_this.html(_html);
					if (callback) callback(data);
				}, 300);
			},
			error: function(data){
				_this.html();
				_this.html("<img src='/www/icons/tick.png'/>");
				setTimeout(function(){
					_this.attr("disabled", false);
					_this.html(_html);
					if (callback) callback(data);
				}, 300);

			}
		})
	}
};


Farseer.Collector.get_model = function(model_name, instance_id, callback) {
	$.ajax({
		method:"GET",
		url:"/apps/collector/api/v0/model/get.json",
		dataType:"json",
		data:{
			model: model_name,
			id: instance_id
		},
		success: callback
	});
};

Farseer.Collector.get_model = function(model_name, instance_id, dataset_id, callback) {
	$.ajax({
		method:"GET",
		url:"/apps/collector/api/v0/model/get.json",
		dataType:"json",
		data:{
			model: model_name,
			id: instance_id,
			dataset: dataset_id
		},
		success: callback
	});
};

Farseer.Collector.list_model = function(model_name, dataset, limit, offset, callback) {
	$.ajax({
		method:"GET",
		url:"/apps/collector/api/v0/model/list.json",
		dataType:"json",
		data:{
			model: model_name,
			dataset: dataset,
			limit: limit,
			offset: offset
		},
		success: callback
	});
};

