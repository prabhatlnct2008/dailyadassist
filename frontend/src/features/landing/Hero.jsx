import { Link } from 'react-router-dom';
import { Button } from '../shared/Button';

export function Hero() {
  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section className="relative bg-gradient-to-br from-primary-50 via-white to-primary-50 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - Text Content */}
          <div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
              Your AI Media Buyer for{' '}
              <span className="text-primary-600">Facebook Ads</span>
            </h1>
            <p className="text-lg md:text-xl text-gray-600 mb-8 leading-relaxed">
              Stop wrestling with Ads Manager. Let AI plan, create, and optimize
              your campaigns—daily. Wake up to ready-to-launch ads every morning.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 mb-10">
              <Link to="/login">
                <Button variant="primary" size="lg" className="w-full sm:w-auto">
                  Start Free
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
              <Button
                variant="outline"
                size="lg"
                className="w-full sm:w-auto"
                onClick={() => scrollToSection('how-it-works')}
              >
                See How It Works
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <svg
                  className="w-4 h-4 text-green-600"
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
              <div className="flex items-center gap-2">
                <svg
                  className="w-4 h-4 text-green-600"
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
            </div>
          </div>

          {/* Right Column - Visual */}
          <div className="relative lg:pl-8">
            <div className="relative rounded-xl shadow-2xl overflow-hidden border border-gray-200 bg-white">
              {/* Mock War Room Interface Screenshot */}
              <div className="p-4 space-y-3">
                {/* Mock Chat Interface */}
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-start gap-2 mb-2">
                    <div className="w-7 h-7 bg-primary-600 rounded-full flex items-center justify-center flex-shrink-0">
                      <svg
                        className="w-4 h-4 text-white"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13 10V3L4 14h7v7l9-11h-7z"
                        />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <p className="text-xs text-gray-700 leading-relaxed">
                        Good morning! Yesterday's campaign achieved 3.2x ROAS.
                        Ready to create today's ad?
                      </p>
                    </div>
                  </div>
                </div>

                {/* Mock Ad Preview */}
                <div className="bg-white border border-gray-200 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
                    <div>
                      <div className="h-2 w-20 bg-gray-300 rounded"></div>
                      <div className="h-1.5 w-14 bg-gray-200 rounded mt-1"></div>
                    </div>
                  </div>
                  <div className="h-24 bg-gradient-to-br from-primary-100 to-primary-200 rounded mb-2"></div>
                  <div className="space-y-1.5">
                    <div className="h-2 bg-gray-200 rounded w-full"></div>
                    <div className="h-2 bg-gray-200 rounded w-4/5"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Floating Stats Badge */}
            <div className="absolute -bottom-4 -left-4 bg-white rounded-lg shadow-xl p-3 border border-gray-100">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-5 h-5 text-green-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                    />
                  </svg>
                </div>
                <div>
                  <p className="text-xl font-bold text-gray-900">3.2x</p>
                  <p className="text-xs text-gray-600">Avg. ROAS</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Hero;
