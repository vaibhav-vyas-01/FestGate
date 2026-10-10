/**
 * FESTGATE SPLIT-SCREEN AUTH CONTROLLER
 * Manages Role Switching (Participant vs Organizer),
 * Mode Switching (Login vs Sign-up), Password Toggle, Testimonial Carousel,
 * and Client-side Validations.
 */

// Toast Notification Utility
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : '⚠️'}</span>
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

document.addEventListener('DOMContentLoaded', () => {
  // Elements: Switcher
  const topSwitchBtn = document.getElementById('topSwitchBtn');
  const topPromptText = document.getElementById('topPromptText');
  const formTitle = document.getElementById('formTitle');
  const formSubtitle = document.getElementById('formSubtitle');
  const dividerLabel = document.getElementById('dividerLabel');
  const nameGroup = document.getElementById('nameGroup');
  const clubGroup = document.getElementById('clubGroup');
  const confirmPasswordGroup = document.getElementById('confirmPasswordGroup');
  const forgotPassLink = document.getElementById('forgotPassLink');
  const submitBtn = document.getElementById('submitBtn');
  const submitBtnLabel = document.getElementById('submitBtnLabel');
  const legalText = document.getElementById('legalText');
  const emailLabel = document.getElementById('emailLabel');
  const googleBtnDisabled = document.getElementById('googleBtnDisabled');

  // Tabs: Participant / Organizer
  const tabParticipant = document.getElementById('tabParticipant');
  const tabOrganizer = document.getElementById('tabOrganizer');

  // Form & inputs
  const authForm = document.getElementById('authForm');
  const fullNameInput = document.getElementById('fullName');
  const clubNameInput = document.getElementById('clubName');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const confirmPasswordInput = document.getElementById('confirmPassword');
  const pwdToggleBtn = document.getElementById('pwdToggleBtn');
  const eyeShow = document.querySelector('.eye-show');
  const eyeHide = document.querySelector('.eye-hide');

  // Error Message Spans
  const nameError = document.getElementById('nameError');
  const clubError = document.getElementById('clubError');
  const emailError = document.getElementById('emailError');
  const passwordError = document.getElementById('passwordError');
  const confirmPasswordError = document.getElementById('confirmPasswordError');

  // Testimonials Carousel Data & Elements
  const quoteText = document.getElementById('quoteText');
  const authorAvatarInitials = document.getElementById('authorAvatarInitials');
  const authorName = document.getElementById('authorName');
  const authorRole = document.getElementById('authorRole');
  const dotBtns = document.querySelectorAll('.dot-btn');

  // State: 'login' or 'signup', and role: 'participant' or 'organizer'
  let currentMode = 'login';
  let currentRole = 'participant';

  const testimonials = [
    {
      quote: "FestGate made entry management effortless during our annual cultural fest. Over 2,500 students checked in smoothly without any gate bottlenecks!",
      name: "Aarav Sharma",
      role: "Lead Coordinator, Campus Fest Council",
      initials: "AS"
    },
    {
      quote: "The instant QR pass and duplicate-email block made our 48-hour hackathon check-in the fastest we've ever conducted.",
      name: "Tanvi Deshmukh",
      role: "Hackathon Lead, Tech Club",
      initials: "TD"
    },
    {
      quote: "Having every college event under one gate saves our volunteer team hours of manual verification work every semester.",
      name: "Rahul Verma",
      role: "Student Council President",
      initials: "RV"
    }
  ];

  let currentSlide = 0;
  let slideInterval = null;

  /* ==========================================================================
     1. FORM VIEW UPDATER
     ========================================================================== */
  function updateFormView() {
    clearErrors();

    if (currentMode === 'login') {
      topPromptText.textContent = "Don't have an account?";
      topSwitchBtn.textContent = 'Sign up';
      dividerLabel.textContent = 'Or log in with email';
      submitBtnLabel.textContent = 'Log in';
      emailLabel.textContent = 'Email address';
      emailInput.placeholder = 'you@college.edu';

      if (currentRole === 'organizer') {
        formTitle.textContent = 'Log in to FestGate';
        formSubtitle.textContent = 'Log in to manage your campus events';
      } else {
        formTitle.textContent = 'Log in to FestGate';
        formSubtitle.textContent = 'Log in to get your event pass';
      }

      // Hide signup-specific inputs
      if (nameGroup) nameGroup.style.display = 'none';
      if (clubGroup) clubGroup.style.display = 'none';
      if (confirmPasswordGroup) confirmPasswordGroup.style.display = 'none';
      if (forgotPassLink) forgotPassLink.style.display = 'inline';

      legalText.textContent = 'By logging in, you agree to our Terms of Service and Privacy Policy';

      fullNameInput.removeAttribute('required');
      if (clubNameInput) clubNameInput.removeAttribute('required');
      if (confirmPasswordInput) confirmPasswordInput.removeAttribute('required');

    } else {
      // Sign-up mode
      topPromptText.textContent = 'Already have an account?';
      topSwitchBtn.textContent = 'Log in';
      dividerLabel.textContent = 'Or sign up with email';
      submitBtnLabel.textContent = 'Create Account';
      emailLabel.textContent = currentRole === 'organizer' ? 'Official / Club Email' : 'Student Email';
      emailInput.placeholder = currentRole === 'organizer' ? 'club.lead@college.edu' : 'alex@college.edu';

      if (currentRole === 'organizer') {
        formTitle.textContent = 'Create Organizer Account';
        formSubtitle.textContent = 'Set up your club or committee profile to host campus events';
        if (clubGroup) clubGroup.style.display = 'flex';
        if (clubNameInput) clubNameInput.setAttribute('required', 'true');
      } else {
        formTitle.textContent = 'Join FestGate';
        formSubtitle.textContent = 'Create your attendee account to get instant event passes';
        if (clubGroup) clubGroup.style.display = 'none';
        if (clubNameInput) clubNameInput.removeAttribute('required');
      }

      // Show name and confirm password
      if (nameGroup) nameGroup.style.display = 'flex';
      if (confirmPasswordGroup) confirmPasswordGroup.style.display = 'flex';
      if (forgotPassLink) forgotPassLink.style.display = 'none';

      legalText.textContent = 'By creating your account, you agree to our Terms of Service and Privacy Policy';

      fullNameInput.setAttribute('required', 'true');
      if (confirmPasswordInput) confirmPasswordInput.setAttribute('required', 'true');
    }
  }

  // Toggle Mode (Login <--> Sign up)
  topSwitchBtn.addEventListener('click', () => {
    currentMode = currentMode === 'login' ? 'signup' : 'login';
    updateFormView();
  });

  /* ==========================================================================
     2. SEGMENTED ROLE TABS (Participant / Organizer)
     ========================================================================== */
  function setActiveRole(role) {
    currentRole = role;
    if (role === 'participant') {
      tabParticipant.classList.add('active');
      tabParticipant.setAttribute('aria-selected', 'true');
      tabParticipant.innerHTML = 'Participant <span class="active-indicator"></span>';

      tabOrganizer.classList.remove('active');
      tabOrganizer.setAttribute('aria-selected', 'false');
      tabOrganizer.innerHTML = 'Organizer';
    } else {
      tabOrganizer.classList.add('active');
      tabOrganizer.setAttribute('aria-selected', 'true');
      tabOrganizer.innerHTML = 'Organizer <span class="active-indicator"></span>';

      tabParticipant.classList.remove('active');
      tabParticipant.setAttribute('aria-selected', 'false');
      tabParticipant.innerHTML = 'Participant';
    }
    updateFormView();
  }

  tabParticipant.addEventListener('click', () => setActiveRole('participant'));
  tabOrganizer.addEventListener('click', () => setActiveRole('organizer'));

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
     4. GOOGLE BUTTON (Disabled placeholder feedback)
     ========================================================================== */
  if (googleBtnDisabled) {
    googleBtnDisabled.addEventListener('click', (e) => {
      e.preventDefault();
      showToast('Google Sign-in is coming soon! Please use email login.', 'error');
    });
  }

  /* ==========================================================================
     5. TESTIMONIAL CAROUSEL
     ========================================================================== */
  function showSlide(index) {
    currentSlide = index;
    const slide = testimonials[index];

    quoteText.style.opacity = '0';
    quoteText.style.transform = 'translateY(6px)';

    setTimeout(() => {
      quoteText.textContent = `"${slide.quote}"`;
      authorName.textContent = slide.name;
      authorRole.textContent = slide.role;
      if (authorAvatarInitials) {
        authorAvatarInitials.textContent = slide.initials;
      }

      quoteText.style.opacity = '1';
      quoteText.style.transform = 'translateY(0)';
    }, 180);

    dotBtns.forEach((dot, idx) => {
      if (idx === index) {
        dot.classList.add('active');
        dot.setAttribute('aria-selected', 'true');
      } else {
        dot.classList.remove('active');
        dot.setAttribute('aria-selected', 'false');
      }
    });
  }

  function startAutoplay() {
    stopAutoplay();
    slideInterval = setInterval(() => {
      const nextSlide = (currentSlide + 1) % testimonials.length;
      showSlide(nextSlide);
    }, 6000);
  }

  function stopAutoplay() {
    if (slideInterval) clearInterval(slideInterval);
  }

  dotBtns.forEach((dot) => {
    dot.addEventListener('click', (e) => {
      const idx = parseInt(e.target.getAttribute('data-index'), 10);
      showSlide(idx);
      startAutoplay();
    });
  });

  const testimonialCard = document.getElementById('testimonialCard');
  if (testimonialCard) {
    testimonialCard.addEventListener('mouseenter', stopAutoplay);
    testimonialCard.addEventListener('mouseleave', startAutoplay);
  }

  startAutoplay();

  /* ==========================================================================
     6. VALIDATION & SUBMISSION
     ========================================================================== */
  function clearErrors() {
    [nameError, clubError, emailError, passwordError, confirmPasswordError].forEach((el) => {
      if (el) el.textContent = '';
    });
    document.querySelectorAll('.form-input').forEach((input) => {
      input.classList.remove('is-invalid');
    });
  }

  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  authForm.addEventListener('submit', (e) => {
    e.preventDefault();
    clearErrors();

    let isValid = true;
    const emailVal = emailInput.value.trim();
    const passVal = passwordInput.value;

    if (currentMode === 'signup') {
      const nameVal = fullNameInput.value.trim();
      if (!nameVal) {
        nameError.textContent = 'Please enter your full name.';
        fullNameInput.classList.add('is-invalid');
        isValid = false;
      }

      if (currentRole === 'organizer' && clubNameInput) {
        const clubVal = clubNameInput.value.trim();
        if (!clubVal) {
          clubError.textContent = 'Please enter your college or club name.';
          clubNameInput.classList.add('is-invalid');
          isValid = false;
        }
      }

      if (confirmPasswordInput) {
        const confirmVal = confirmPasswordInput.value;
        if (passVal !== confirmVal) {
          confirmPasswordError.textContent = 'Passwords do not match.';
          confirmPasswordInput.classList.add('is-invalid');
          isValid = false;
        }
      }
    }

    if (!emailVal) {
      emailError.textContent = 'Please enter your email.';
      emailInput.classList.add('is-invalid');
      isValid = false;
    } else if (!validateEmail(emailVal)) {
      emailError.textContent = 'Please enter a valid email address.';
      emailInput.classList.add('is-invalid');
      isValid = false;
    }

    if (!passVal) {
      passwordError.textContent = 'Please enter your password.';
      passwordInput.classList.add('is-invalid');
      isValid = false;
    } else if (passVal.length < 8) {
      passwordError.textContent = 'Password must be at least 8 characters.';
      passwordInput.classList.add('is-invalid');
      isValid = false;
    }

    if (!isValid) return;

    // Simulate submission state
    submitBtn.classList.add('is-loading');
    submitBtn.disabled = true;

    setTimeout(() => {
      submitBtn.classList.remove('is-loading');
      submitBtn.disabled = false;

      if (currentMode === 'signup') {
        showToast(`Account created for ${emailVal}! Please log in.`, 'success');
        currentMode = 'login';
        updateFormView();
      } else {
        showToast(`Welcome back to FestGate (${currentRole})!`, 'success');
      }
    }, 1000);
  });

  // Initial render
  updateFormView();
});
