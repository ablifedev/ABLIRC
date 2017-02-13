/**
 * 1.1.1 = 1*100*100 + 1*100 + 1
 * 1.2.2 = 1*100*100 + 2*100 + 3
 *
 * 1 = 0*100 +1
 */
function encode_id_with_array(opts,arr) {
	var result = 0;
  for(var z = 0; z < arr.length; z++ ) {
		result += factor(opts, arr.length - z ,arr[z]);
  }

	return result;
}


/**
 * 1.1.1 = 1*100*100 + 1*100 + 1
 * 1.2.2 = 1*100*100 + 2*100 + 3
 *
 * 1 = 0*100 +1

	1,1 = 100

 */
function get_parent_id_with_array(opts,arr) {
	var result_arr = [];

  for(var z = 0; z < arr.length; z++ ) {
		result_arr.push(arr[z]);
  }

	result_arr.pop();

	var result = 0;
  for(var z = 0; z < result_arr.length; z++ ) {
		result += factor(opts,result_arr.length - z,result_arr[z]);
  }

	return result;
}

function factor(opts ,count,current) {
	if(1 == count) {
		return current;
	}

	var str = '';
	for(var i = count - 1;i > 0; i-- ) {
		str += current * opts.step+'*';
	}

	return eval( str + '1' );
}

;(function($) {
	/*
	 *   header
	 */
	function create_toc(opts) {
		$(opts.documment_selector).find(':header').each(function() {
			var level = parseInt(this.nodeName.substring(1), 10);
			var origin_title = $.trim($(this).text());
			
			_rename_header_content(opts,this,level);
			
			_add_header_node(opts,$(this),level,origin_title);
		});//end each
	}

	/*
	 *   header
	 */
	function render_with_headers(opts) {
		opts.render_before(opts);
	 	return compile_headers(opts);
	}
	
	/*
	 *   header
	 */
	function compile_headers(opts) {
		var result = opts._header_nodes;
		var html = '';
		
		for(var i in result){
			var item = result[i];
			// compile with template
			html += opts.compile_headers_with_item(item);
		}
		
		opts.render_after(opts, html);
	 	return html;
	}


	/*
	 *    header  ，
	 */
	function _rename_header_content(opts ,header_obj ,level) {
		if(opts._headers.length == level) {
			opts._headers[level - 1]++;
		} else if(opts._headers.length > level) {
			opts._headers = opts._headers.slice(0, level);
			opts._headers[level - 1] ++;
		} else if(opts._headers.length < level) {
			for(var i = 0; i < (level - opts._headers.length); i++) {
			  // console.log('push 1');
			  opts._headers.push(1);
			}
		}

		if(opts.is_auto_number == true) {
			//           ，
			if($(header_obj).text().indexOf( opts._headers.join('.') ) != -1){

			}else{
				$(header_obj).text(opts._headers.join('.') + '. ' + $(header_obj).text());
			}
		}
	}
	
	/*
	 * create table with head for anchor for example: <h2 id="#Linux  ">Linux  </h2>
	 * this method can get a headable anchor
	 * add by https://github.com/chanble
	 */
	function _get_anchor_from_head(header_obj){
		var name = header_obj.html();
		var aname = name.split('.');
		var anchor = aname.pop().trim();
		return anchor;
	}

	/*
	 *  ztree  header_nodes
	 */
	function _add_header_node(opts ,header_obj, level, origin_title) {
		var id  = encode_id_with_array(opts,opts._headers);//for ztree
		var pid = get_parent_id_with_array(opts,opts._headers);//for ztree
		var anchor = id;//use_head_anchor.html#

		//         anchor
		if(opts.use_head_anchor == true){
			anchor = _get_anchor_from_head(header_obj);
		}
		
    //     id
		$(header_obj).attr('id',anchor);

		log($(header_obj).text());

		opts._header_offsets.push($(header_obj).offset().top - opts.highlight_offset);

		log('h offset ='+( $(header_obj).offset().top - opts.highlight_offset ) );

		opts._header_nodes.push({
			id					: id,
			level				: level,
			pId					: pid ,
			orderd_title				: $(header_obj).text()||'null',
			origin_title: origin_title,
			open				: true,
			url					: '#'+ anchor,
			target			: '_self'
		});
	}

	/*
	 *           ，   ztree
	 */
	function bind_scroll_event_and_update_postion(opts) {
		var timeout;
	    var highlight_on_scroll = function(e) {
			if (timeout) {
				clearTimeout(timeout);
			}

			timeout = setTimeout(function() {
				var top = $(opts.scroll_selector).scrollTop(),highlighted;

				if(opts.debug) console.log('top='+top);

				for (var i = 0, c = opts._header_offsets.length; i < c; i++) {
					// fixed: top+5    ztree   ，
					if (opts._header_offsets[i] >= (top + 5) ) {
						console.log('opts._header_offsets['+ i +'] = '+opts._header_offsets[i]);
						$('a').removeClass('curSelectedNode');

						//    root  ，  i   1
				  		var obj = $('#tree_' + (i+1) + '_a').addClass('curSelectedNode');
						break;
					}
				}
			}, opts.refresh_scroll_time);
		};

	  if (opts.highlight_on_scroll) {
	    $(opts.scroll_selector).bind('scroll', highlight_on_scroll);
	    highlight_on_scroll();
	  }
	}
	/*
	 *
	 */
	function init_with_middlewares(opts){
		var middlewares = opts.middlewares;
		for(o in middlewares){
			middlewares[o](opts);
		}
	}

	/*
	 *
	 */
	function init_with_config(opts) {
		opts.highlight_offset = $(opts.documment_selector).offset().top;
	}

	/*
	 *
	 */
	function log(str) {
		if($.fn.markdown_toc.defaults.debug == true) {
			console.log(str);
		}
	}

	$.fn.markdown_toc = function(options) {
		//  defaults   options      {}
		var opts = $.extend({},$.fn.markdown_toc.defaults,options);

		return this.each(function() {
			opts._zTree = $(this);

			//
			init_with_config(opts);
			
			//    middlewares
			init_with_middlewares(opts);

			//   table of content，     _headers
			create_toc(opts);

			//   _headers  ztree
			render_with_headers(opts);

			//           ，   ztree
		    // bind_scroll_event_and_update_postion(opts);
		});
		// each end
	}

	//
	$.fn.markdown_toc.defaults = {
		_zTree: null,
		_headers: [],
		_header_offsets: [],
		_header_nodes: [{ id:1, pId:0, orderd_title:"Table of Content",open:true}],
		debug: false,
		/*
		 *       anchor
		 * create table with head for anchor for example: <h2 id="#Linux  ">Linux  </h2>
		 *         ，       ，       ，
		 *       false，
		 */
		use_head_anchor: false,
    scroll_selector: 'window',
		highlight_offset: 0,
		highlight_on_scroll: true,
		/*
		 *              ，   50
		 */
		refresh_scroll_time: 50,
		documment_selector: 'body',
		render_before:function(opts){
			
		},
		render_after:function(opts,compiled_html){
			$(opts._zTree).html("<ul>" + compiled_html  +"</ul>");
		},
		/*
		 *
		 */
		middlewares:[
			function(opts){
				console.log('aaaaaa');
			},
			function(opts){
				console.log('bbbbbb');
			}
		],
		/**
		{id: 2105 ,level:1,orderd_title: "21.5.       ",origin_title:"      ", open: true,  pId: 21 ,target: "_self", url: "#2105"}
	
		function compile_headers_with_item(item) {
			return "<li>" + item.name + "<li>"
		}
		**/
		compile_headers_with_item:function(item){
			return " <h"+item.level +"><a href='#" +item.id+ "'>" + item.orderd_title + "</a></h"+item.level +">"
		},
		/*
		 * ztree   ，
		 */
		is_posion_top: true,
		/*
		 *       header
		 */
		is_auto_number: false,
		/*
		 *
		 */
		is_expand_all: true,
		/*
		 *       ，
		 */
		is_highlight_selected_line: true,
		step: 100 
	};

})(jQuery);
