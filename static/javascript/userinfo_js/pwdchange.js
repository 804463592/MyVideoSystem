//TODO:注册完成之后,跳转到登录界面,然后点击浏览器左上角的返回上一页,由于用户名和邮箱存在,直接点击注册,会出现异常
var isError = true;

$(function () {
    var oError = document.getElementById("error_box");//这是提示错误的信息
    var success = false;

    //校验用户名是否重复及格式是否满足要求
    var $username = $("#username_input");
    $username.change(function () {
        var username = $username.val().trim();//获取到username的值,.trim()去除左右两边的空格
        var $username_info = $("#username_info");//用户名的提示信息

        if (username.length)//若输入用户名长度大于0
        {
            //将用户名发送服务器进行预校验
            $.getJSON("/app/checkuser/",{'username':username},function (data) {
                console.log(data);

                if(data['status'] ==200) //当用户名唯一
                {
                    oError.innerHTML = " ";

                    //当用户名满足唯一,先判断长度
                    if (username.length<5||username.length>10) {
                        oError.innerHTML = "用户名要5-10位字符或数字";
                        isError = false
                        return
                    }

                    //判断首字母是否为数字
                    else if (username.charCodeAt(0) >= 48 && (username.charCodeAt(0) <= 57)) {
                        oError.innerHTML = "用户名首位不能为数字";
                        isError = false
                        return
                    }

                    //判断是不是只有数字和字母
                    else for (var i = 0; i < username.length; i++)
                    {
                        if ((username.charCodeAt(i) < 48) || (username.charCodeAt(i) > 57) && (username.charCodeAt(i) < 58) && (username.charCodeAt(i) > 97))
                        {
                        oError.innerHTML = "用户名只能为数字和字母";
                        isError = false
                        }
                    }
                }

                if(data['status'] ==901){
                    oError.innerHTML = "用户名已存在";
                    //$username_info.html("用户名已存在").css("color","red");
                    //return
                }
            })
        }
    })


    //密码的格式是否符合要求
    var $password = $("#password_input");
    $password.change(function () {
        var password = $password.val().trim();

        if (password.length<3)
        {
            console.log(password);
            oError.innerHTML = "密码不少于3位";
            isError = false;
        }
        else
        {
            console.log(password);
            oError.innerHTML = "";
            isError = false;
        }
    })

    //验证密码
    var $password = $("#password_input");
    var $password_confirm = $("#password_confirm_input");
    $password_confirm.change(function () {
        var password_confirm = $password_confirm.val();
        var password = $password.val();

        if (password != password_confirm)
        {
            console.log(password_confirm);
            oError.innerHTML = "设置密码和验证密码不一致";
            isError = false;
        }
        else
        {
            console.log(password_confirm);
            isError = true;
        }
    })
})

function check() {
    var oError = document.getElementById("error_box");//这是提示错误的信息
    var success = false;

    var $username = $("#username_input");
    var username = $username.val().trim();
    if(username.length==0)
    {
        oError.innerHTML = "    ";
        oError.innerHTML = " ";
    }

    if(isError == false)
    {
        return false
    }
    else
    {
        oError.innerHTML = "注册成功!";
        return true
    }
}
