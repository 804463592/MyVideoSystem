$(document).ready(function(){

   // 开始写 jQuery 代码...

    $("#upload").click(function() {
        $(this).attr('disabled',1);

        $.ajax({
            "url": "/app/configuration/",    //提交URL
            "type": "POST",//处理方式
            "data": {
                "capacity": $("#video_capacity option:selected").val(),
                "length": $("#video_length option:selected").val(),
                "fps": $("#video_fps option:selected").val()
            },//提交的数据
            "dataType": "json",//指定返回的数据格式
            "success": function (data) {
                alert(data['msg'])
            },//执行成功后的回调函数
            "async": "true",//是否同步
            //错误后执行
            "error": function () {
                alert("失败")
            }

        });
    });

});