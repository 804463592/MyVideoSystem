$(document).ready(function(){

   // 开始写 jQuery 代码...

    $("#queryvideo").click(function() {

        var tablebody =window.document.getElementById("ttt");
        var tablehead = window.document.getElementById("t_head")

        tablebody.innerHTML ="";
        tablehead.innerHTML ="";

        var date =document.getElementById("date").value;
        var time =document.getElementById("searchstarttime").value;

        date_list =date.split("-");
        time_list =time.split(":");

        year =date_list[0];
        month =date_list[1];
        day =date_list[2];

        hour =time_list[0];
        minute =time_list[1];

        $.ajax({
            // "url": "/app/videoanalysis/objectdetection_playback/",    //提交URL
            "url": "/app/videolookback/",
            "type": "Post",//处理方式
            "data":{
                    "year":year,
                    "month":month,
                    "day":day,
                    "hour":hour,
                    "minute":minute
                },//提交的数据
            "dataType" : "json",//指定返回的数据格式
            "success" : callback,//执行成功后的回调函数
            "async" : "true",//是否同步
            //错误后执行
            "error" : function() {
                alert("没有查询到数据,请重新选择时间！")
            }

        });

        function callback(result) {
            // result = eval(result);
            // result = r esult[0];
            //alert("返回数据成功！！！！:"+ "\n" + " first start_name:" + Object.keys(result).length);

            var strhtml ="";
            var strhead ="";
            var i;

            strhead = "<tr>\n" +
                "<th>序号</th>\n" +
                "<th>摄像机</th>\n" +
                "<th>开始时间</th>\n" +
                "<th>结束时间</th>\n" +
                "<th>视频名称</th>\n" +
                "<th>视频操作</th>\n" +
                "</tr>";
            tablehead.innerHTML =strhead;


            for (i=0; i < Object.keys(result).length; i++) {

                var video_url ="/app/videoanalysis/videoplay/?video_file_name="+result[i]["video_file"]
                +"&video_camera_name="+result[i]["camera_name"]
                +"&video_start_time="+result[i]["start_time"]
                +"&video_end_time="+result[i]["end_time"];

                //var video_url ="/static/videoStorage/realVideo/20191220152030.mp4"
                //var video_url ="/static/transferStation/video0.avi";

                //去掉视频名字的路径前缀,便于只显示视频名字
                var split_str =  result[i]["video_file"].split("/");
                var video_file_name =split_str[split_str.length-1];

                var t =i+1;
                strhtml +="<tr>"+
                    "<td>"+t+"</td>"+
                    "<td>"+result[i]["camera_name"]+"</td>"+
                    "<td>"+result[i]["start_time"]+"</td>"+
                    "<td>"+result[i]["end_time"]+"</td>"+
                    "<td>"+video_file_name+"</td>"+
                    "<td><button><a href="+
                    "'"+video_url+"'"+
                    ">检测</a></button>"+
                    // "<button><a href="+'/static/videoStorage/'+result[i]["video_file"]+">下载</a></button> </td>"+
                    "</tr>";
            }

            tablebody.innerHTML =strhtml;

             $('#mytable').DataTable({//注意,html中的<thead></thead>标签必不可少

                             //其他参数可参考：https://blog.csdn.net/lijunxian0114/article/details/79109138

                             //bJQueryUI:true,
                            "scrollX": "800%",
                             // sScrollY:"400px",
                            "scrollY": 400,

                            //是否允许搜索
                            "searching": true,
                            // 件数选择下拉框内容,前面为值,后面的为下拉框内容的显示
                            "lengthMenu": [[-1,10, 25, 50],["all",10, 25, 50]],

                            //自动单列宽
                            "autoWidth": false,

                            "bAutoWidth": false,//自动整个表格的宽度

                            //这个destroy参数很重要,因为需要多次初始化，所以需要设置允许销毁实例
                            "destroy": true,
                            "bDestroy": true,

                            // 翻页按钮文字控制
                            "pagingType": "full_numbers",

                            "oLanguage":
                            {
                                "sSearch":"搜索表格：",
                                "sLengthMenu": "每页显示 _MENU_条数据",
                                "sZeroRecords": "抱歉,没有找到!",
                                "sInfo": "第_START_到_END_ /共_TOTAL_条数据",
                                "sInfoEmpty": "没有数据",
                                "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
                                "oPaginate":
                                    { "sFirst": "首页",
                                      "sPrevious": "前一页",
                                      "sNext": "后一页",
                                      "sLast": "尾页",
                                    },
                             //"sZeroRecords": "没有检索到数据",
                            }
                        });

        }

    })

});
