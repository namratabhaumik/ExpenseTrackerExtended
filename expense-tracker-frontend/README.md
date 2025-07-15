## Responsive Navbar

This project now uses a custom, production-ready Navbar component (`src/Navbar.js`) styled exclusively with Tailwind CSS and the Minimal Neutrals palette:

- **Primary:** #4B5563 (Slate Gray)
- **Secondary:** #9CA3AF (Light Gray)
- **Accent:** #2563EB (Blue)
- **Background:** #F9FAFB (Lightest Gray)
- **Success:** #10B981 (Emerald Green)
- **Error:** #EF4444 (Red)

### Features

- Responsive: Desktop/tablet shows full nav, mobile uses a hamburger menu with a slide-in overlay.
- Accessible: Keyboard and screen reader friendly.
- Navigation links: Dashboard, Expenses, Categories, Profile, Logout.
- Clean, modern look with smooth transitions and correct color usage.

### Customization

- To change navigation links, edit the `NAV_LINKS` and `USER_LINKS` arrays in `src/Navbar.js`.
- To customize colors, update your `tailwind.config.js` to include the Minimal Neutrals palette for easy class usage.

### Integration

- The Navbar is imported and rendered at the top of the app in `src/App.js`.
- The old header/nav and React logo have been removed for a cleaner, more professional UI.

## Modern Login/Signup UI

- The Login/Signup form now features a modern, responsive UI with a global dark/light theme toggle (🌙/☀️ button, persists in localStorage).
- The theme toggle is now a global button in the top right corner of the screen on the login/signup page, with persistent theme preference in localStorage. This improves accessibility and visual consistency. The toggle is no longer inside the form box.
- Loading spinners (using `react-spinners`) are shown on login and signup buttons during async actions.
- Input fields have improved focus effects and accessibility, with ARIA labels and keyboard navigation.
- The color palette uses 'Minimal Neutrals':
  - Slate: #4B5563
  - Gray: #9CA3AF
  - Blue: #2563EB
- Dark mode is fully supported for all screens and components.
- All UI is responsive and accessible.

## Navigation Bar

- A persistent navigation bar (Navbar) is shown for authenticated users.
- Navigation links: Dashboard, Expenses, Profile (with active state indicator).
- Responsive: Collapses into a hamburger menu on mobile (max-width: 768px).
- Styled with Tailwind CSS for modern look and accessibility.
- Logout button included in the Navbar.

## Expenses Summary, Sorting, and Filtering

- A summary card at the top shows the total expenses, styled with the 'Minimal Neutrals' palette.
- Dropdowns allow sorting expenses by date (newest/oldest) or amount (high-low/low-high).
- A text input filters expenses by category in real time.
- The expense table updates dynamically as you sort or filter.
- All new UI is styled with Tailwind CSS and is fully responsive.

## Toast Notifications

- Success and error messages in Expenses (e.g., adding expenses, uploading receipts) now use toast notifications via react-toastify.
- Toasts are styled to match the app's 'Minimal Neutrals' palette and are accessible and responsive.
- The notification system provides immediate feedback for user actions.
- Previous toast messages are automatically dismissed when new ones are triggered for a cleaner experience.
- Loading spinners appear during API calls to improve user feedback and prevent multiple submissions.

## Dashboard Component

- A comprehensive dashboard displays expense summaries and recent transactions.
- Summary cards show total expenses, transaction count, and average per transaction.
- Recent expenses table displays the 5 most recent transactions with sorting by date.
- Fetches real data from the API using accessToken, with fallback to sample data.
- Styled with Tailwind CSS using the 'Minimal Neutrals' palette and dark mode support.
- Fully responsive design that integrates with the navigation system.

## Categories and Profile Components

- Categories component displays a polished placeholder UI for category management with loading indicators.
- Profile component shows account settings interface with similar placeholder design.
- Both components use ClipLoader from react-spinners as loading indicators.
- Styled with Tailwind CSS using the 'Minimal Neutrals' palette and responsive design.
- Integrated with the navigation system for seamless user experience.

## Navbar Enhancements

- Sticky navbar with subtle shadow that remains fixed at the top while scrolling.
- 3px blue underline (#2563EB) for active page links with smooth transitions.
- Hover animations with scale-up effect (1.05x) and 0.2s transitions for all interactive elements.
- Slide-in animation (0.3s) for mobile menu from right to left.
- Enhanced accessibility with ARIA roles (aria-current, aria-label, aria-expanded) and keyboard navigation support.
- Focus rings and proper tab navigation for screen readers.
- Responsive design with smooth animations across all device sizes.

## Layout and Navigation Enhancements

- **Centered Layout**: All page content is now centered with max-width containers (max-w-7xl) and consistent padding for better visual balance.
- **Styled Navbar Buttons**: Navigation buttons feature rounded corners (rounded-md), consistent spacing (px-3 py-2), and enhanced hover effects with scale animations.
- **Persistent Dark Mode Toggle**: Dark mode toggle moved to navbar top-right corner, visible on all authenticated pages with sun/moon icons and localStorage persistence.
- **Improved Table Design**: Dashboard table enhanced with borders, alternating row colors, proper cell padding, and hover effects for better readability.
- **Visual Hierarchy**: Enhanced typography with larger headings (text-3xl for main titles, text-2xl for subtitles), better spacing between sections, and improved color contrast.
- **Background Gradients**: Subtle background gradients applied to the entire app (light: #F9FAFB to #E5E7EB, dark: #4B5563 to #1F2937) for depth and modern appearance.
- **Responsive Design**: All components maintain proper spacing and layout across mobile, tablet, and desktop screens.
- **Smooth Transitions**: Theme switching and interactive elements feature smooth 0.3s transitions for a polished user experience.

## Accessibility Improvements

- The theme toggle is now always accessible in the top right corner of the screen, improving keyboard and screen reader access for all users.

## UI/UX Improvements

### Navbar Visual Polish (2024-06)

- Navigation buttons are now always horizontally aligned, never stacked or overlapping.
- Buttons have consistent spacing, min-width, subtle box-shadow, and a blue hover/active effect for a modern look.
- Navbar never overlaps content and remains sticky at the top.
- A fallback Navbar is shown for unauthenticated/demo mode to ensure navigation always looks polished for testing.
- All navigation uses flexbox for alignment and spacing.

## Bug Fixes & Improvements

- Expenses page now always fetches the latest expenses from the backend after login and after adding a new expense. This ensures all past and new expenses are visible, even across devices or sessions.
- The color palette is now fully emerald/teal; all blue accents have been removed for a consistent, modern look.
