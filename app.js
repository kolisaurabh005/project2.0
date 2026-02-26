/**
 * Secure Multi-Language App - React Frontend
 * ==========================================
 * A production-ready SPA with ReactBits-inspired animated components
 */

const { useState, useEffect, useCallback, createContext, useContext, useRef } = React;

// ===================================
// Context & State Management
// ===================================

// Language Context
const LanguageContext = createContext();

// Auth Context
const AuthContext = createContext();

// Available languages
const LANGUAGES = [
    { code: 'en', name: 'English', native: 'English', flag: '🇺🇸' },
    { code: 'hi', name: 'Hindi', native: 'हिन्दी', flag: '🇮🇳' },
    { code: 'es', name: 'Spanish', native: 'Español', flag: '🇪🇸' },
    { code: 'pt', name: 'Portuguese', native: 'Português', flag: '🇧🇷' },
    { code: 'zh', name: 'Chinese', native: '中文', flag: '🇨🇳' },
    { code: 'fr', name: 'French', native: 'Français', flag: '🇫🇷' }
];

// ===================================
// API Service
// ===================================
const API = {
    async request(url, options = {}) {
        const config = {
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            return { ok: response.ok, status: response.status, data };
        } catch (error) {
            return { ok: false, status: 500, data: { message: 'Network error' } };
        }
    },
    
    // Auth endpoints
    register: (data) => API.request('/api/auth/register', { method: 'POST', body: JSON.stringify(data) }),
    login: (data) => API.request('/api/auth/login', { method: 'POST', body: JSON.stringify(data) }),
    logout: () => API.request('/api/auth/logout', { method: 'POST' }),
    getMe: () => API.request('/api/auth/me'),
    verifyLoginOtp: (otp) => API.request('/api/auth/verify-login-otp', { method: 'POST', body: JSON.stringify({ otp }) }),
    resendLoginOtp: () => API.request('/api/auth/resend-otp', { method: 'POST' }),
    
    // Dashboard endpoints
    getDashboard: () => API.request('/api/dashboard/summary'),
    getLoginHistory: () => API.request('/api/dashboard/login-history'),
    getLanguageHistory: () => API.request('/api/dashboard/language-history'),
    
    // Language endpoints
    getTranslations: (lang) => API.request(`/api/language/translations/${lang}`),
    changeLanguage: (lang) => API.request('/api/language/change', { method: 'POST', body: JSON.stringify({ language: lang }) }),
    verifyLanguageOtp: (otp) => API.request('/api/language/verify-change', { method: 'POST', body: JSON.stringify({ otp }) }),
    resendLanguageOtp: () => API.request('/api/language/resend-otp', { method: 'POST' }),
    cancelLanguageChange: () => API.request('/api/language/cancel-change', { method: 'POST' })
};

// ===================================
// Particle Background Component
// ===================================
function ParticleBackground() {
    useEffect(() => {
        const container = document.getElementById('particles-container');
        if (!container) return;
        
        // Create particles
        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.animationDelay = `${Math.random() * 20}s`;
            particle.style.animationDuration = `${15 + Math.random() * 10}s`;
            container.appendChild(particle);
        }
        
        return () => {
            container.innerHTML = '';
        };
    }, []);
    
    return null;
}

// ===================================
// Animated Text Component (ReactBits BlurText inspired)
// ===================================
function BlurText({ children, className = '', delay = 0 }) {
    return (
        <span 
            className={`blur-text ${className}`} 
            style={{ animationDelay: `${delay}s` }}
        >
            {children}
        </span>
    );
}

// ===================================
// Glow Button Component (ReactBits inspired)
// ===================================
function GlowButton({ children, onClick, disabled, loading, className = '', variant = 'primary', block = false }) {
    const btnClass = `btn btn-${variant} ${block ? 'btn-block' : ''} ${loading ? 'glow-pulse' : ''} ${className}`;
    
    return (
        <button 
            className={btnClass}
            onClick={onClick}
            disabled={disabled || loading}
        >
            {loading ? (
                <>
                    <span className="loader-spinner" style={{ width: 20, height: 20, marginRight: 8 }}></span>
                    Loading...
                </>
            ) : children}
        </button>
    );
}

// ===================================
// Alert Component
// ===================================
function Alert({ type = 'info', children, onClose }) {
    if (!children) return null;
    
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    
    return (
        <div className={`alert alert-${type} fade-in`}>
            <span>{icons[type]}</span>
            <span>{children}</span>
            {onClose && (
                <button onClick={onClose} style={{ marginLeft: 'auto', background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}>
                    ✕
                </button>
            )}
        </div>
    );
}

// ===================================
// OTP Input Component
// ===================================
function OTPInput({ length = 6, onComplete, disabled }) {
    const [values, setValues] = useState(Array(length).fill(''));
    const inputRefs = useRef([]);
    
    const handleChange = (index, value) => {
        if (!/^\d*$/.test(value)) return;
        
        const newValues = [...values];
        newValues[index] = value.slice(-1);
        setValues(newValues);
        
        // Move to next input
        if (value && index < length - 1) {
            inputRefs.current[index + 1]?.focus();
        }
        
        // Check if complete
        const otp = newValues.join('');
        if (otp.length === length) {
            onComplete(otp);
        }
    };
    
    const handleKeyDown = (index, e) => {
        if (e.key === 'Backspace' && !values[index] && index > 0) {
            inputRefs.current[index - 1]?.focus();
        }
    };
    
    const handlePaste = (e) => {
        e.preventDefault();
        const pasted = e.clipboardData.getData('text').slice(0, length);
        if (!/^\d+$/.test(pasted)) return;
        
        const newValues = pasted.split('').concat(Array(length - pasted.length).fill(''));
        setValues(newValues);
        
        if (pasted.length === length) {
            onComplete(pasted);
        }
    };
    
    return (
        <div className="otp-input-container">
            {values.map((value, index) => (
                <input
                    key={index}
                    ref={el => inputRefs.current[index] = el}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={value}
                    onChange={e => handleChange(index, e.target.value)}
                    onKeyDown={e => handleKeyDown(index, e)}
                    onPaste={handlePaste}
                    className="otp-input"
                    disabled={disabled}
                    autoFocus={index === 0}
                />
            ))}
        </div>
    );
}

// ===================================
// OTP Timer Component
// ===================================
function OTPTimer({ initialSeconds = 300, onExpire }) {
    const [seconds, setSeconds] = useState(initialSeconds);
    
    useEffect(() => {
        if (seconds <= 0) {
            onExpire?.();
            return;
        }
        
        const timer = setInterval(() => {
            setSeconds(s => s - 1);
        }, 1000);
        
        return () => clearInterval(timer);
    }, [seconds, onExpire]);
    
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    
    return (
        <div className="otp-timer">
            OTP expires in <span>{minutes}:{secs.toString().padStart(2, '0')}</span>
        </div>
    );
}

// ===================================
// Language Selector Component
// ===================================
function LanguageSelector() {
    const { currentLanguage, changeLanguage, t } = useContext(LanguageContext);
    const { user } = useContext(AuthContext);
    const [isOpen, setIsOpen] = useState(false);
    const [showOtpModal, setShowOtpModal] = useState(false);
    const [otpData, setOtpData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    
    const currentLang = LANGUAGES.find(l => l.code === currentLanguage) || LANGUAGES[0];
    
    const handleLanguageSelect = async (langCode) => {
        if (langCode === currentLanguage) {
            setIsOpen(false);
            return;
        }
        
        if (!user) {
            // Not logged in - just change language in context
            changeLanguage(langCode);
            setIsOpen(false);
            return;
        }
        
        // Logged in - need OTP verification
        setLoading(true);
        setError('');
        
        const result = await API.changeLanguage(langCode);
        setLoading(false);
        
        if (result.ok && result.data.otp_required) {
            setOtpData({
                targetLanguage: langCode,
                otpType: result.data.otp_type,
                targetHint: result.data.target_hint
            });
            setShowOtpModal(true);
        } else {
            setError(result.data.message || 'Failed to initiate language change');
        }
        
        setIsOpen(false);
    };
    
    const handleOtpVerify = async (otp) => {
        setLoading(true);
        setError('');
        
        const result = await API.verifyLanguageOtp(otp);
        setLoading(false);
        
        if (result.ok) {
            changeLanguage(otpData.targetLanguage);
            setShowOtpModal(false);
            setOtpData(null);
        } else {
            setError(result.data.message || 'Invalid OTP');
        }
    };
    
    const handleResendOtp = async () => {
        setLoading(true);
        const result = await API.resendLanguageOtp();
        setLoading(false);
        
        if (!result.ok) {
            setError(result.data.message || 'Failed to resend OTP');
        }
    };
    
    const handleCancelOtp = async () => {
        await API.cancelLanguageChange();
        setShowOtpModal(false);
        setOtpData(null);
        setError('');
    };
    
    return (
        <>
            <div className="language-selector">
                <button className="language-btn" onClick={() => setIsOpen(!isOpen)}>
                    <span>{currentLang.flag}</span>
                    <span>{currentLang.native}</span>
                    <span style={{ fontSize: '0.8em' }}>▼</span>
                </button>
                
                {isOpen && (
                    <div className="language-dropdown">
                        {LANGUAGES.map(lang => (
                            <div 
                                key={lang.code}
                                className={`language-option ${lang.code === currentLanguage ? 'active' : ''}`}
                                onClick={() => handleLanguageSelect(lang.code)}
                            >
                                <span>{lang.flag}</span>
                                <span>{lang.native}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
            
            {/* OTP Verification Modal */}
            {showOtpModal && (
                <div className="modal-overlay" onClick={handleCancelOtp}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3 className="modal-title">{t('otp.title')}</h3>
                            <button className="modal-close" onClick={handleCancelOtp}>✕</button>
                        </div>
                        <div className="modal-body">
                            <p className="text-center mb-2">
                                {otpData?.otpType === 'email' ? t('otp.otp_sent_email') : t('otp.otp_sent_mobile')}
                            </p>
                            <p className="text-center mb-3" style={{ color: 'var(--text-muted)' }}>
                                {otpData?.targetHint}
                            </p>
                            
                            {error && <Alert type="error">{error}</Alert>}
                            
                            <OTPInput onComplete={handleOtpVerify} disabled={loading} />
                            
                            <OTPTimer onExpire={handleCancelOtp} />
                            
                            <div className="flex justify-center gap-2 mt-3">
                                <GlowButton variant="secondary" onClick={handleResendOtp} disabled={loading}>
                                    {t('otp.resend')}
                                </GlowButton>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}

// ===================================
// Navigation Component
// ===================================
function Navbar() {
    const { user, logout } = useContext(AuthContext);
    const { t } = useContext(LanguageContext);
    const [currentPage, setCurrentPage] = useState('home');
    
    return (
        <nav className="navbar">
            <div className="navbar-content">
                <a href="#" className="navbar-brand" onClick={() => setCurrentPage('home')}>
                    <span className="navbar-brand-icon">🔐</span>
                    <span>{t('app.name')}</span>
                </a>
                
                <div className="navbar-nav">
                    {user ? (
                        <>
                            <span 
                                className="nav-link" 
                                onClick={() => window.dispatchEvent(new CustomEvent('navigate', { detail: 'dashboard' }))}
                            >
                                {t('nav.dashboard')}
                            </span>
                            <span className="nav-link" onClick={logout}>
                                {t('nav.logout')}
                            </span>
                        </>
                    ) : (
                        <>
                            <span 
                                className="nav-link"
                                onClick={() => window.dispatchEvent(new CustomEvent('navigate', { detail: 'login' }))}
                            >
                                {t('nav.login')}
                            </span>
                            <span 
                                className="nav-link"
                                onClick={() => window.dispatchEvent(new CustomEvent('navigate', { detail: 'register' }))}
                            >
                                {t('nav.register')}
                            </span>
                        </>
                    )}
                    <LanguageSelector />
                </div>
            </div>
        </nav>
    );
}

// ===================================
// Login Page Component
// ===================================
function LoginPage({ onNavigate }) {
    const { login } = useContext(AuthContext);
    const { t } = useContext(LanguageContext);
    const [formData, setFormData] = useState({ email: '', password: '' });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showOtp, setShowOtp] = useState(false);
    const [otpData, setOtpData] = useState(null);
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        
        const result = await API.login(formData);
        setLoading(false);
        
        if (result.ok) {
            if (result.data.otp_required) {
                // Chrome browser - need OTP
                setOtpData({
                    emailHint: result.data.email_hint,
                    otpType: result.data.otp_type
                });
                setShowOtp(true);
            } else if (result.data.access_denied) {
                // Mobile time restriction
                setError(result.data.message);
            } else {
                // Direct login (Edge or other browsers)
                login(result.data.user);
                onNavigate('dashboard');
            }
        } else {
            setError(result.data.message || t('errors.invalid_credentials'));
        }
    };
    
    const handleOtpVerify = async (otp) => {
        setLoading(true);
        setError('');
        
        const result = await API.verifyLoginOtp(otp);
        setLoading(false);
        
        if (result.ok) {
            login(result.data.user);
            onNavigate('dashboard');
        } else {
            setError(result.data.message || t('otp.invalid_otp'));
        }
    };
    
    const handleResendOtp = async () => {
        setLoading(true);
        const result = await API.resendLoginOtp();
        setLoading(false);
        
        if (!result.ok) {
            setError(result.data.message || 'Failed to resend OTP');
        }
    };
    
    if (showOtp) {
        return (
            <div className="auth-container">
                <div className="auth-card scale-in">
                    <div className="auth-header">
                        <h1 className="auth-title">{t('otp.title')}</h1>
                        <p className="auth-subtitle">{t('otp.otp_sent_email')}</p>
                        <p style={{ color: 'var(--text-muted)', marginTop: '8px' }}>{otpData?.emailHint}</p>
                    </div>
                    
                    {error && <Alert type="error">{error}</Alert>}
                    
                    <OTPInput onComplete={handleOtpVerify} disabled={loading} />
                    
                    <OTPTimer />
                    
                    <div className="flex justify-center gap-2 mt-3">
                        <GlowButton variant="secondary" onClick={handleResendOtp} disabled={loading}>
                            {t('otp.resend')}
                        </GlowButton>
                        <GlowButton variant="secondary" onClick={() => setShowOtp(false)}>
                            {t('common.cancel')}
                        </GlowButton>
                    </div>
                </div>
            </div>
        );
    }
    
    return (
        <div className="auth-container">
            <div className="auth-card scale-in">
                <div className="auth-header">
                    <h1 className="auth-title">{t('auth.login')}</h1>
                    <p className="auth-subtitle">{t('app.tagline')}</p>
                </div>
                
                {error && <Alert type="error">{error}</Alert>}
                
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">{t('auth.email')}</label>
                        <input
                            type="email"
                            className="form-input"
                            value={formData.email}
                            onChange={e => setFormData({...formData, email: e.target.value})}
                            placeholder="you@example.com"
                            required
                        />
                    </div>
                    
                    <div className="form-group">
                        <label className="form-label">{t('auth.password')}</label>
                        <input
                            type="password"
                            className="form-input"
                            value={formData.password}
                            onChange={e => setFormData({...formData, password: e.target.value})}
                            placeholder="••••••••"
                            required
                        />
                    </div>
                    
                    <GlowButton type="submit" block loading={loading}>
                        {t('auth.login_btn')}
                    </GlowButton>
                </form>
                
                <div className="auth-footer">
                    {t('auth.no_account')} <a href="#" onClick={() => onNavigate('register')}>{t('auth.register')}</a>
                </div>
            </div>
        </div>
    );
}

// ===================================
// Register Page Component
// ===================================
function RegisterPage({ onNavigate }) {
    const { t } = useContext(LanguageContext);
    const [formData, setFormData] = useState({ name: '', email: '', password: '', confirmPassword: '', mobile: '' });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        
        if (formData.password !== formData.confirmPassword) {
            setError(t('errors.passwords_match'));
            return;
        }
        
        if (formData.password.length < 6) {
            setError(t('errors.password_min'));
            return;
        }
        
        setLoading(true);
        
        const result = await API.register({
            name: formData.name,
            email: formData.email,
            password: formData.password,
            mobile: formData.mobile
        });
        
        setLoading(false);
        
        if (result.ok) {
            setSuccess(t('auth.register_success'));
            setTimeout(() => onNavigate('login'), 2000);
        } else {
            setError(result.data.message || t('errors.server_error'));
        }
    };
    
    return (
        <div className="auth-container">
            <div className="auth-card scale-in">
                <div className="auth-header">
                    <h1 className="auth-title">{t('auth.register')}</h1>
                    <p className="auth-subtitle">{t('app.tagline')}</p>
                </div>
                
                {error && <Alert type="error">{error}</Alert>}
                {success && <Alert type="success">{success}</Alert>}
                
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">{t('auth.name')}</label>
                        <input
                            type="text"
                            className="form-input"
                            value={formData.name}
                            onChange={e => setFormData({...formData, name: e.target.value})}
                            placeholder="John Doe"
                            required
                        />
                    </div>
                    
                    <div className="form-group">
                        <label className="form-label">{t('auth.email')}</label>
                        <input
                            type="email"
                            className="form-input"
                            value={formData.email}
                            onChange={e => setFormData({...formData, email: e.target.value})}
                            placeholder="you@example.com"
                            required
                        />
                    </div>
                    
                    <div className="form-group">
                        <label className="form-label">{t('auth.mobile')}</label>
                        <input
                            type="tel"
                            className="form-input"
                            value={formData.mobile}
                            onChange={e => setFormData({...formData, mobile: e.target.value})}
                            placeholder="+1234567890"
                            required
                        />
                    </div>
                    
                    <div className="form-group">
                        <label className="form-label">{t('auth.password')}</label>
                        <input
                            type="password"
                            className="form-input"
                            value={formData.password}
                            onChange={e => setFormData({...formData, password: e.target.value})}
                            placeholder="••••••••"
                            required
                        />
                    </div>
                    
                    <div className="form-group">
                        <label className="form-label">{t('auth.confirm_password')}</label>
                        <input
                            type="password"
                            className="form-input"
                            value={formData.confirmPassword}
                            onChange={e => setFormData({...formData, confirmPassword: e.target.value})}
                            placeholder="••••••••"
                            required
                        />
                    </div>
                    
                    <GlowButton type="submit" block loading={loading}>
                        {t('auth.register_btn')}
                    </GlowButton>
                </form>
                
                <div className="auth-footer">
                    {t('auth.have_account')} <a href="#" onClick={() => onNavigate('login')}>{t('auth.login')}</a>
                </div>
            </div>
        </div>
    );
}

// ===================================
// Dashboard Page Component
// ===================================
function DashboardPage() {
    const { user } = useContext(AuthContext);
    const { t, currentLanguage } = useContext(LanguageContext);
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('overview');
    
    useEffect(() => {
        loadDashboard();
    }, []);
    
    const loadDashboard = async () => {
        setLoading(true);
        const result = await API.getDashboard();
        if (result.ok) {
            setData(result.data);
        }
        setLoading(false);
    };
    
    if (loading) {
        return (
            <div className="main-content flex items-center justify-center" style={{ minHeight: '60vh' }}>
                <div className="loader-spinner"></div>
            </div>
        );
    }
    
    const langName = LANGUAGES.find(l => l.code === currentLanguage)?.native || 'English';
    
    return (
        <div className="main-content">
            <div className="dashboard-header blur-text">
                <h1 className="dashboard-title">
                    {t('dashboard.welcome')}, {data?.user?.name || user?.name}! 👋
                </h1>
                <p className="dashboard-subtitle">{t('dashboard.overview')}</p>
            </div>
            
            {/* Stats Grid */}
            <div className="stats-grid">
                <div className="stat-card fade-in stagger-1">
                    <div className="stat-icon">📊</div>
                    <div className="stat-value">{data?.statistics?.total_logins || 0}</div>
                    <div className="stat-label">{t('dashboard.total_logins')}</div>
                </div>
                
                <div className="stat-card fade-in stagger-2">
                    <div className="stat-icon">🕐</div>
                    <div className="stat-value">{data?.statistics?.recent_logins_24h || 0}</div>
                    <div className="stat-label">{t('dashboard.recent_logins')}</div>
                </div>
                
                <div className="stat-card fade-in stagger-3">
                    <div className="stat-icon">📱</div>
                    <div className="stat-value">{data?.statistics?.unique_devices || 0}</div>
                    <div className="stat-label">{t('dashboard.unique_devices')}</div>
                </div>
                
                <div className="stat-card fade-in stagger-4">
                    <div className="stat-icon">🌍</div>
                    <div className="stat-value">{langName}</div>
                    <div className="stat-label">{t('dashboard.current_language')}</div>
                </div>
            </div>
            
            {/* Tabs */}
            <div className="flex gap-2 mb-3">
                <GlowButton 
                    variant={activeTab === 'overview' ? 'primary' : 'secondary'}
                    onClick={() => setActiveTab('overview')}
                >
                    {t('dashboard.login_history')}
                </GlowButton>
                <GlowButton 
                    variant={activeTab === 'language' ? 'primary' : 'secondary'}
                    onClick={() => setActiveTab('language')}
                >
                    {t('dashboard.language_history')}
                </GlowButton>
            </div>
            
            {/* Login History Table */}
            {activeTab === 'overview' && (
                <div className="card fade-in">
                    <div className="card-header">
                        <h2 className="card-title">{t('dashboard.login_history')}</h2>
                    </div>
                    <div className="table-container">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>{t('history.browser')}</th>
                                    <th>{t('history.os')}</th>
                                    <th>{t('history.device')}</th>
                                    <th>{t('history.ip_address')}</th>
                                    <th>{t('history.time')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data?.recent_login_history?.length > 0 ? (
                                    data.recent_login_history.map((login, index) => (
                                        <tr key={index}>
                                            <td>{login.browser}</td>
                                            <td>{login.os}</td>
                                            <td>
                                                <span className={`badge badge-${login.device_type}`}>
                                                    {login.device_type}
                                                </span>
                                            </td>
                                            <td>{login.ip_address}</td>
                                            <td>{new Date(login.login_time).toLocaleString()}</td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan="5" className="text-center">{t('history.no_records')}</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
            
            {/* Language History Table */}
            {activeTab === 'language' && (
                <div className="card fade-in">
                    <div className="card-header">
                        <h2 className="card-title">{t('dashboard.language_history')}</h2>
                    </div>
                    <div className="table-container">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>{t('history.language')}</th>
                                    <th>{t('history.verified_by')}</th>
                                    <th>{t('history.time')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data?.recent_language_changes?.length > 0 ? (
                                    data.recent_language_changes.map((change, index) => (
                                        <tr key={index}>
                                            <td>
                                                {LANGUAGES.find(l => l.code === change.language)?.flag} {' '}
                                                {LANGUAGES.find(l => l.code === change.language)?.native || change.language.toUpperCase()}
                                            </td>
                                            <td>
                                                <span className={`badge badge-${change.verified_by === 'email' ? 'email' : 'mobile-otp'}`}>
                                                    {change.verified_by}
                                                </span>
                                            </td>
                                            <td>{new Date(change.change_time).toLocaleString()}</td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan="3" className="text-center">{t('history.no_records')}</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}

// ===================================
// Home Page Component
// ===================================
function HomePage({ onNavigate }) {
    const { t } = useContext(LanguageContext);
    const { user } = useContext(AuthContext);
    
    if (user) {
        return <DashboardPage />;
    }
    
    return (
        <div className="auth-container">
            <div className="text-center">
                <h1 className="dashboard-title blur-text" style={{ fontSize: '3rem', marginBottom: '16px' }}>
                    🔐 {t('app.name')}
                </h1>
                <p className="dashboard-subtitle blur-text" style={{ animationDelay: '0.2s', marginBottom: '32px' }}>
                    {t('app.tagline')}
                </p>
                
                <div className="flex justify-center gap-2 fade-in" style={{ animationDelay: '0.4s' }}>
                    <GlowButton onClick={() => onNavigate('login')}>
                        {t('auth.login')}
                    </GlowButton>
                    <GlowButton variant="secondary" onClick={() => onNavigate('register')}>
                        {t('auth.register')}
                    </GlowButton>
                </div>
                
                <div className="mt-4 fade-in" style={{ animationDelay: '0.6s' }}>
                    <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
                        <h3 className="card-title" style={{ fontSize: '1.2rem', marginBottom: '16px' }}>
                            ✨ Features
                        </h3>
                        <div style={{ textAlign: 'left', color: 'var(--text-secondary)' }}>
                            <p>🔒 <strong>Browser-based Security:</strong> Chrome requires OTP, Edge direct access</p>
                            <p>📱 <strong>Mobile Time Restriction:</strong> Access only 10 AM - 1 PM</p>
                            <p>🌍 <strong>Multilingual:</strong> 6 languages with OTP verification</p>
                            <p>📊 <strong>Login History:</strong> Track all your sessions</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ===================================
// Main App Component
// ===================================
function App() {
    const [user, setUser] = useState(null);
    const [currentLanguage, setCurrentLanguage] = useState('en');
    const [translations, setTranslations] = useState({});
    const [currentPage, setCurrentPage] = useState('home');
    const [loading, setLoading] = useState(true);
    
    // Load translations
    const loadTranslations = useCallback(async (lang) => {
        const result = await API.getTranslations(lang);
        if (result.ok) {
            setTranslations(result.data.translations);
        }
    }, []);
    
    // Check auth status on mount
    useEffect(() => {
        const checkAuth = async () => {
            const result = await API.getMe();
            if (result.ok && result.data.authenticated) {
                setUser(result.data.user);
            }
            setLoading(false);
        };
        
        checkAuth();
        loadTranslations(currentLanguage);
    }, []);
    
    // Handle navigation events
    useEffect(() => {
        const handleNavigate = (e) => setCurrentPage(e.detail);
        window.addEventListener('navigate', handleNavigate);
        return () => window.removeEventListener('navigate', handleNavigate);
    }, []);
    
    // Translation helper
    const t = useCallback((key) => {
        const keys = key.split('.');
        let value = translations;
        for (const k of keys) {
            value = value?.[k];
        }
        return value || key;
    }, [translations]);
    
    // Change language
    const changeLanguage = useCallback((lang) => {
        setCurrentLanguage(lang);
        loadTranslations(lang);
    }, [loadTranslations]);
    
    // Auth functions
    const login = useCallback((userData) => {
        setUser(userData);
    }, []);
    
    const logout = useCallback(async () => {
        await API.logout();
        setUser(null);
        setCurrentPage('home');
    }, []);
    
    // Navigate function
    const navigate = useCallback((page) => {
        setCurrentPage(page);
    }, []);
    
    if (loading) {
        return null; // Let the HTML loader show
    }
    
    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            <LanguageContext.Provider value={{ currentLanguage, changeLanguage, t }}>
                <div className="app-container">
                    <ParticleBackground />
                    <Navbar />
                    
                    {currentPage === 'home' && <HomePage onNavigate={navigate} />}
                    {currentPage === 'login' && <LoginPage onNavigate={navigate} />}
                    {currentPage === 'register' && <RegisterPage onNavigate={navigate} />}
                    {currentPage === 'dashboard' && user && <DashboardPage />}
                </div>
            </LanguageContext.Provider>
        </AuthContext.Provider>
    );
}

// ===================================
// Render App
// ===================================
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
