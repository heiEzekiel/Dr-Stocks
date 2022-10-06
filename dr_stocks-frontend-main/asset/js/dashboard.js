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
    get_stock_company_info(apikey);
    get_user_stock(accid, apikey);
    get_stock_info(apikey);
    get_stock_pref(accid, apikey);
    repeat();
    get_acc_bal(accid, apikey);
});

function checktime(){
    const d = new Date();
    var current_time = d.getUTCHours() + ":" + d.getUTCMinutes();
    var start_time = "13:30";
    var end_time = "20:00";
    if (current_time > start_time && current_time < end_time){
        return true;
    }
    return false;
}

function repeat(){
    if (checktime()){
        setTimeout(repeat, 10000);
        var apikey = sessionStorage.getItem("apikey");
        get_stock_info(apikey);
    }else{
        document.getElementById("transaction_action").disabled = true;
    }
}

function get_stock(symbol){
    sessionStorage.setItem("previous_stock_symbol", document.getElementById('stock_symbol').textContent )
    document.getElementById('stock_symbol').textContent = symbol;
    var apikey = sessionStorage.getItem("apikey");
    get_stock_company_info(apikey);
    get_stock_info(apikey);
    document.getElementById("stock_company").textContent = sessionStorage.getItem("company_name");
}

function logout(){
    sessionStorage.clear();
    window.location.replace("index.html");
};


async function getAjax(url, method){
    return $.ajax({
        url: url,
        type: method || 'GET',
        dataType: 'json',
        crossDomain: true
    });
};

async function get_user_stock(accid, apikey){
    $('#user_stocks_table_body tr').remove();
    var accid = UnicodeDecodeB64(accid);
    var apikey = UnicodeDecodeB64(apikey);
    var loginURL = 'http://' + url + ':8000/api/v1/user_stock/';
    var params = "?apikey=" + apikey;
    const website = loginURL + accid + params;
    try {
        const result = await getAjax(website, 'GET');
        if (result.code === 200) {
            var user_stocks = result["user_stocks"];
            var rows = "";
                for (const stock of user_stocks) {
                    eachRow ="<td>" + stock.user_stockid + "</td>" +
                                "<td>" + stock.accid + "</td>" +
                                "<td>" + stock.tradeid + "</td>" +
                                "<td>" + stock.stock_symbol + "</td>"+
                                "<td>" + stock.stock_quantity + "</td>" +
                                "<td>" + "$" + stock.purchased_price + "</td>" +
                                "<td>" + stock.currency + "</td>";
                    rows += "<tr>" + eachRow + "</tr>";
                }
                    // add all the rows to the table
                $('#user_stocks_table_body').append(rows);
        }
    } catch (error) {
    }
};

function stock_status(current, close){
    if (current > close){
        return "text-success";
    }
    return "text-danger";
};

async function get_stock_info(apikey){
    try {
        var stockURL = 'http://' + url + ':8000/api/v1/stock_info/';
        var stock_symbol = document.getElementById('stock_symbol').textContent;
        document.getElementById("stock_company").textContent = sessionStorage.getItem("company_name");
        var apikey = UnicodeDecodeB64(apikey);
        var params = "?apikey=" + apikey;
        const website = stockURL + stock_symbol + params;
        const result = await getAjax(website, 'GET');
        if (result.code === 200) {
            var stock_info = result["data"];
            var status = stock_status(stock_info.c, stock_info.pc);
            var quote_current = document.getElementById('quote_current');
            var quote_change = document.getElementById('quote_change');
            var quote_change2 = document.getElementById('quote_change2');
            var quote_close = document.getElementById('quote_close');
            var quote_open = document.getElementById('quote_open');
            var quote_high = document.getElementById('quote_high');
            var quote_low = document.getElementById('quote_low');
            var quote_change_d = document.getElementById('quote_change_d');
            quote_current.textContent = String(parseFloat(stock_info.c).toFixed(2));
            quote_high.textContent = stock_info.h;
            quote_low.textContent = stock_info.l;
            quote_open.textContent = stock_info.o;
            quote_close.textContent = stock_info.pc;
            quote_change_d.textContent = String(parseFloat(stock_info.d).toFixed(2));
            quote_change_d.className = status;
            quote_change.textContent = String(parseFloat(stock_info.dp).toFixed(2)) + "%";
            quote_change2.textContent = String(parseFloat(stock_info.dp).toFixed(2)) + "%";
            quote_change.className = status;
            quote_change2.className = status;
            var graphURL1 = "https://widget.finnhub.io/widgets/stocks/chart?symbol="
            var graphURL2 = "&watermarkColor=black&backgroundColor=black&textColor=white"
            document.getElementById("stock_chart").src = graphURL1 + stock_symbol + graphURL2;
        }
        else if (result.code === 404){
            document.getElementById('stock_symbol').textContent = sessionStorage.getItem("previous_stock_symbol");
            alert("No Such Stock Found.");
        }
    } catch (error) {
        document.getElementById('stock_symbol').textContent = sessionStorage.getItem("previous_stock_symbol");
        alert("Error searching stock, please try again later.");
    }
}

async function postAjax(url, method, data){
    return $.ajax({
        url: url,
        type: method || 'POST',
        crossDomain: true,
        data: JSON.stringify(data),
        dataType: "json"      
    });
};

async function get_stock_company_info(apikey){
    var stockcompanyURL = 'http://' + url + ':8000/api/v1/stock_info/profile2/'
    var apikey = UnicodeDecodeB64(apikey);
    var params = "?apikey=" + apikey;
    var stock_symbol = document.getElementById('stock_symbol').textContent;
    const website = stockcompanyURL + stock_symbol + params;
    const result = await getAjax(website, 'GET');
    try{
        if (result.code === 200) {
            sessionStorage.setItem("company_name", result['data']["name"]);
            sessionStorage.setItem("currency", result['data']["currency"]);
            document.getElementById("stock_company").textContent = sessionStorage.getItem("company_name");
        }
        else if (result.code === 404){
        }
    }
    catch(error){
    }
}

async function place_trade(){
    try {
        var placeradeURL = 'http://' + url +':8000/api/v1/place_trade';        
        var apikey = UnicodeDecodeB64(sessionStorage.getItem("apikey"));
        var email = String(sessionStorage.getItem("email"));
        var stock_symbol = String(document.getElementById('stock_symbol').textContent);
        var stock_quantity = Number(document.getElementById("quantity").value);
        var currency = String(sessionStorage.getItem("currency"));
        var transaction_action = String(document.getElementById("transaction_action").value);
        var params = "?apikey=" + apikey;
        const website = placeradeURL + params;
        var data = {
            "email":email,
            "stock_symbol":stock_symbol,
            "stock_quantity":stock_quantity,
            "currency":currency,
            "transaction_action":transaction_action
        };
        const result = await postAjax(website, 'POST', data);
        if (result.code === 201) {
            alert("Trade placed successfully");
            document.getElementById("quantity").value = "1";
            var apikey = sessionStorage.getItem("apikey");
            var accid = sessionStorage.getItem("accid");
            get_user_stock(accid, apikey);
            get_acc_bal(accid, apikey);
        }
    }
    catch (error) {
        alert("Error placing trade, please try again later.");
    }
};


async function get_acc_bal(accid, apikey){
    var accid = UnicodeDecodeB64(accid);
    var apikey = UnicodeDecodeB64(apikey);
    var currency = "USD";
    try {
        var tradeaccURL = 'http://' + url + ':8000/api/v1/trading_acc/';
        var params = "?apikey=" + apikey;
        const website = tradeaccURL + accid + "/" + currency + params;
        const result = await getAjax(website, 'GET');
        if (result.code === 200) {
            var acc_bal = document.getElementById('acc_bal');
            var user_acc_bal = "Total Assets: " + "$" + String(parseFloat(result["data"]["trade_acc_balance"]).toFixed(2));
            acc_bal.textContent = user_acc_bal;
        }
    } catch (error) {
    }
};

temp = {
    healthcare: ["UNH", "PFE", "SWTX", "INCY", "TMO"],
    energy: ["XOM", "MPC", "COST", "VLO", "PBR"],
    utilities: ["ELEC", "DUK", "NRG", "DTE", "DRE"],
    financials: ["BA", "BAC", "UWMC", "CSCO", "CVX"],
    real_estate: ["HON", "ARE", "EXR", "INVH", "REG"],
    information_technology: ["TSLA", "GOOG", "AMZN", "AAPL", "FB"],
    consumer_discretionary: ["KO", "MMM", "MCD", "DIS", "WMT"],
    materials: ["X", "CLF", "STLD", "LYB", "AA"],
    communication_services: ["PARA", "LUMN", "D", "ATUS", "WWE"],
    industrials: ["LPX", "SEB", "C", "NLSN", "CPA"],
    consumer_staples: ["ACI", "HSY", "BG", "HRL", "SYY"],
};

var container = document.getElementById("search_container");
var ul = document.createElement("ul");
ul.setAttribute("id", "stocks_list");
ul.setAttribute("class", "list-group-flush p-0");

function selectedCheck() {
    var checkedValue = [];
    var inputElements = document.getElementsByName("checkbox[]");

    for (var i = 0; inputElements[i]; ++i) {
        if (inputElements[i].checked) {
            checkedValue.push(inputElements[i].value);
        }
    }
    while (ul.firstChild) {
        ul.removeChild(ul.firstChild);
    }
    for (value of checkedValue) {
        for (symbols of temp[value]) {
            var a = document.createElement("a");
            a.setAttribute(
                "class",
                "link-primary list-group-item bg-dark border-light "
            );
            a.setAttribute("value", symbols);
            a.setAttribute("id", symbols);
            a.setAttribute("href", "#");
            a.innerHTML = symbols + " (" + value + ")";
            ul.appendChild(a);
            a.setAttribute("onclick", "get_stock(this.id)");
        }
        container.appendChild(ul);
    }
}

async function get_stock_pref(accid, apikey){
    var accid = UnicodeDecodeB64(accid);
    var apikey = UnicodeDecodeB64(apikey);
    try {
        var stockprefURL = 'http://' + url + ':8000/api/v1/stock_pref/';
        var params = "?apikey=" + apikey;
        const website = stockprefURL + accid + params;
        const result = await getAjax(website, 'GET');
        if (result.code === 200) {
            for (pref of result["data"]){
                var checkBoxes = document.querySelectorAll('input[id=flexCheckDefault]');
                for (box of checkBoxes){
                    if (box.value.toUpperCase() == pref['stock_Industry'].split(' ').join('_').toUpperCase()){
                        box.checked = true;
                    }
                }
            }
            selectedCheck();
        }
    } catch (error) {
    }
}

function hasWhiteSpace(s) {
    return s.indexOf(' ') >= 0;
  }

function firstCase(string){
    if (hasWhiteSpace(string)){
        return string.split(' ').map(function(word){
            return word.charAt(0).toUpperCase() + word.slice(1);
        }).join(' ');
    }
    return string[0].toUpperCase() + string.slice(1).toLowerCase();
  }

async function addstockpref(accid, apikey, addlist){
    try {
        var addstockprefURL = 'http://' + url + ':8000/api/v1/stock_pref/add/';
        var params = "?apikey=" + apikey;
        var data = {
            "accid": accid,
            "stock_industry": addlist
        }
        const website = addstockprefURL + accid + params;
        const result = await postAjax(website, 'POST', data);
        if (result.code === 200) {
            get_stock_pref(sessionStorage.getItem("accid"), sessionStorage.getItem("apikey"));
        }
    } catch (error) {
    }
}

async function delstockpref(accid, apikey, deletelist){
    try {
        var delstockprefURL = 'http://' + url + ':8000/api/v1/stock_pref/remove/';
        var params = "?apikey=" + apikey;
        var data = {
            "accid": accid,
            "stock_industry": deletelist
        }
        const website = delstockprefURL + accid + params;
        const result = await postAjax(website, 'POST', data);
        if (result.code === 200) {
            get_stock_pref(sessionStorage.getItem("accid"), sessionStorage.getItem("apikey"));
        }
    } catch (error) {
    }
}

async function change_stock_pref(){
    var accid = UnicodeDecodeB64(sessionStorage.getItem("accid"));
    var apikey = UnicodeDecodeB64(sessionStorage.getItem("apikey"));
    var checkedValue = [];
    var inputElements = document.getElementsByName("checkbox[]");
    for (var i = 0; inputElements[i]; ++i) {
        if (inputElements[i].checked) {
            checkedValue.push(firstCase(inputElements[i].value.split('_').join(' ')));
        }
    }
    var setlist = [];
    var addlist = [];
    var deletelist = [];
    try{
        var stockprefURL = 'http://' + url + ':8000/api/v1/stock_pref/';
        var params = "?apikey=" + apikey;
        const website = stockprefURL + accid + params;
        const result = await getAjax(website, 'GET');
        
        if (result.code === 200) {
            for (pref of result["data"]){
                setlist.push(pref['stock_Industry']);
            }
            for (value of checkedValue){
                if (!setlist.includes(value)){
                    addlist.push(value);
                }
            }
            for (value of setlist){
                if (!checkedValue.includes(value)){
                    deletelist.push(value);
                }
            }
        }
    }
    catch(error){
    }
    if (addlist.length > 0){
        addstockpref(accid, apikey, addlist);
    }
    if (deletelist.length > 0){
        delstockpref(accid, apikey, deletelist);
    }   
};

function search(){
    var stock_symbol = document.getElementById("search_stocks").value.toUpperCase();
    if (stock_symbol.length == 0){
        alert("Please enter a stock symbol");
        return;
    }
    if (stock_symbol.length > 5){
        alert("Please enter a stock symbol with less than 5 characters");
        return;
    }
    get_stock(stock_symbol);
} 
