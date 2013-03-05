function get_random_padding_size () {
    var padding_max_bytes = 1048576 * 2; // 1048576 = 1024**2, * 2 = 2MB
    return Math.floor(Math.random()*padding_max_bytes);
}

function random_char () {
    /* Javascript has 16-bit (Unicode) strings. 2**16 = 65536 */
    //return String.fromCharCode(Math.floor(Math.random()*65536));
    // ^ this code had unexpected behavior, seems like there are some problems
    // with sending unexpected characters in the browser. Probably due to
    // encoding.
    var chars = "0123456789!@#$%^&*()ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz";
    var random_char_index = Math.floor(Math.random()*chars.length);
    return chars[random_char_index];
}

function add_padding () {
    var padding_size = get_random_padding_size();
    console.log("Padding size: " + padding_size); // DEBUG
    /* Use a list to build the padding string (more efficient than repeated
     * string concatenation) */
    var padding = [];
    /* Since Javascript strings have 16-bit Unicode characters, we generate
     * padding_size/2 random characters so we end up padding by padding_size
     * bytes */
    for(var i=0; i<padding_size/2; i++) {
        /* Although the connection is encrypted, it is possible that it might
         * be compressed. Therefore, we should pad with random bytes to
         * avoid losing our padding to compression. */
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
