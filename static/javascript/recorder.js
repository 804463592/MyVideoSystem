
//标志位
var is_download =false
var is_play =true
var is_record =false

//设置四个按钮
var buttonStartVideo =document.getElementById("startvideo")
var buttonSuspendVideo =document.getElementById("suspendvideo")

var buttonRecord = document.getElementById("record");
var buttonStop = document.getElementById("stop");

// 设置下载链接
var downloadLink = document.getElementById("download");

//找到图片的ID
var img_video =document.getElementById("video")
img_video.onclick =function () {
    //录制，则不做操作,正在播放，则暂停，否则开始播放
    if(!is_record)
    {
        if(is_play) {
            suspendPlay();
        }
        else {
            startPlay();
        }
    }
};

function getCookie(name){
    var arr,reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)");

    if(arr=document.cookie.match(reg))

        return unescape(arr[2]);
    else
        return null;
}

function sendJsonRequest(method ="POST",url ="/app/recordstatus/",commandline ="start_play",alert_words = "一切正常")
{
     // XMLHttpRequest
     var xhr = new XMLHttpRequest();
     xhr.onreadystatechange = function () {
         if (xhr.readyState == 4 && xhr.status == 200) {
             //alert(xhr.responseText);
             //alert(alert_words)
         }
     }
     xhr.open(method, url,true);
     xhr.setRequestHeader("X-CSRFToken",getCookie("csrftoken"));  //设置csrf头，否则后面中间件csrf处报错
     xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
     xhr.send(JSON.stringify({status: commandline}));
}


buttonStartVideo.disabled =true;
buttonSuspendVideo.disabled =false;

buttonStartVideo.onclick =startPlay;  //不能带括号，不能写成 = startFun()
function startPlay(){

    is_play =true;
    buttonStartVideo.disabled =true;
    buttonSuspendVideo.disabled =false;
    //录制视频生效，停止录制仍然要失效
    buttonRecord.disabled =false;
    buttonStop.disabled =true;

    //如果我们这里ajax已经下载了视频，则刷新页面，否则，则向后端发post请求，打开ret标志，返回视频
    if(is_download){
        window.location.reload();  //刷新页面,监控视频才能再次继续
        is_download =false;
    }
    sendJsonRequest("POST","/app/playstatus/","start_play");
}

buttonSuspendVideo.onclick =suspendPlay;
function suspendPlay()
{
    is_play =false;
    buttonStartVideo.disabled =false;
    buttonSuspendVideo.disabled =true;

    //录制视频和停止录制按钮全部失效
    buttonRecord.disabled =true;
    buttonStop.disabled =true;

    //向后端发送post请求，关闭is_paly标志,不返回视频
    sendJsonRequest("POST","/app/playstatus/","suspend_play");
}

buttonStop.disabled = true;
buttonRecord.onclick = function () {

    // var url = window.location.href + "record_status";
    buttonStartVideo.disabled =true;
    buttonSuspendVideo.disabled =true;

    buttonRecord.disabled = true;
    buttonStop.disabled = false;

    //录制时候,只允许点击结束录制,结束录制，才允许点击其他的
    is_record =true;

    sendJsonRequest("POST","/app/recordstatus/","start_record");
};

buttonStop.onclick = function () {

    //结束录制，只允许点击开始播放按钮(或者点击播放窗口)
    buttonStartVideo.disabled =false;
    is_record =false;

    buttonSuspendVideo.disabled =true;
    buttonRecord.disabled = true;
    buttonStop.disabled = true;

    // XMLHttpRequest
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
         if (xhr.readyState == 4 && xhr.status == 200) {
             //alert(xhr.responseText);
             //alert("停止，一切正常")
            downloadLink.innerHTML ="点击下载录制的视频";
            downloadLink.href = "/static/video.avi";
            downloadLink.style.color ="red";
        }
    }
    xhr.open("POST", "/app/recordstatus/",true);
    xhr.setRequestHeader("X-CSRFToken",getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({status: "stop_record"}));

};

downloadLink.onclick =function () {

     //更新标志位
    is_download =true

    buttonStartVideo.disabled =false;
    buttonSuspendVideo.disabled =true;

    //录制视频生效，停止录制仍然要失效
    buttonRecord.disabled =true;
    buttonStop.disabled =true;
}



