/**
 * PICKLE SPLIT-SCREEN AUTH TEMPLATE CONTROLLER
 * Handles Google Authentication (GIS), mode switching (Login vs Sign-up),
 * Testimonial Carousel, 3D Parallax Tilt, Password visibility toggle, and validation.
 */

// Google Client ID Configuration
const GOOGLE_CLIENT_ID = '587875318844-2nb5iekjk2i11v6kjfsnmsm7qmed99pm.apps.googleusercontent.com';

/**
 * Toast Notification Utility
 * Displays non-intrusive feedback toasts to the user.
 */
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : 'ℹ'}</span>
    <span>${message}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
window.showToast = showToast;

/**
 * Decodes the base64 URL encoded JWT payload from Google Identity Services
 * @param {string} token - The raw credential JWT token
 * @returns {object|null} - Decoded payload object containing user profile claims
 */
function decodeJwtResponse(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error decoding Google JWT token:', error);
    return null;
  }
}
window.decodeJwtResponse = decodeJwtResponse;

/**
 * Official Google Sign-In Callback Handler
 * Invoked automatically by Google Identity Services upon successful user authentication.
 * @param {object} response - Credential response containing the JWT token
 */
function handleCredentialResponse(response) {
  console.log('=== Google Authentication Response Received ===');
  console.log('Encoded JWT ID token:', response.credential);

  // Decode the JWT token to extract user profile details
  const payload = decodeJwtResponse(response.credential);

  if (payload) {
    // 4. Extract and console.log Profile Name, Email, and Picture
    console.log('=== Decoded User Profile Information ===');
    console.log('Profile Name:', payload.name);
    console.log('Email:', payload.email);
    console.log('Picture:', payload.picture);

    // Additional useful decoded claims
    console.log('User ID (sub):', payload.sub);
    console.log('Given Name:', payload.given_name);
    console.log('Family Name:', payload.family_name);
    console.log('Email Verified:', payload.email_verified);
    console.log('Full Payload Object:', payload);

    // Show friendly success toast
    showToast(`Welcome, ${payload.name}! Authenticated with Google (${payload.email}).`, 'success');

    // Auto-populate relevant form fields if available
    const emailInput = document.getElementById('email');
    const firstNameInput = document.getElementById('firstName');
    const lastNameInput = document.getElementById('lastName');

    if (emailInput && payload.email) {
      emailInput.value = payload.email;
    }
    if (firstNameInput && payload.given_name) {
      firstNameInput.value = payload.given_name;
    }
    if (lastNameInput && payload.family_name) {
      lastNameInput.value = payload.family_name;
    }
  } else {
    console.error('Failed to parse user profile from Google credential.');
    showToast('Failed to authenticate with Google.', 'info');
  }
}
window.handleCredentialResponse = handleCredentialResponse;

document.addEventListener('DOMContentLoaded', () => {
  // Elements: Switcher
  const topSwitchBtn = document.getElementById('topSwitchBtn');
  const topPromptText = document.getElementById('topPromptText');
  const formTitle = document.getElementById('formTitle');
  const formSubtitle = document.getElementById('formSubtitle');
  const googleBtn = document.getElementById('googleBtn');
  const dividerLabel = document.getElementById('dividerLabel');
  const nameFieldsRow = document.getElementById('nameFieldsRow');
  const forgotPassLink = document.getElementById('forgotPassLink');
  const rememberGroup = document.getElementById('rememberGroup');
  const submitBtn = document.getElementById('submitBtn');
  const submitBtnLabel = document.getElementById('submitBtnLabel');
  const legalText = document.getElementById('legalText');
  const emailLabel = document.getElementById('emailLabel');

  // Tabs: Find a job / Post a job
  const tabFindJob = document.getElementById('tabFindJob');
  const tabPostJob = document.getElementById('tabPostJob');

  // Form & inputs
  const authForm = document.getElementById('authForm');
  const firstNameInput = document.getElementById('firstName');
  const lastNameInput = document.getElementById('lastName');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const pwdToggleBtn = document.getElementById('pwdToggleBtn');
  const eyeShow = document.querySelector('.eye-show');
  const eyeHide = document.querySelector('.eye-hide');

  // Testimonials Carousel Data & Elements
  const quoteText = document.getElementById('quoteText');
  const authorAvatar = document.getElementById('authorAvatar');
  const authorName = document.getElementById('authorName');
  const authorRole = document.getElementById('authorRole');
  const dotBtns = document.querySelectorAll('.dot-btn');
  const testimonialCard = document.getElementById('testimonialCard');

  // Parallax Cluster
  const showcasePanel = document.getElementById('showcasePanel');
  const badgeCards = document.querySelectorAll('.badge-card');

  // Current State: 'signup' or 'login'
  let currentMode = 'signup';
  let currentTab = 'post'; // 'find' or 'post'

  const testimonials = [
    {
      quote: "Getting personalized, data-driven recommendations beyond clinic that align with my aims and values has been revolutionary. Tailored recommendations are key!",
      name: "Dr. Temi Akitikori",
      role: "OB/GYN, Femtech and Digital Health Strategist",
      avatar: "assets/testimonial-avatar.jpg"
    },
    {
      quote: "We hired 3 world-class clinical specialists in under 10 days through Pickle. The precision and quality of candidates here is unmatched anywhere else.",
      name: "Alex Vance",
      role: "Head of Talent, BioHealth Solutions",
      avatar: "assets/avatar-2.jpg"
    },
    {
      quote: "Pickle simplified our hiring roadmap completely. It connects us directly with certified practitioners who care about digital health innovation.",
      name: "Sarah Chen",
      role: "VP of People & Culture, MedVenture Group",
      avatar: "assets/avatar-3.jpg"
    }
  ];

  let currentSlide = 0;
  let slideInterval = null;

  /* ==========================================================================
     1. MODE SWITCHING (Sign-up <--> Login)
     ========================================================================== */
  function setMode(mode) {
    currentMode = mode;
    clearErrors();

    if (mode === 'login') {
      // Top switch text
      topPromptText.textContent = "Don't have an account?";
      topSwitchBtn.textContent = 'Sign up';

      // Header
      formTitle.textContent = 'Log in to Pickle';
      formSubtitle.textContent = 'Welcome back! Please enter your details to access your account.';

      // Social Button & Divider
      updateGoogleButton('login');
      dividerLabel.textContent = 'Or log in with email';

      // Fields visibility
      nameFieldsRow.style.display = 'none';
      forgotPassLink.style.display = 'inline';
      rememberGroup.style.display = 'block';

      // Inputs
      emailLabel.textContent = 'Email address';
      emailInput.placeholder = 'you@company.com';
      passwordInput.placeholder = 'Enter your password';

      // Button & Footer
      submitBtnLabel.textContent = 'Log in';
      legalText.innerHTML = `By logging in, you agree to our <a href="#terms" class="legal-link">Terms of Service</a> and <a href="#privacy" class="legal-link">Privacy Policy</a>`;

      // Disable required for hidden fields
      firstNameInput.removeAttribute('required');
      lastNameInput.removeAttribute('required');

    } else {
      // Sign up mode
      topPromptText.textContent = 'Already have an account?';
      topSwitchBtn.textContent = 'Log in';

      if (currentTab === 'post') {
        formTitle.textContent = 'Post on Pickle';
        formSubtitle.textContent = 'Looking for your next healthcare hire? Complete the details below to get started.';
      } else {
        formTitle.textContent = 'Join Pickle';
        formSubtitle.textContent = 'Find top-tier clinical and healthcare roles tailored to your career goals.';
      }

      updateGoogleButton('signup');
      dividerLabel.textContent = 'Or sign up with email';

      nameFieldsRow.style.display = 'flex';
      forgotPassLink.style.display = 'none';
      rememberGroup.style.display = 'none';

      emailLabel.textContent = 'Work email';
      emailInput.placeholder = 'jane.doe@company.com';
      passwordInput.placeholder = '••••••••••••';

      submitBtnLabel.textContent = 'Sign up';
      legalText.innerHTML = `By creating your account, you agree to our <a href="#terms" class="legal-link">Terms of Service</a> and <a href="#privacy" class="legal-link">Privacy Policy</a>`;

      firstNameInput.setAttribute('required', 'true');
      lastNameInput.setAttribute('required', 'true');
    }
  }

  topSwitchBtn.addEventListener('click', () => {
    setMode(currentMode === 'signup' ? 'login' : 'signup');
  });

  /* ==========================================================================
     2. SEGMENT TABS (Find a job / Post a job)
     ========================================================================== */
  function setActiveTab(tab) {
    currentTab = tab;
    if (tab === 'find') {
      tabFindJob.classList.add('active');
      tabFindJob.setAttribute('aria-selected', 'true');
      tabFindJob.innerHTML = 'Find a job <span class="active-indicator"></span>';

      tabPostJob.classList.remove('active');
      tabPostJob.setAttribute('aria-selected', 'false');
      tabPostJob.innerHTML = 'Post a job';

      if (currentMode === 'signup') {
        formTitle.textContent = 'Join Pickle';
        formSubtitle.textContent = 'Find top-tier clinical and healthcare roles tailored to your career goals.';
      }
    } else {
      tabPostJob.classList.add('active');
      tabPostJob.setAttribute('aria-selected', 'true');
      tabPostJob.innerHTML = 'Post a job <span class="active-indicator"></span>';

      tabFindJob.classList.remove('active');
      tabFindJob.setAttribute('aria-selected', 'false');
      tabFindJob.innerHTML = 'Find a job';

      if (currentMode === 'signup') {
        formTitle.textContent = 'Post on Pickle';
        formSubtitle.textContent = 'Looking for your next healthcare hire? Complete the details below to get started.';
      }
    }
  }

  tabFindJob.addEventListener('click', () => setActiveTab('find'));
  tabPostJob.addEventListener('click', () => setActiveTab('post'));

  /* ==========================================================================
     3. PASSWORD VISIBILITY TOGGLE
     ========================================================================== */
  pwdToggleBtn.addEventListener('click', () => {
    const isPassword = passwordInput.getAttribute('type') === 'password';
    if (isPassword) {
      passwordInput.setAttribute('type', 'text');
      eyeShow.style.display = 'none';
      eyeHide.style.display = 'inline';
    } else {
      passwordInput.setAttribute('type', 'password');
      eyeShow.style.display = 'inline';
      eyeHide.style.display = 'none';
    }
  });

  /* ==========================================================================
     4. TESTIMONIAL CAROUSEL
     ========================================================================== */
  function showSlide(index) {
    if (index === currentSlide) return;
    currentSlide = index;

    // Cross-fade animation
    quoteText.style.opacity = '0';
    quoteText.style.transform = 'translateY(6px)';
    authorAvatar.style.opacity = '0';
    authorName.style.opacity = '0';
    authorRole.style.opacity = '0';

    setTimeout(() => {
      const data = testimonials[index];
      quoteText.textContent = `"${data.quote}"`;
      authorAvatar.src = data.avatar;
      authorAvatar.alt = data.name;
      authorName.textContent = data.name;
      authorRole.textContent = data.role;

      dotBtns.forEach((dot, idx) => {
        const isActive = idx === index;
        dot.classList.toggle('active', isActive);
        dot.setAttribute('aria-selected', isActive ? 'true' : 'false');
      });

      quoteText.style.opacity = '1';
      quoteText.style.transform = 'translateY(0)';
      authorAvatar.style.opacity = '1';
      authorName.style.opacity = '1';
      authorRole.style.opacity = '1';
    }, 180);
  }

  dotBtns.forEach((dot) => {
    dot.addEventListener('click', () => {
      const idx = parseInt(dot.getAttribute('data-index'), 10);
      showSlide(idx);
      resetAutoSlide();
    });
  });

  function startAutoSlide() {
    slideInterval = setInterval(() => {
      const nextSlide = (currentSlide + 1) % testimonials.length;
      showSlide(nextSlide);
    }, 6000);
  }

  function resetAutoSlide() {
    clearInterval(slideInterval);
    startAutoSlide();
  }

  if (testimonialCard) {
    testimonialCard.addEventListener('mouseenter', () => clearInterval(slideInterval));
    testimonialCard.addEventListener('mouseleave', () => startAutoSlide());
  }

  startAutoSlide();

  /* ==========================================================================
     5. INTERACTIVE 3D PARALLAX ON BADGE CLUSTER
     ========================================================================== */
  if (showcasePanel && window.matchMedia('(min-width: 900px)').matches) {
    showcasePanel.addEventListener('mousemove', (e) => {
      const rect = showcasePanel.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;

      badgeCards.forEach((card) => {
        const depth = parseFloat(card.getAttribute('data-depth') || '0.15');
        const moveX = x * 35 * depth;
        const moveY = y * 35 * depth;
        const rotate = (x * 8);

        // Keep intrinsic tilt while layering parallax
        card.style.transform = `translate(${moveX}px, ${moveY}px) rotate(${rotate}deg)`;
      });
    });

    showcasePanel.addEventListener('mouseleave', () => {
      badgeCards.forEach((card) => {
        card.style.transform = '';
      });
    });
  }

  /* ==========================================================================
     6. FORM VALIDATION & SUBMISSION
     ========================================================================== */
  function clearErrors() {
    document.querySelectorAll('.input-error-msg').forEach((el) => (el.textContent = ''));
    document.querySelectorAll('.form-input').forEach((el) => el.classList.remove('is-invalid'));
  }

  function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  authForm.addEventListener('submit', (e) => {
    e.preventDefault();
    clearErrors();

    let isValid = true;

    // First and last name validation for sign up
    if (currentMode === 'signup') {
      if (!firstNameInput.value.trim()) {
        showError('firstName', 'Please enter your first name');
        isValid = false;
      }
      if (!lastNameInput.value.trim()) {
        showError('lastName', 'Please enter your last name');
        isValid = false;
      }
    }

    // Email validation
    const emailVal = emailInput.value.trim();
    if (!emailVal) {
      showError('email', 'Email address is required');
      isValid = false;
    } else if (!validateEmail(emailVal)) {
      showError('email', 'Please enter a valid email address');
      isValid = false;
    }

    // Password validation
    const passVal = passwordInput.value;
    if (!passVal) {
      showError('password', 'Password is required');
      isValid = false;
    } else if (passVal.length < 8) {
      showError('password', 'Password must be at least 8 characters');
      isValid = false;
    }

    if (!isValid) return;

    // Loading state simulation
    submitBtn.classList.add('is-loading');
    submitBtn.setAttribute('disabled', 'true');

    setTimeout(() => {
      submitBtn.classList.remove('is-loading');
      submitBtn.removeAttribute('disabled');

      if (currentMode === 'signup') {
        showToast(`Account created for ${emailVal}! Welcome to Pickle.`, 'success');
      } else {
        showToast(`Welcome back! Successfully logged in.`, 'success');
      }
    }, 1200);
  });

  function showError(fieldId, message) {
    const input = document.getElementById(fieldId);
    const errorEl = document.getElementById(`${fieldId}Error`);
    if (input) input.classList.add('is-invalid');
    if (errorEl) errorEl.textContent = message;
  }

  // Inform developer if opening directly via file:// protocol
  if (window.location.protocol === 'file:') {
    console.warn(
      '⚠️ Note: Google Identity Services requires an authorized HTTP/HTTPS origin (e.g. http://localhost:5500). If running locally, serve this folder with a local server like Live Server or "npx serve".'
    );
  }

  // Forgot password click
  forgotPassLink.addEventListener('click', (e) => {
    e.preventDefault();
    showToast('Password reset link will be sent to your email.', 'success');
  });

  /* ==========================================================================
     7. GOOGLE SIGN-IN BUTTON RESPONSIVE CONTROLLER
     ========================================================================== */
  function updateGoogleButton(mode) {
    if (!googleBtn) return;
    const buttonText = mode === 'login' ? 'signin_with' : 'signup_with';
    googleBtn.setAttribute('data-text', buttonText);

    // If GIS script is loaded, re-render to apply current width and text dynamically
    if (typeof google !== 'undefined' && google.accounts && google.accounts.id) {
      const wrapperWidth = googleBtn.parentElement ? googleBtn.parentElement.offsetWidth : 380;
      const responsiveWidth = Math.max(200, Math.min(wrapperWidth || 380, 400));

      googleBtn.innerHTML = '';
      google.accounts.id.renderButton(googleBtn, {
        type: 'standard',
        shape: 'rectangular',
        theme: 'outline',
        text: buttonText,
        size: 'large',
        logo_alignment: 'left',
        width: responsiveWidth
      });
    }
  }

  // Handle responsive resizing of Google Sign-In button
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      updateGoogleButton(currentMode);
    }, 150);
  });

  // Check URL hash or default to 'login' mode for login template
  const initialMode = window.location.hash.toLowerCase().includes('signup') ? 'signup' : 'login';
  setMode(initialMode);
});

