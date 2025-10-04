document.addEventListener('DOMContentLoaded', function() {
    // File upload preview
    const fileUpload = document.getElementById('image');
    const fileUploadLabel = document.querySelector('.file-upload-label');
    
    fileUpload.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const fileName = this.files[0].name;
            const fileText = document.querySelector('.file-upload-text');
            fileText.textContent = fileName;
            
            // Show preview (optional)
            // const reader = new FileReader();
            // reader.onload = function(e) {
            //     document.getElementById('previewImage').src = e.target.result;
            // }
            // reader.readAsDataURL(this.files[0]);
        }
    });
    
    // Form submission feedback
    const uploadForm = document.getElementById('uploadForm');
    const convertBtn = document.querySelector('.convert-btn');
    
    uploadForm.addEventListener('submit', function() {
        if (!fileUpload.files[0]) {
            return;
        }
        
        convertBtn.disabled = true;
        convertBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    });
});

// Download image function
function downloadImage(dataUrl, filename) {
    const link = document.createElement('a');
    link.href = dataUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Show download confirmation
    const originalText = event.target.innerHTML;
    event.target.innerHTML = '<i class="fas fa-check"></i> Downloaded!';
    event.target.style.backgroundColor = '#28a745';
    
    setTimeout(() => {
        event.target.innerHTML = originalText;
        event.target.style.backgroundColor = '';
    }, 2000);
}