export function HowItWorks() {
  const steps = [
    {
      number: '01',
      title: 'Connect',
      description:
        'Link your Google account and Facebook Ad Account. Takes less than 2 minutes.',
      icon: (
        <svg
          className="w-6 h-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
          />
        </svg>
      ),
    },
    {
      number: '02',
      title: 'Converse',
      description:
        'Chat with the AI about your campaign goals, budget, and target audience. Natural conversation, no jargon.',
      icon: (
        <svg
          className="w-6 h-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"
          />
        </svg>
      ),
    },
    {
      number: '03',
      title: 'Launch',
      description:
        'Review the AI-generated ad with live preview, make edits if needed, and approve. Published directly to Facebook.',
      icon: (
        <svg
          className="w-6 h-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
          />
        </svg>
      ),
    },
  ];

  return (
    <section
      id="how-it-works"
      className="py-16 md:py-20 bg-gradient-to-br from-primary-50 to-white"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            How It Works
          </h2>
          <p className="text-base md:text-lg text-gray-600 max-w-2xl mx-auto">
            From setup to launch in three simple steps. No training required.
          </p>
        </div>

        {/* Steps */}
        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              {/* Connector Line (desktop only) */}
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-12 left-1/2 w-full h-0.5 bg-gradient-to-r from-primary-200 to-primary-300 z-0"></div>
              )}

              {/* Step Card */}
              <div className="relative z-10 text-center">
                {/* Icon Circle */}
                <div className="w-24 h-24 mx-auto mb-5 bg-white rounded-full shadow-lg flex items-center justify-center border-2 border-primary-100">
                  <div className="text-primary-600">{step.icon}</div>
                </div>

                {/* Step Number */}
                <div className="inline-block px-3 py-1 bg-primary-100 text-primary-700 font-semibold rounded-full text-sm mb-3">
                  Step {step.number}
                </div>

                {/* Title */}
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  {step.title}
                </h3>

                {/* Description */}
                <p className="text-sm text-gray-600 leading-relaxed">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-12">
          <p className="text-gray-700 mb-3 font-medium">
            Ready to get started?
          </p>
          <a
            href="/login"
            className="inline-flex items-center text-primary-600 hover:text-primary-700 font-semibold group"
          >
            Sign up now
            <svg
              className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform"
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
          </a>
        </div>
      </div>
    </section>
  );
}

export default HowItWorks;
