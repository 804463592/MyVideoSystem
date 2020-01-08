
//TODO:注册完成之后,跳转到登录界面,用户名和邮箱存在,直接点击注册,会出现异常

var isusername = true;
var isemail = true;
var ispassword = true;
var ispassword_confirm = true;

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
                        isusername = false
                    }

                    //判断首字母是否为数字
                    if (username.charCodeAt(0) >= 48 && (username.charCodeAt(0) <= 57)) {
                        oError.innerHTML = "用户名首位不能为数字";
                        isusername = false
                    }

                    //判断是不是只有数字和字母
                    for (var i = 0; i < username.length; i++)
                    {
                        if ((username.charCodeAt(i) < 48) || (username.charCodeAt(i) > 57) && (username.charCodeAt(i) < 58) && (username.charCodeAt(i) > 97))
                        {
                            oError.innerHTML = "用户名只能为数字和字母";
                            isusername = false
                        }
                    }
                }

                if(data['status'] ==901){
                    oError.innerHTML = "用户名已存在";
                    isusername = false
                }
            })
        }
    })

    //校验邮箱是否重复及格式是否正确
    var $email = $("#email_input");
    $email.change(function () {
        var email = $email.val().trim();//获取到email的值,.trim()去除左右两边的空格

        if (email.length)
        {
            //将邮箱发送服务器进行预校验
            $.getJSON("/app/checkemail/",{'email':email},function (data)
            {
                console.log(data);

                if(data['status'] == 200)
                {
                    oError.innerHTML = " ";
                    //当邮箱唯一可用时,判断邮箱格式是否正确
                    var reg = /^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$/;
                    isok = reg.test(email);
                    if (!isok)
                    {
                       console.log("邮箱不正确");
                       oError.innerHTML = "邮箱格式不正确";
                       isemail = false;
                    }
                }

                if(data['status'] == 901)
                {
                    oError.innerHTML = "该邮箱已存在";
                    isemail = false
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
            oError.innerHTML = "密码要大于3位小于15位";
            ispassword = false;
        }
        for (var i = 0; i < password.length; i++)
        {
            if ((password.charCodeAt(i) < 48) || (password.charCodeAt(i) > 57) && (password.charCodeAt(i) < 58) && (password.charCodeAt(i) > 97))
            {
                oError.innerHTML = "密码只能为数字和字母";
                ispassword = false
            }
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
            ispassword_confirm = false;
        }
        else
        {
            ispassword_confirm = true;
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
       isusername = false
    }

    if(isusername == false||isemail == false||ispassword == false || ispassword_confirm == false)
    {
        success = false;
    }
    else
    {
        success = true;
    }

    if(success == false)
    {
        oError.innerHTML = "注册失败!";
        return false
    }
    else(success == true)
    {
        oError.innerHTML = "注册成功!";
        return true
    }
}
