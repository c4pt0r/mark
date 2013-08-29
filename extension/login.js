$(document).ready(function(){
        $('#login-btn').click(function(){
            var email = $('#email').val();
            var password = $('#password').val();

            $.post('http://localhost:5000/user/login', {email:email, password:password}, function(d){
                var data = JSON.parse(d);
                if (data.ret == 0) {
                    storage('token', data.token)
                    location.href="./popup.html";
                } else {
                    alert(data.msg);
                    $('#password').val('');
                    $('#password').focus();
                }
            })
        })
    })