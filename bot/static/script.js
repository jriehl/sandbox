function main() {
    const message_container = document.querySelector('.messages');
    const form = document.querySelector('form');
    const input_box = document.querySelector('input');

    form.addEventListener('submit', (e) => {
        console.log(form, e, input_box);
        e.preventDefault();
        selfReply(input_box.value);
        input_box.value = '';
    });
    function botReply(message){
        message_container.innerHTML += `<div class="bot">${message['reply']}</div>`;
        location.href = '#edge';
    }
    function selfReply(message){
        message_container.innerHTML += `<div class="self">${message}</div>`;
        location.href = '#edge';
        const reply = postData('reply', {'message': message}).then(botReply);
    }
    botReply({'reply': 'Hello'});
}

// From MDN fetch documentation.
function postData(url = '', data = {}) {
    // Default options are marked with *
    return fetch(url, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, cors, *same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/json',
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        redirect: 'follow', // manual, *follow, error
        referrer: 'no-referrer', // no-referrer, *client
        body: JSON.stringify(data), // body data type must match "Content-Type" header
    })
    .then(response => response.json()); // parses JSON response into native JavaScript objects 
}

function ready(fn) {
    if (document.attachEvent ? document.readyState === "complete" : document.readyState !== "loading"){
        fn();
    } else {
        document.addEventListener('DOMContentLoaded', fn);
    }
}

ready(main);