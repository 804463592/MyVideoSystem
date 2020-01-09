function check() {
    var oError1 = document.getElementById("error_box1");//这是提示错误的信息
    // var oError2 = document.getElementById("error_box2");//这是提示正确的信息

    var password1 = document.getElementById("password1");
    var password2 = document.getElementById("password2");
    var password2_confirm = document.getElementById("password2_confirm");

    password1 = password1.value;
    password2 = password2.value;
    password2_confirm = password2_confirm.value;

    // var password1 = $password1.val().trim();

    //判断原密码是否相同
    $.ajax({
            "url": "/app/pwdchange/",    //提交URL
            "type": "POST",//处理方式
            "data": {
                "user_newpassword": password2
            },//提交的数据
            "dataType": "json",//指定返回的数据格式
            "success": function (data) {
                oldpassword = data['oldpassword']
                console.log(oldpassword);

                if(oldpassword != password1.trim())
                 {
                    // console.log(oldpassword);
                    oError1.innerHTML = "原密码输入不正确";
                    return
                 }

            },//执行成功后的回调函数
            "async": "true",//是否同步
            //错误后执行
            "error": function () {
                alert("失败")
            }
        });


    //新密码的长度要是6-10位数字和字母的组合
    if (password2.length < 6 || password2.length > 10) {
        console.log(password2);
        oError1.innerHTML = "新密码的长度为6-10位";
        return
    }

     //判断是否只有数字和字母
    else for (var i = 0; i < password2.length; i++)
    {
        if ((password2.charCodeAt(i) < 48) || (password2.charCodeAt(i) > 57) && (password2.charCodeAt(i) < 58) && (password2.charCodeAt(i) > 97))
        {
            oError1.innerHTML = "密码只能为数字和字母";
            return;
        }
    }

    //判断验证的密码是否和输入新密码相同
    if (password2.trim() != password2_confirm.trim()) {
        console.log(password2_confirm);
        oError1.innerHTML = "设置密码和验证密码不一致";
    }
    else
    {
        oError1.innerHTML = "修改密码成功";
        console.log("一致");
        // setTimeout("window.location=('index.php'",3000);
        // setTimeout("window.location.href='/static/basictemplates/login3.html'",3000);
        // window.setTimeout("alert('Hello, world')", 1000);
        //setTimeout("window.location.url='app:login'",30);
        // setTimeout(go, 3000);
        window.history.back(-1);
    }
}
// function go()
// {
//     location.href="login";
// }
