navigator.geolocation.getCurrentPosition(success,error);

function success(position)
{
    var user_latitude=position.coords.latitude;
    var user_longitude=position.coords.longitude;
    console.log(user_latitude+","+user_longitude);
    sendData(user_latitude,user_longitude);
    //sendData(13.3467869,74.7668934);
    const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${user_latitude}&lon=${user_longitude}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const address = data.display_name;
            //document.getElementById("location").innerHTML += `<br>Address: ${address}`;
            console.log(address);
        })
        .catch(error => console.error('Error fetching the address:', error));
}

function error()
{
    console.log("error....");
}
// static/js/script.js

function sendData(user_latitude,user_longitude) {

    
    const data = { key1: user_latitude, key2: user_longitude };

    fetch('/my-view/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Ensure CSRF token is included
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        //displayResponse(data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Call the function to send data


/*function displayResponse(data) {
    const responseContainer = document.getElementById('response-container');
    responseContainer.innerText = JSON.stringify(data, null, 2);
    console.log(JSON.stringify(data, null, 2));
    console.log("working");
}

// Call the function to send data (for example, on window load)
window.onload = function() {
    sendData();
};*/
