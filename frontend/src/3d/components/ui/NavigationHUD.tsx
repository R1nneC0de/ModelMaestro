import { useEffect, useState } from 'react';
import { useCurrentView, useIsTransitioning, useFocusedBodyId } from '../../store/navigationStore';
import { NAVIGATION_NODES } from '../../config/navigationNodes';
import './NavigationHUD.css';

/**
 * NavigationHUD Component
 * 
 * Persistent heads-up display for navigation hints and current state.
 * Shows navigation controls, loading states, and keyboard shortcuts.
 * 
 * Requirements: 1.4, 8.3
 */

export interface NavigationHUDProps {
  showControls?: boolean;
}

export function NavigationHUD({ showControls = true }: NavigationHUDProps) {
  const currentView = useCurrentView();
  const isTransitioning = useIsTransitioning();
  const focusedBodyId = useFocusedBodyId();
  const [showKeyboardShortcuts, setShowKeyboardShortcuts] = useState(false);

  // Get current section name
  const currentSection = focusedBodyId
    ? NAVIGATION_NODES.find(node => node.id === focusedBodyId)?.label
    : null;

  // Toggle keyboard shortcuts with '?' key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '?' || (e.shiftKey && e.key === '/')) {
        e.preventDefault();
        setShowKeyboardShortcuts(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <>
      {/* Main HUD */}
      <div className="navigation-hud" role="status" aria-live="polite">
        {/* Logo and Title */}
        <div className="navigation-hud__branding">
          <img src="/src/assets/images/MM_logo.png" alt="Model Maestro Logo" className="navigation-hud__logo" />
          <h1 className="navigation-hud__brand-title">Model Maestro</h1>
        </div>
      </div>

      {/* Keyboard Shortcuts Modal */}
      {showKeyboardShortcuts && (
        <div className="keyboard-shortcuts">
          <div className="keyboard-shortcuts__backdrop" onClick={() => setShowKeyboardShortcuts(false)} />
          <div className="keyboard-shortcuts__panel">
            <div className="keyboard-shortcuts__header">
              <h3>Keyboard Shortcuts</h3>
              <button
                onClick={() => setShowKeyboardShortcuts(false)}
                className="keyboard-shortcuts__close"
                aria-label="Close shortcuts"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <div className="keyboard-shortcuts__content">
              <div className="keyboard-shortcuts__section">
                <h4>Navigation</h4>
                <div className="keyboard-shortcuts__list">
                  <div className="keyboard-shortcuts__item">
                    <kbd>ESC</kbd>
                    <span>Return to overview</span>
                  </div>
                  <div className="keyboard-shortcuts__item">
                    <kbd>Tab</kbd>
                    <span>Cycle through nodes</span>
                  </div>
                  <div className="keyboard-shortcuts__item">
                    <kbd>Enter</kbd>
                    <span>Select focused node</span>
                  </div>
                  <div className="keyboard-shortcuts__item">
                    <kbd>←</kbd> <kbd>→</kbd>
                    <span>Navigate between nodes</span>
                  </div>
                </div>
              </div>
              <div className="keyboard-shortcuts__section">
                <h4>Quick Access</h4>
                <div className="keyboard-shortcuts__list">
                  <div className="keyboard-shortcuts__item">
                    <kbd>1</kbd>
                    <span>Create Model</span>
                  </div>
                  <div className="keyboard-shortcuts__item">
                    <kbd>2</kbd>
                    <span>Past Models</span>
                  </div>
                  <div className="keyboard-shortcuts__item">
                    <kbd>3</kbd>
                    <span>Information</span>
                  </div>
                </div>
              </div>
              <div className="keyboard-shortcuts__section">
                <h4>Other</h4>
                <div className="keyboard-shortcuts__list">
                  <div className="keyboard-shortcuts__item">
                    <kbd>?</kbd>
                    <span>Toggle this help</span>
                  </div>
                  <div className="keyboard-shortcuts__item">
                    <kbd>Space</kbd>
                    <span>Pause/resume animation</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Screen Reader Announcements */}
      <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
        {isTransitioning && 'Navigating to section'}
        {currentView === 'focused' && currentSection && `Viewing ${currentSection}`}
        {currentView === 'overview' && 'Galaxy overview. Three sections available.'}
      </div>
    </>
  );
}
