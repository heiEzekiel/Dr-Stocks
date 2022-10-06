var url = "localhost";


function b64EncodeUnicode(str) {
    return btoa(encodeURIComponent(str));
};

function UnicodeDecodeB64(str) {
    return decodeURIComponent(atob(str));
};


async function getAjax(url, method){
    return $.ajax({
        url: url,
        type: method || 'GET',
        dataType: 'json',
    });
}

async function login(){
    var loginURL = "http://"+url+":8000/api/v1/login";

    var email = document.getElementById('inputEmail').value;
    var password = document.getElementById('inputPassword').value;
    var send_email =  "email" + "=" + email;
    var send_password = "password" + "=" + b64EncodeUnicode(password);
    var params = "?" + send_email + "&" + send_password;
    const website = loginURL + params;
    try {
        const result = await getAjax(website, 'GET');
        if (result.code === 200) {
            var apikey = result["data"]["apikey"];
            var accid = b64EncodeUnicode(result["data"]["accid"]);
            var email = result["data"]["email"];
            sessionStorage.setItem("apikey", apikey);
            sessionStorage.setItem("accid", accid);
            sessionStorage.setItem("email", email);
            window.location.replace("dashboard.html");
        }
    } catch (error) {
        alert("Wrong email or password");
    }
}