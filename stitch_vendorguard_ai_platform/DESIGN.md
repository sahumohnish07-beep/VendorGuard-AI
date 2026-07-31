---
name: Deep Slate Sentinel
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#adc6ff'
  on-secondary: '#002e6a'
  secondary-container: '#0566d9'
  on-secondary-container: '#e6ecff'
  tertiary: '#ffb3ad'
  on-tertiary: '#68000a'
  tertiary-container: '#ff7a73'
  on-tertiary-container: '#79000e'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#adc6ff'
  on-secondary-fixed: '#001a42'
  on-secondary-fixed-variant: '#004395'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#ffb3ad'
  on-tertiary-fixed: '#410004'
  on-tertiary-fixed-variant: '#930013'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  container-padding: 24px
  gutter: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
  sidebar-width: 260px
---

## Brand & Style

The design system is engineered for **VendorGuard AI**, an enterprise platform where security, autonomy, and data density are paramount. The personality is authoritative and agentic, positioning the AI not just as a tool, but as a reliable guardian. 

The aesthetic blends **Modern Corporate** efficiency with **High-Tech Minimalism**. It utilizes a "Dark Mode First" philosophy to reduce eye strain during long-term monitoring and to emphasize the glowing status of AI-driven insights. The interface feels like a sophisticated command center—stable, precise, and uncompromisingly professional. 

Key visual drivers:
- **Data-Dense Layouts:** Maximizing information display without clutter.
- **Agentic Feedback:** Using subtle motion and distinct accent colors to signify autonomous AI actions.
- **Reliability:** Heavy use of structured grids and consistent border treatments to evoke a sense of structural integrity.

## Colors

The palette is anchored in a deep, professional slate that provides a high-contrast foundation for data visualization.

- **Background & Surfaces:** The primary canvas uses `#0F172A`. Containers and cards sit one level higher at `#1E293B` to create a logical hierarchy of information.
- **Accents:** 
    - **Emerald Green (#10B981):** Reserved for successful AI validations, approvals, and "healthy" system states.
    - **AI Blue (#3B82F6):** Used for information, processing states, and primary interactive elements.
    - **Crimson Red (#EF4444):** Specifically for security breaches, anomalies, and critical risk factors.
- **Borders:** All structural boundaries use `#334155`. This low-contrast separation maintains a clean look while defining the "Terminal" feel.

## Typography

This design system utilizes **Inter** for all primary UI elements to ensure maximum legibility at small sizes. The typographic scale is optimized for high information density.

- **Headlines:** Use tighter letter-spacing and heavier weights to stand out against the dark background.
- **Labels:** Small, uppercase labels with increased letter-spacing are used for categorization and table headers to mimic technical documentation.
- **Mono Space:** **JetBrains Mono** is introduced for terminal-style consoles and raw data snippets, providing a clear distinction between narrative AI reasoning and hard system data.

## Layout & Spacing

The layout follows a **Fixed-Fluid Hybrid** model. The sidebar remains fixed at 260px, while the main dashboard content utilizes a fluid grid to maximize the visibility of data tables and charts.

- **The Grid:** A 12-column system with a 16px gutter. In "Control Center" views, columns may be split into 3 or 4 equal-width KPI cards.
- **Density:** Padding is intentionally kept tight (12px to 16px inside cards) to ensure that more data is visible above the fold. 
- **Breakpoints:**
    - **Desktop (1440px+):** Full sidebar, 12-column grid.
    - **Tablet (768px - 1439px):** Collapsed icon-only sidebar, 8-column grid.
    - **Mobile (<767px):** Single column stack, hidden sidebar with hamburger menu.

## Elevation & Depth

In this dark slate environment, depth is conveyed through **Tonal Layering** and **Low-Contrast Outlines** rather than traditional shadows.

- **Level 0 (Base):** `#0F172A` - The foundation layer.
- **Level 1 (Cards/Sidebar):** `#1E293B` - Elevated components. These always feature a 1px solid border of `#334155`.
- **Level 2 (Modals/Popovers):** `#2D3748` - Floating elements. These receive a subtle, high-spread shadow (`0 12px 24px rgba(0,0,0,0.4)`) to distinguish them from the card layer.
- **Interactive State:** Buttons and clickable rows use a subtle background-color shift on hover (lightening the slate by 5%) rather than physical lift.

## Shapes

The design system uses **Soft** geometry (`0.25rem`) to maintain a professional, architectural feel. 

- **Containers:** Cards and primary sections use the standard `rounded` (4px).
- **Interactive Elements:** Buttons and input fields use the same 4px radius for a unified, "blocked-in" appearance.
- **Status Pills:** The only exception—these are fully rounded (pill-shaped) to distinguish them from structural elements and buttons.

## Components

### Buttons
- **Primary:** Background `#3B82F6`, Text `#FFFFFF`. No gradient.
- **Secondary:** Transparent background, Border `#334155`, Text `#F8FAFC`.
- **Ghost:** No background or border, Text `#94A3B8`.

### AI Reasoning Cards
Special containers featuring a subtle left-accent border of `#3B82F6` and a slightly lighter background (`#232F3E`). These use **JetBrains Mono** for "Log" data and **Inter** for the AI's natural language summary.

### Status Pills
- **Active/Approved:** Emerald Green background (15% opacity), Emerald Green text.
- **Risk/Breach:** Red background (15% opacity), Red text.
- **Neutral/Pending:** Slate background (15% opacity), Slate text.

### Data Tables
- **Header:** Background `#1E293B`, Text `#94A3B8` (Label-MD style), 1px bottom-border `#334155`.
- **Row:** High-contrast primary text. Hover state shifts background to `#263345`.

### Terminal-Style Console
A dedicated component for raw AI logs. Background `#020617` (near black), text `#10B981` (Emerald), using `code-md` typography. No rounded corners on the bottom edge to simulate an integrated hardware screen.