class NotlifyApp {
    constructor() {
        this.apiBaseUrl = '/api';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadNotifications();
    }

    bindEvents() {
        const form = document.getElementById('notificationForm');
        const refreshBtn = document.getElementById('refreshBtn');

        form.addEventListener('submit', (e) => this.handleSubmit(e));
        refreshBtn.addEventListener('click', () => this.loadNotifications());
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const notificationData = {
            email: formData.get('email'),
            subject: formData.get('subject'),
            message: formData.get('message'),
            priority: formData.get('priority')
        };

        this.showLoading(true);

        try {
            const response = await this.sendNotification(notificationData);
            this.showNotification('Notification sent successfully!', 'success');
            e.target.reset();
            this.loadNotifications(); // Refresh the list
        } catch (error) {
            this.showNotification('Failed to send notification: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async sendNotification(notificationData) {
        const response = await fetch(`${this.apiBaseUrl}/notify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(notificationData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to send notification');
        }

        return await response.json();
    }

    async loadNotifications() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/notifications?limit=10`);
            const data = await response.json();
            
            this.displayNotifications(data.notifications);
        } catch (error) {
            console.error('Failed to load notifications:', error);
            this.showNotification('Failed to load notifications', 'error');
        }
    }

    displayNotifications(notifications) {
        const container = document.getElementById('notificationsContainer');
        
        if (notifications.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #666;">No notifications yet</p>';
            return;
        }

        container.innerHTML = notifications.map(notification => `
            <div class="notification-item">
                <div class="notification-header">
                    <span class="notification-email">${this.escapeHtml(notification.email)}</span>
                    <span class="notification-status status-${notification.status}">
                        ${notification.status.toUpperCase()}
                    </span>
                </div>
                <div class="notification-subject">${this.escapeHtml(notification.subject)}</div>
                <div class="notification-message">${this.escapeHtml(notification.message)}</div>
                <div class="notification-time">${this.formatDate(notification.timestamp)}</div>
            </div>
        `).join('');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatDate(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        loading.classList.toggle('hidden', !show);
    }

    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type} show`;
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 5000);
    }

    // Health check
    async checkHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const data = await response.json();
            console.log('API Health:', data.status);
            return data.status === 'healthy';
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.notlifyApp = new NotlifyApp();
    
    // Perform health check on startup
    window.notlifyApp.checkHealth().then(healthy => {
        if (!healthy) {
            window.notlifyApp.showNotification('API service is unavailable', 'error');
        }
    });
});
