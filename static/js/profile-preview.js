// Profile Picture Preview
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('profile_picture');
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            if (file) {
                // Check file type
                const validTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif'];
                if (!validTypes.includes(file.type)) {
                    showToast('Please select a valid image file (PNG, JPG, JPEG, or GIF)', 'error');
                    this.value = '';
                    return;
                }
                
                // Check file size (16MB max)
                if (file.size > 16 * 1024 * 1024) {
                    showToast('File size must be less than 16MB', 'error');
                    this.value = '';
                    return;
                }
                
                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    const avatarImg = document.querySelector('.avatar-circle');
                    if (avatarImg.tagName === 'IMG') {
                        avatarImg.src = e.target.result;
                    } else {
                        // Replace div with img
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.className = 'avatar-circle';
                        img.alt = 'Profile Picture Preview';
                        avatarImg.parentNode.replaceChild(img, avatarImg);
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
});
