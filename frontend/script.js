/**
 * Medical Image Watermarking Frontend Script
 *
 * This script manages the user interface for embedding and verifying
 * medical image watermarks. It communicates with the FastAPI backend
 * and shows the result in a friendly way.
 *
 * Author: Adarsh
 * License: MIT
 */

const apiBaseUrl = 'http://127.0.0.1:8000';

function showMessage(element, text, type = 'info') {
    const colors = {
        info: '#2563eb',
        success: '#16a34a',
        error: '#dc2626',
    };
    element.innerHTML = `<span style="color: ${colors[type]};">${text}</span>`;
}

async function embedImage() {
    const fileInput = document.getElementById('embedFile');
    const resultDiv = document.getElementById('embedResult');
    const outputImg = document.getElementById('embedOutput');

    if (!fileInput.files.length) {
        showMessage(resultDiv, '❌ Please choose a medical image first.', 'error');
        return;
    }

    showMessage(resultDiv, '⏳ Uploading image and embedding watermark...', 'info');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch(`${apiBaseUrl}/embed`, {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();

        if (!response.ok) {
            showMessage(resultDiv, `❌ ${data.detail || data.message || 'Failed to embed watermark.'}`, 'error');
            return;
        }

        showMessage(resultDiv, `✔ ${data.message} Hash: ${data.hash}`, 'success');
        const outputUrl = data.output_url ? `${apiBaseUrl}${data.output_url}` : `${apiBaseUrl}/${data.output}`;
        outputImg.src = outputUrl;
        outputImg.style.display = 'block';
        outputImg.alt = 'Watermarked medical image preview';
    } catch (error) {
        showMessage(resultDiv, '❌ Unable to contact the backend. Please start the server and try again.', 'error');
        console.error('Embed error:', error);
    }
}

async function verifyImage() {
    const fileInput = document.getElementById('verifyFile');
    const resultDiv = document.getElementById('verifyResult');

    if (!fileInput.files.length) {
        showMessage(resultDiv, '❌ Please choose an image to verify.', 'error');
        return;
    }

    showMessage(resultDiv, '⏳ Verifying image...', 'info');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch(`${apiBaseUrl}/verify`, {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();

        if (!response.ok) {
            showMessage(resultDiv, `❌ ${data.detail || data.message || 'Verification failed.'}`, 'error');
            return;
        }

        if (data.status === 'Authentic') {
            showMessage(resultDiv, '✅ The image is authentic and has not been tampered with.', 'success');
        } else {
            showMessage(resultDiv, '❌ The image appears to have been tampered with.', 'error');
        }
    } catch (error) {
        showMessage(resultDiv, '❌ Unable to contact the backend. Please start the server and try again.', 'error');
        console.error('Verify error:', error);
    }
}
