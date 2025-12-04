import { Link } from 'react-router-dom';
import { Button } from '../shared/Button';

export function CTASection() {
  return (
    <section className="py-16 md:py-20 bg-gradient-to-br from-primary-600 to-primary-700">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Headline */}
        <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-5">
          Ready to let AI handle your ads?
        </h2>

        {/* Subheadline */}
        <p className="text-base md:text-lg text-primary-100 mb-8 max-w-2xl mx-auto">
          Join marketers who wake up to ready-to-launch campaigns every morning.
          No dashboards, no complexity—just results.
        </p>

        {/* CTA Button */}
        <Link to="/login">
          <Button
            size="lg"
            className="bg-white text-primary-600 hover:bg-gray-50 shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-200"
          >
            Get Started Free
            <svg
              className="w-4 h-4 ml-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7l5 5m0 0l-5 5m5-5H6"
              />
            </svg>
          </Button>
        </Link>

        {/* Trust Indicators */}
        <div className="mt-6 flex flex-wrap items-center justify-center gap-4 text-sm text-primary-100">
          <div className="flex items-center gap-1.5">
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span>No credit card required</span>
          </div>
          <div className="flex items-center gap-1.5">
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span>2-minute setup</span>
          </div>
          <div className="flex items-center gap-1.5">
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span>Cancel anytime</span>
          </div>
        </div>

        {/* Stats Row */}
        <div className="mt-10 grid grid-cols-3 gap-6 max-w-2xl mx-auto">
          <div>
            <div className="text-3xl md:text-4xl font-bold text-white mb-1">
              3.2x
            </div>
            <div className="text-xs text-primary-100">Avg. ROAS</div>
          </div>
          <div>
            <div className="text-3xl md:text-4xl font-bold text-white mb-1">
              5 min
            </div>
            <div className="text-xs text-primary-100">Daily time spent</div>
          </div>
          <div>
            <div className="text-3xl md:text-4xl font-bold text-white mb-1">
              100%
            </div>
            <div className="text-xs text-primary-100">Automated</div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default CTASection;
