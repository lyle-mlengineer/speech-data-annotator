const fileInput = document.getElementById('fileInput');
const uploadButton = document.getElementById('upload');

fileInput.addEventListener('change', function() {
    if (fileInput.files.length > 0) {
        uploadButton.style.display = 'inline-block';
    } else {
        uploadButton.style.display = 'none';
    }
});