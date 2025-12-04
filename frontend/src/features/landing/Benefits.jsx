export function Benefits() {
  const benefits = [
    {
      problem: 'Tired of Ads Manager complexity?',
      solution: 'One-screen approval',
      description:
        'No more tabs, dropdowns, or cryptic settings. See everything you need in one conversational interface.',
      icon: (
        <svg
          className="w-5 h-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      ),
    },
    {
      problem: 'Wasting hours on copywriting?',
      solution: 'AI generates variants instantly',
      description:
        'Get multiple headline and copy variations in seconds. Pick the best, edit if needed, or let AI decide.',
      icon: (
        <svg
          className="w-5 h-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
          />
        </svg>
      ),
    },
    {
      problem: 'Guessing what works?',
      solution: 'Data-driven recommendations daily',
      description:
        'Start every day with performance insights and specific actions. Know exactly what to double down on.',
      icon: (
        <svg
          className="w-5 h-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
      ),
    },
    {
      problem: 'Losing sleep over budgets?',
      solution: 'Automatic safety guardrails',
      description:
        'Set daily limits and policy checks. Never accidentally overspend or violate Facebook policies.',
      icon: (
        <svg
          className="w-5 h-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
          />
        </svg>
      ),
    },
  ];

  return (
    <section className="py-16 md:py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Stop fighting with Ads Manager
          </h2>
          <p className="text-base md:text-lg text-gray-600 max-w-2xl mx-auto">
            We built Daily Ad Agent to solve the real problems marketers face
            every day.
          </p>
        </div>

        {/* Benefits Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {benefits.map((benefit, index) => (
            <div
              key={index}
              className="relative p-6 rounded-xl bg-gradient-to-br from-gray-50 to-white border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all duration-200"
            >
              {/* Icon */}
              <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center text-primary-600 mb-4">
                {benefit.icon}
              </div>

              {/* Problem */}
              <div className="mb-3">
                <div className="inline-block px-2 py-0.5 bg-red-100 text-red-700 text-xs font-medium rounded mb-2">
                  Problem
                </div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {benefit.problem}
                </h3>
              </div>

              {/* Solution */}
              <div className="mb-3">
                <div className="inline-block px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded mb-2">
                  Solution
                </div>
                <h4 className="text-base font-semibold text-primary-600">
                  {benefit.solution}
                </h4>
              </div>

              {/* Description */}
              <p className="text-sm text-gray-600 leading-relaxed">
                {benefit.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Benefits;
