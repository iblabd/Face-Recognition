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

function main() {
    let status = get("s")

    let text = document.getElementById("text")
    let message = ""

    if(status == 1)
        message = "Yay! Presensi masuk telah berhasil!! <⁠(⁠￣⁠︶⁠￣⁠)⁠>"
    else if(status == 2)
        message = "Presensi hari ini sudah selesai!! (⁠ ⁠╹⁠▽⁠╹⁠ ⁠)⁠✧"
    else
        message = "Furesenshi gagaru desu (⁠-_-⁠メ⁠)"
    text.innerHTML = message
}

main()