(function(){
    window.Redis = function() {
        
    }
    Redis.prototype.subscribe = function(channel, callback) {
        var request = XMLHttpRequest();
        var lastLength = 0;
        function handleProgress(e) {
            if (request.response.length == lastLength)
                return;
            var nextLength;
            while ((nextLength = request.response.indexOf('\n', lastLength)) != -1) {
                var blob = request.response.substring(lastLength, nextLength);
                var json = JSON.parse(blob);
                callback(json.channel, json.data);
                lastLength = nextLength + 1;
            }
        }
        request.onprogress = handleProgress;
        request.load = handleProgress;
        request.loadend = function(e) {
            console.log("Server terminated request, reconnecting...");
            this.subscribe(channel, callback);
        }
        request.open('GET', '/subscribe/' + channel);
        request.send();
    }
})()
