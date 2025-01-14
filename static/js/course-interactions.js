// Resource Preview
function initializeResourcePreview() {
    const previewButtons = document.querySelectorAll('.preview-resource');
    previewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const resourceUrl = this.dataset.url;
            const resourceType = this.dataset.type;
            const previewContainer = document.getElementById('resource-preview');
            
            if (resourceType === 'pdf') {
                previewContainer.innerHTML = `
                    <iframe src="${resourceUrl}" class="pdf-preview"></iframe>
                `;
            } else if (resourceType === 'image') {
                previewContainer.innerHTML = `
                    <img src="${resourceUrl}" class="img-fluid" alt="Resource Preview">
                `;
            }
            
            $('#previewModal').modal('show');
        });
    });
}

// Discussion Thread Interactions
function initializeDiscussionThreads() {
    const replyButtons = document.querySelectorAll('.reply-button');
    replyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const parentId = this.dataset.parent;
            const replyForm = document.querySelector(`#reply-form-${parentId}`);
            
            // Hide all other active forms
            document.querySelectorAll('.reply-form.active').forEach(form => {
                if (form !== replyForm) {
                    form.classList.remove('active');
                }
            });
            
            replyForm.classList.toggle('active');
        });
    });
}

// Notification Handling
function initializeNotifications() {
    const notificationBell = document.getElementById('notification-bell');
    const notificationCount = document.getElementById('notification-count');
    
    function updateNotifications() {
        fetch('/api/notifications/unread-count/')
            .then(response => response.json())
            .then(data => {
                notificationCount.textContent = data.count;
                if (data.count > 0) {
                    notificationBell.classList.add('has-notifications');
                } else {
                    notificationBell.classList.remove('has-notifications');
                }
            });
    }
    
    // Update notifications every minute
    setInterval(updateNotifications, 60000);
}

// Initialize all features
document.addEventListener('DOMContentLoaded', function() {
    initializeResourcePreview();
    initializeDiscussionThreads();
    initializeNotifications();
}); 