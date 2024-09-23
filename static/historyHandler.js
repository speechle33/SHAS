// Intercept popstate event (Back & Forward navigation)
window.addEventListener("popstate", function(event) {
    location.reload();
});

// Intercept pushstate and replacestate events (for SPA frameworks or manual history handling, if needed)
(function(history) {
    var pushState = history.pushState;
    var replaceState = history.replaceState;

    history.pushState = function(state) {
        if (typeof history.onpushstate == "function") {
            history.onpushstate({state: state});
        }
        return pushState.apply(history, arguments);
    };

    history.replaceState = function(state) {
        if (typeof history.onreplacestate == "function") {
            history.onreplacestate({state: state});
        }
        return replaceState.apply(history, arguments);
    };

    window.addEventListener("popstate", function(event) {
        location.reload();
    });
})(window.history);