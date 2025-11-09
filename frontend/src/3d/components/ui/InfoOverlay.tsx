import './InfoOverlay.css';

/**
 * InfoOverlay Component
 * 
 * Displays platform information and documentation.
 * Reuses content from old InfoPage component.
 * 
 * Requirements: 14.4
 */

export interface InfoOverlayProps {
  visible: boolean;
}

export function InfoOverlay({ visible }: InfoOverlayProps) {
  if (!visible) {
    return null;
  }

  return (
    <div className="info-overlay">
      <div className="info-overlay__header">
        <h2 id="overlay-title" className="info-overlay__title">
          About the Platform
        </h2>
        <p className="info-overlay__subtitle">
          AI-powered machine learning made accessible to everyone
        </p>
      </div>

      {/* Platform Description */}
      <section className="info-overlay__section">
        <h3 className="info-overlay__section-title">What is this?</h3>
        <p className="info-overlay__text">
          An AI-powered platform that automatically trains machine learning models from your data. 
          Just upload your dataset and describe what you want to learn - our intelligent agent 
          handles everything from data analysis to model selection and training.
        </p>
        <p className="info-overlay__text">
          Built with Google Cloud Vertex AI and powered by advanced AI reasoning, this platform 
          makes machine learning accessible to everyone, regardless of technical expertise.
        </p>
      </section>

      {/* Usage Instructions */}
      <section className="info-overlay__section">
        <h3 className="info-overlay__section-title">How to Use</h3>
        <div className="info-overlay__steps">
          <div className="info-overlay__step">
            <div className="info-overlay__step-number">1</div>
            <div className="info-overlay__step-content">
              <h4>Upload your dataset</h4>
              <p>Supports CSV, JSON, and Excel formats. Simply drag and drop or click to browse.</p>
            </div>
          </div>
          <div className="info-overlay__step">
            <div className="info-overlay__step-number">2</div>
            <div className="info-overlay__step-content">
              <h4>Describe what you want the model to predict</h4>
              <p>Use natural language to explain your goal. For example: "Predict customer churn" or "Classify product categories".</p>
            </div>
          </div>
          <div className="info-overlay__step">
            <div className="info-overlay__step-number">3</div>
            <div className="info-overlay__step-content">
              <h4>Click 'Start Training' and watch the magic happen</h4>
              <p>Our AI agent analyzes your data, selects the best model, and trains it automatically. Track progress in real-time.</p>
            </div>
          </div>
          <div className="info-overlay__step">
            <div className="info-overlay__step-number">4</div>
            <div className="info-overlay__step-content">
              <h4>Review results and download your trained model</h4>
              <p>Get detailed performance metrics, visualizations, and a ready-to-use model for predictions.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="info-overlay__section">
        <h3 className="info-overlay__section-title">Key Features</h3>
        <div className="info-overlay__features">
          <div className="info-overlay__feature">
            <div className="info-overlay__feature-icon" style={{ color: '#4285F4' }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
            </div>
            <h4>Automatic Model Selection</h4>
            <p>AI agent analyzes your data and selects the optimal algorithm</p>
          </div>
          <div className="info-overlay__feature">
            <div className="info-overlay__feature-icon" style={{ color: '#FBBC04' }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
            </div>
            <h4>Fast Training</h4>
            <p>Powered by Google Cloud Vertex AI for rapid model training</p>
          </div>
          <div className="info-overlay__feature">
            <div className="info-overlay__feature-icon" style={{ color: '#EA4335' }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
            </div>
            <h4>AI-Powered Reasoning</h4>
            <p>Intelligent decision-making at every step of the pipeline</p>
          </div>
          <div className="info-overlay__feature">
            <div className="info-overlay__feature-icon" style={{ color: '#34A853' }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
            </div>
            <h4>Automatic Data Processing</h4>
            <p>Handles cleaning, feature engineering, and preprocessing</p>
          </div>
          <div className="info-overlay__feature">
            <div className="info-overlay__feature-icon" style={{ color: '#4285F4' }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="20" x2="18" y2="10" />
                <line x1="12" y1="20" x2="12" y2="4" />
                <line x1="6" y1="20" x2="6" y2="14" />
              </svg>
            </div>
            <h4>Detailed Analytics</h4>
            <p>Comprehensive metrics and visualizations for model performance</p>
          </div>
          <div className="info-overlay__feature">
            <div className="info-overlay__feature-icon" style={{ color: '#FBBC04' }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
                <polyline points="17 6 23 6 23 12" />
              </svg>
            </div>
            <h4>Production Ready</h4>
            <p>Deploy models directly to Vertex AI endpoints for predictions</p>
          </div>
        </div>
      </section>

      {/* Use Case Examples */}
      <section className="info-overlay__section">
        <h3 className="info-overlay__section-title">Use Case Examples</h3>
        <div className="info-overlay__use-cases">
          <div className="info-overlay__use-case">
            <h4 style={{ color: '#4285F4' }}>Customer Churn Prediction</h4>
            <p>
              Upload customer data with features like usage patterns, demographics, and support tickets. 
              The platform identifies customers likely to churn and provides insights into key factors.
            </p>
            <div className="info-overlay__use-case-tags">
              <span>Classification</span>
              <span>Feature Importance</span>
              <span>Actionable Insights</span>
            </div>
          </div>
          <div className="info-overlay__use-case">
            <h4 style={{ color: '#34A853' }}>Sales Forecasting</h4>
            <p>
              Predict future sales based on historical data, seasonality, and market trends. 
              Get accurate forecasts to optimize inventory and resource planning.
            </p>
            <div className="info-overlay__use-case-tags">
              <span>Regression</span>
              <span>Time Series</span>
              <span>Trend Analysis</span>
            </div>
          </div>
          <div className="info-overlay__use-case">
            <h4 style={{ color: '#FBBC04' }}>Product Categorization</h4>
            <p>
              Automatically classify products into categories based on descriptions, attributes, and images. 
              Perfect for e-commerce catalog management and organization.
            </p>
            <div className="info-overlay__use-case-tags">
              <span>Multi-class Classification</span>
              <span>Text Analysis</span>
              <span>Automated Tagging</span>
            </div>
          </div>
          <div className="info-overlay__use-case">
            <h4 style={{ color: '#EA4335' }}>Fraud Detection</h4>
            <p>
              Identify fraudulent transactions or activities by analyzing patterns in transaction data. 
              Protect your business with real-time anomaly detection.
            </p>
            <div className="info-overlay__use-case-tags">
              <span>Anomaly Detection</span>
              <span>Binary Classification</span>
              <span>Risk Scoring</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
