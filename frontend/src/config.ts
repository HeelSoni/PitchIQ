let rawBase = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

// Trim trailing slashes safely
rawBase = rawBase.replace(/\/+$/, '');

// Ensure /api is present at the end
if (!rawBase.endsWith('/api')) {
  rawBase = `${rawBase}/api`;
}

export const API_BASE = rawBase;
