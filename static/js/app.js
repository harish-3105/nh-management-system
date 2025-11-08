// NH Management System - Main Application JavaScript

class NHManagementApp {
    constructor() {
        // Use current origin for API calls (works with dev tunnels and localhost)
        this.apiUrl = window.location.origin;
        this.token = localStorage.getItem('nh_token');
        this.user = JSON.parse(localStorage.getItem('nh_user') || 'null');
        this.currentPage = 'dashboard';
    }

    // Authentication
    async login(username, password) {
        try {
            const response = await fetch(`${this.apiUrl}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            
            if (data.success) {
                this.token = data.data.token;
                this.user = data.data.user;
                localStorage.setItem('nh_token', this.token);
                localStorage.setItem('nh_user', JSON.stringify(this.user));
                return { success: true };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            return { success: false, message: 'Connection error: ' + error.message };
        }
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('nh_token');
        localStorage.removeItem('nh_user');
        window.location.href = '/';
    }

    isAuthenticated() {
        return this.token !== null;
    }

    // API calls with authentication
    async apiCall(endpoint, method = 'GET', body = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        // Only add Authorization header if token exists
        if (this.token) {
            options.headers['Authorization'] = `Bearer ${this.token}`;
        }

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`${this.apiUrl}${endpoint}`, options);
        
        // If 422 (invalid token), clear token and retry without auth
        if (response.status === 422 && this.token) {
            console.warn('Invalid token detected, clearing and retrying...');
            this.token = null;
            localStorage.removeItem('nh_token');
            // Retry without token
            delete options.headers['Authorization'];
            const retryResponse = await fetch(`${this.apiUrl}${endpoint}`, options);
            return await retryResponse.json();
        }
        
        return await response.json();
    }

    // Data fetching
    async getDashboardStats() {
        try {
            const [nhs, segments, divisions] = await Promise.all([
                this.apiCall('/api/nh'),
                this.apiCall('/api/segments'),
                this.apiCall('/api/divisions')
            ]);

            return {
                totalNHs: nhs.data?.length || 0,
                totalSegments: segments.data?.length || 0,
                totalOffices: divisions.data?.length || 0,
                segments: segments.data || []
            };
        } catch (error) {
            console.error('Error fetching dashboard stats:', error);
            return { totalNHs: 0, totalSegments: 0, totalOffices: 0, segments: [] };
        }
    }

    async getSegments() {
        return await this.apiCall('/api/segments');
    }

    async getSegmentDetails(segmentId) {
        return await this.apiCall(`/api/segments/${segmentId}`);
    }

    async getRoadDetails(segmentId) {
        return await this.apiCall(`/api/segments/${segmentId}/details`);
    }

    async getConfigurations() {
        return await this.apiCall('/api/configurations');
    }

    async getAllNHs() {
        return await this.apiCall('/api/nh');
    }

    async addRoadDetail(data) {
        return await this.apiCall('/api/details', 'POST', data);
    }

    async updateRoadDetail(detailId, data) {
        return await this.apiCall(`/api/details/${detailId}`, 'PUT', data);
    }

    async deleteRoadDetail(detailId) {
        return await this.apiCall(`/api/details/${detailId}`, 'DELETE');
    }

    async runValidation() {
        const [overlappingSegments, overlappingConfigs, outOfBounds] = await Promise.all([
            this.apiCall('/api/validation/overlapping-segments'),
            this.apiCall('/api/validation/overlapping-configurations'),
            this.apiCall('/api/validation/out-of-bounds')
        ]);

        return {
            overlappingSegments: overlappingSegments.data || [],
            overlappingConfigs: overlappingConfigs.data || [],
            outOfBounds: outOfBounds.data || []
        };
    }

    async getNHReport(nhNumber) {
        return await this.apiCall(`/api/reports/nh-summary?nh_number=${nhNumber}`);
    }

    async getDivisionReport(divisionName) {
        return await this.apiCall(`/api/reports/division-summary?division_name=${divisionName}`);
    }

    async getConfigStats() {
        return await this.apiCall('/api/reports/config-statistics');
    }

    async getDetailedConfigReport(configId) {
        return await this.apiCall(`/api/reports/config-details?config_id=${configId}`);
    }

    async getDivisionWiseReport(nhNumber, configId) {
        let url = `/api/reports/division-wise?nh_number=${nhNumber}`;
        if (configId) {
            url += `&config_id=${configId}`;
        }
        return await this.apiCall(url);
    }

    // Utility functions
    formatNumber(num) {
        return new Intl.NumberFormat('en-IN').format(num);
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    showLoading() {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = 'loadingOverlay';
        overlay.innerHTML = '<div class="loading-spinner"></div>';
        document.body.appendChild(overlay);
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.remove();
        }
    }

    showAlert(message, type = 'success') {
        const alertContainer = document.getElementById('alertContainer');
        if (!alertContainer) return;

        const alert = document.createElement('div');
        alert.className = `alert alert-${type === 'error' ? 'error' : type}`;
        alert.innerHTML = `
            <span>${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</span>
            <span>${message}</span>
        `;
        alertContainer.appendChild(alert);

        setTimeout(() => alert.remove(), 5000);
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
        }
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
        }
    }

    getUserInitials() {
        if (!this.user || !this.user.full_name) return 'U';
        return this.user.full_name
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .slice(0, 2);
    }
}

// Initialize app
const app = new NHManagementApp();

// Export for use in HTML pages
window.app = app;
