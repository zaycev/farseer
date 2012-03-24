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
			url: "/apps/collector/api/v0/call",
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
				}, 300);
			},
			error: function(data){
				_this.html();
				_this.html("<img src='/www/icons/tick.png'/>");
				setTimeout(function(){
					_this.attr("disabled", false);
					_this.html(_html);
				}, 300);

			}
		})
	}
};