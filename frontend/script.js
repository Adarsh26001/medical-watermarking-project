/**
 * Medical Image Watermarking Frontend Script
 *
 * Handles client-side interactions for watermark embedding and verification.
 * Communicates with FastAPI backend for image processing operations.
 *
 * Author: Adarsh
 * License: MIT
 */

/**
 * Embed watermark in uploaded medical image
 * Sends image to backend API and displays results
 */
async function embedImage() {
    const fileInput = document.getElementById('embedFile');
    const resultDiv = document.getElementById('embedResult');
    const outputImg = document.getElementById('embedOutput');

    // Validate file selection
    if (!fileInput.files[0]) {
        resultDiv.innerHTML = '<span style="color: red;">❌ Please select an image file first.</span>';
        return;
    }

    // Show loading state
    resultDiv.innerHTML = '<span style="color: blue;">⏳ Processing image...</span>';

    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        // Send to backend API
        const response = await fetch('http://127.0.0.1:8000/embed', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            // Success: Display results
            resultDiv.innerHTML = `
                <span style="color: green;">✔ ${data.message}</span><br>
                <strong>SHA-256 Hash:</strong> <code>${data.hash}</code>
            `;

            // Display watermarked image
            outputImg.src = `http://127.0.0.1:8000/${data.output}`;
            outputImg.style.display = 'block';
        } else {
            // API error
            resultDiv.innerHTML = `<span style="color: red;">❌ Error: ${data.detail || 'Unknown error'}</span>`;
        }

    } catch (error) {
        // Network error
        resultDiv.innerHTML = '<span style="color: red;">❌ Network error. Please check if the backend server is running.</span>';
        console.error('Embed error:', error);
    }
}

/**
 * Verify authenticity of uploaded image
 * Compares image hash with stored original hash
 */
async function verifyImage() {
    const fileInput = document.getElementById('verifyFile');
    const resultDiv = document.getElementById('verifyResult');

    // Validate file selection
    if (!fileInput.files[0]) {
        resultDiv.innerHTML = '<span style="color: red;">❌ Please select an image file first.</span>';
        return;
    }

    // Show loading state
    resultDiv.innerHTML = '<span style="color: blue;">⏳ Verifying image...</span>';

    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        // Send to backend API
        const response = await fetch('http://127.0.0.1:8000/verify', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            if (data.status === 'Authentic') {
                resultDiv.innerHTML = '<span style="color: green;">✅ Image is Authentic - No tampering detected</span>';
            } else {
                resultDiv.innerHTML = '<span style="color: red;">❌ Image has been Tampered - Security breach detected</span>';
            }
        } else {
            // API error
            resultDiv.innerHTML = `<span style="color: red;">❌ Error: ${data.detail || 'Unknown error'}</span>`;
        }

    } catch (error) {
        // Network error
        resultDiv.innerHTML = '<span style="color: red;">❌ Network error. Please check if the backend server is running.</span>';
        console.error('Verify error:', error);
    }
}