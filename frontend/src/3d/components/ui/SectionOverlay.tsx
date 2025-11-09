import React, { useEffect, useState } from 'react';
import { useFocusedBodyId, useCurrentView } from '../../store/navigationStore';
import './SectionOverlay.css';

/**
 * SectionOverlay Component
 * 
 * Context-sensitive UI overlay that appears when focusing on a celestial body.
 * Positioned in screen space using HTML/CSS with smooth animations.
 * 
 * Requirements: 2.4, 2.5
 */

export interface SectionOverlayProps {
  children?: React.ReactNode;
  onClose?: () => void;
}

export function SectionOverlay({ children, onClose }: SectionOverlayProps) {
  const focusedBodyId = useFocusedBodyId();
  const currentView = useCurrentView();
  
  const [isVisible, setIsVisible] = useState(false);
  const [isAnimatingOut, setIsAnimatingOut] = useState(false);

  // Show overlay when focused on a body
  useEffect(() => {
    if (currentView === 'focused' && focusedBodyId) {
      // Small delay to ensure camera has started moving
      const timer = setTimeout(() => {
        setIsVisible(true);
        setIsAnimatingOut(false);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      // Trigger exit animation
      if (isVisible) {
        setIsAnimatingOut(true);
        const timer = setTimeout(() => {
          setIsVisible(false);
          setIsAnimatingOut(false);
        }, 300); // Match exit animation duration
        return () => clearTimeout(timer);
      }
    }
  }, [currentView, focusedBodyId, isVisible]);

  // Handle ESC key to close overlay
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isVisible && !isAnimatingOut && onClose) {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isVisible, isAnimatingOut, onClose]);

  const handleClose = () => {
    if (onClose) {
      onClose();
    }
  };

  if (!isVisible && !isAnimatingOut) {
    return null;
  }

  return (
    <div 
      className={`section-overlay ${isAnimatingOut ? 'exiting' : 'entering'}`}
      role="dialog"
      aria-modal="true"
      aria-labelledby="overlay-title"
    >
      {/* Backdrop */}
      <div 
        className="section-overlay__backdrop"
        onClick={handleClose}
        aria-label="Close overlay"
      />
      
      {/* Content Container */}
      <div className="section-overlay__container">
        {/* Close Button */}
        <button
          className="section-overlay__close"
          onClick={handleClose}
          aria-label="Close overlay (ESC)"
          title="Close (ESC)"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        {/* Content */}
        <div className="section-overlay__content">
          {children}
        </div>
      </div>
    </div>
  );
}
