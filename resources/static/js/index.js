function getCurrentURL() {
    return window.location.href
}

function sleep(milliseconds) {
    const date = Date.now();
    let currentDate = null;
    console.log(`wait(${milliseconds})`)
    do {
        currentDate = Date.now();
    } while (currentDate - date < milliseconds);
}

function buttonOnClick() {
    url = getCurrentURL().replace("index", "tempsession")
    console.log(url)

    async function get(url) {
        let obj = await (await fetch(url)).json();
        return obj;
    }

    var tags;
    const hour = new Date().getHours();

    (async () => {
        sleep(3000)
        tags = await get(url)
        console.log(tags["status"])
        if(tags["status"] == 1 
        // && (hour >= 6 && hour <= 7)
        ) {
            location.replace(getCurrentURL().replace("index", "after?s=1"))
        }else if(tags["status"] == 2 
        // && (hour >= 14 && hour <= 15)
        ) {
            location.replace(getCurrentURL().replace("index", "after?s=2"))
        }else {
            location.replace(getCurrentURL().replace("index", "after?s=0"))
        }
    })()

}

sleep(3000)
document.getElementById("button").click()