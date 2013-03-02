function get_random_padding_size () {
    var padding_max_bytes = 1024 * 1024 * 2; // 2mb
    return Math.floor(Math.random()*padding_max_bytes);
}

function random_char () {
    /* Javascript has 16-byte (Unicode) strings */
    return String.fromCharCode(Math.floor(Math.random()*Math.pow(2,16)));
}

function add_padding () {
    var padding_size = get_random_padding_size();
    /* Use a list to build the padding string (more efficient than string
     * concatenation */
    var padding = [];
    for(var i=0; i<padding_size; i++) {
        /* Although the connection is encrypted, it is possible that it might
         * be compressed. Therefore, we should pad with random bytes to
         * maximize the potential obfuscation of the POST request size */
        padding.push(random_char());
    }
    var padding_string = padding.join('');
    document.getElementById('padding').setAttribute('value', padding_string);
}

function pad_then_upload () {
    console.log("Adding padding...");
    add_padding();
    console.log("Submitting form");
    return true; // submit form
}

window.onload = function () {
    var form = document.getElementById('uploadForm');
    try {
        form.addEventListener("submit", pad_then_upload, false);
    } catch(e) {
        form.attachEvent("onsubmit", pad_then_upload); // Internet Explorer 8-
    }
};
