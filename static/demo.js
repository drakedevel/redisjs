(function(){
    function onSubmit(e) {
        try {
            var channel = e.target.elements['channel'].value;
            if (!channel)
                return;
            console.log("Subscribing to channel " + channel);
            (new Redis()).subscribe(channel, function(c, message) {
                console.log("Got message: " + message);
                var text = document.createTextNode("[" + channel + "] " + message);
                var li = document.createElement("li");
                li.appendChild(text);
                document.getElementById("messages").appendChild(li);
            });
        } catch (ex) {
            console.error(ex);
        } finally {
            e.preventDefault();
            return false;
        }
    }

    window.addEventListener("DOMContentLoaded", function() {
        document.getElementById('subscribe_form').addEventListener('submit', onSubmit);
    }, false);
})()
