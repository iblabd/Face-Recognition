function get(param) {
    var $_GET = {};
    if(document.location.toString().indexOf('?') !== -1) {
        var query = document.location
                    .toString()
                    .replace(/^.*?\?/, '')
                    .replace(/#.*$/, '')
                    .split('&');

        for(var i=0, l=query.length; i<l; i++) {
            var aux = decodeURIComponent(query[i]).split('=');
            $_GET[aux[0]] = aux[1];
        }
    }

    return $_GET[param];
}

function bringMeBack() {
    let currentURL = window.location.href;
    location.replace(currentURL.replace("after?s=0", "index"));
}

function main() {
    let message = "";

    const status = get("s");

    const text = document.querySelector("#text");
    const button = document.querySelector("#btn-try-again");
    const img = document.querySelector("#img");

    button.setAttribute("style", "transform: scale(2);\nmargin-top: 30px;");
    
    img.style.display = "none";

    if(status == 1){
        img.style.display = "block";
        button.style.display = "none";
        message = "Kamu sudah melakukan presensi masuk !! <⁠(⁠￣⁠︶⁠￣⁠)⁠>";
    }else if(status == 2){
        img.style.display = "block";
        button.style.display = "none";
        message = "Presensi hari ini sudah selesai!! (⁠ ⁠╹⁠▽⁠╹⁠ ⁠)⁠✧";
    }else {
        button.style.display = "block";
        message = "Presensi gagal desu (⁠-_-⁠メ⁠)";
        img.style.display = "none";
    }

    text.style.fontSize = "100px;";
    text.innerHTML = message;
}

main();