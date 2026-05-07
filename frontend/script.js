async function embedImage() {

    const file = document.getElementById('embedFile').files[0];

    let formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://127.0.0.1:8000/embed', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    document.getElementById('embedResult').innerText =
        '✔ ' + data.message + '\nHash: ' + data.hash;

    document.getElementById('embedOutput').src =
        'http://127.0.0.1:8000/' + data.output;
}


async function verifyImage() {

    const file = document.getElementById('verifyFile').files[0];

    let formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://127.0.0.1:8000/verify', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    document.getElementById('verifyResult').innerText =
        'Verification Status: ' + data.status;
}