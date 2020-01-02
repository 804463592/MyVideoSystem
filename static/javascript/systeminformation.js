
var date;
var isNext=false;
$(document).ready(function(){
    $.ajax({
        "url": "/app/systeminformation/",    //提交URL
        "type": "Post",//处理方式
        "data": {},//提交的数据
        "dataType": "json",//指定返回的数据格式
        "success": callback,//执行成功后的回调函数
        "async": "true",//是否同步
        //错误后执行
        "error": function () {
        }

    });

    function callback(data) {
        date = data;
        isNext = true
    }

    // callback();
    // setInterval(callback,1000);
    function gettime() {
        if(isNext)
        {
            var init_time = document.getElementById("init_time");
            var duration = document.getElementById("duration");
            var current_date = new Date();
            data_list1 = date.split("-");
            var start_year = data_list1[0];
            var start_month = data_list1[1];
            data_list2 = data_list1[2].split("T");
            var start_day = data_list2[0];
            data_list3 = data_list2[1].split(":");
            var start_hour = data_list3[0];
            var start_minute = data_list3[1];
            var start_second = data_list3[2];

            var dateBegin = new Date(date.replace(/T/g, " "));
            var dateDiff = current_date.getTime() - dateBegin.getTime();
            var dayDiff = Math.floor(dateDiff / (24 * 3600 * 1000));//计算出相差天数
            var leave1=dateDiff%(24*3600*1000); //计算天数后剩余的毫秒数
            var hours=Math.floor(leave1/(3600*1000));//计算出小时数
            //计算相差分钟数
            var leave2=leave1%(3600*1000);//计算小时数后剩余的毫秒数
            var minutes=Math.floor(leave2/(60*1000));//计算相差分钟数
            //计算相差秒数
            var leave3=leave2%(60*1000); //计算分钟数后剩余的毫秒数
            var seconds=Math.round(leave3/1000);
            // console.log(dateDiff+"时间差的毫秒数",dayDiff+"计算出相差天数",leave1+"计算天数后剩余的毫秒数"
            // ,hours+"计算出小时数",minutes+"计算相差分钟数",seconds+"计算相差秒数");

            init_time.innerHTML = start_year + "年" + start_month + "月" + start_day + "日" + start_hour + "时" + start_minute + "分" + Math.floor(start_second)+ "秒";
            duration.innerHTML = dayDiff+"天 "+hours+"小时 "+minutes+" 分钟"+seconds+" 秒";

        }

    }
    gettime();
    setInterval(gettime,1000);

});