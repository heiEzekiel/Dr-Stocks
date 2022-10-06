var url = "localhost";

function b64EncodeUnicode(str) {
    return btoa(encodeURIComponent(str));
};

function UnicodeDecodeB64(str) {
    return decodeURIComponent(atob(str));
};

$(window).on('load', function() {
    var apikey = sessionStorage.getItem("apikey");
    var accid = sessionStorage.getItem("accid");
    get_acc_bal(accid, apikey);
    getAccDetails(accid, apikey);
});

async function getAjax(url, method){
    return $.ajax({
        url: url,
        type: method || 'GET',
        dataType: 'json',
    });
}

async function getAccDetails(accid, apikey){
    var accid = UnicodeDecodeB64(accid);
    var apikey = UnicodeDecodeB64(apikey);
    var accURL = 'http://' + url + ':8000/api/v1/account/email/';
    var email = String(sessionStorage.getItem("email"));
    var params = "?apikey=" + apikey;
    const website = accURL + email + params;
    try {
        const result = await getAjax(website, 'GET');
        if (result.code === 200) {
            var acc_name = "Name: ";
            var acc_email =  "Email: ";
            var acc_id =  "Account ID: ";
            var acc_trade_id =  "Trading Account: ";
            document.getElementById("acc_name").textContent = acc_name + result["data"]["name"];
            document.getElementById("acc_email").textContent = acc_email  + result["data"]["email"];
            document.getElementById("acc_id").textContent = acc_id + result["data"]["accid"];
            document.getElementById("acc_trade_id").textContent = acc_trade_id + result["data"]["trade_accid"];
        }
    }
    catch (error) {
    }
}

async function get_acc_bal(accid, apikey){
    var accid = UnicodeDecodeB64(accid);
    var apikey = UnicodeDecodeB64(apikey);
    var currency = sessionStorage.getItem("currency");
    try {
        var tradeaccURL = 'http://' + url + ':8000/api/v1/trading_acc/';
        var params = "?apikey=" + apikey;
        const website = tradeaccURL + accid + "/" + currency + params;
        const result = await getAjax(website, 'GET');
        if (result.code === 200) {
            var acc_bal = document.getElementById('acc_bal');
            document.getElementById('main_acc_bal').textContent = "$" + String(parseFloat(result["data"]["trade_acc_balance"]).toFixed(2));
            var user_acc_bal = "Total Assets: " + "$" + String(parseFloat(result["data"]["trade_acc_balance"]).toFixed(2));
            acc_bal.textContent = user_acc_bal;
        }
    } catch (error) {
    }
};

async function postAjax(url, method, data){
    return $.ajax({
        url: url,
        type: method || 'POST',
        crossDomain: true,
        data: JSON.stringify(data),
        dataType: "json"
    });
};

async function make_deposit(amount){
    var accid = UnicodeDecodeB64(sessionStorage.getItem("accid"));
    var apikey = UnicodeDecodeB64(sessionStorage.getItem("apikey"));
    var email = sessionStorage.getItem("email");
    var deposit_amt = Number(amount);
    var currency = sessionStorage.getItem("currency");
    var transaction_action = "DEPOSIT";
    try {
        var depositURL = 'http://' + url + ':8000/api/v1/make_deposit';
        var params = "?apikey=" + apikey;
        var data = {
            "email":email,
            "amount":deposit_amt,
            "transaction_action":transaction_action,
            "currency":currency
        };
        const website = depositURL + params;
        const result = await postAjax(website, 'POST', data);
        if (result.code === 201) {
            var accid = sessionStorage.getItem("accid");
            var apikey = sessionStorage.getItem("apikey");
            get_acc_bal(accid, apikey);
            alert("Deposit Successful");
        }
    } catch (error) {
        alert("Error in deposit, please try again later");
    }
}