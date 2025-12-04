export function Testimonials() {
  const testimonials = [
    {
      quote:
        "Daily Ad Agent cut my ad management time from 3 hours to 10 minutes per day. The AI actually understands what works.",
      author: 'Sarah Chen',
      role: 'E-commerce Founder',
      avatar: 'SC',
    },
    {
      quote:
        "I was skeptical about AI writing ad copy, but the results speak for themselves. 2.8x ROAS in the first month.",
      author: 'Michael Rodriguez',
      role: 'Digital Marketing Manager',
      avatar: 'MR',
    },
    {
      quote:
        "Finally, an ads tool that doesn't require a manual to use. It's like having a media buyer on my team 24/7.",
      author: 'Jessica Park',
      role: 'SaaS Marketing Lead',
      avatar: 'JP',
    },
  ];

  return (
    <section className="py-16 md:py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Loved by marketers worldwide
          </h2>
          <p className="text-base md:text-lg text-gray-600 max-w-2xl mx-auto">
            See what our users have to say about Daily Ad Agent.
          </p>
        </div>

        {/* Testimonials Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100"
            >
              {/* Quote Icon */}
              <div className="text-primary-600 mb-4">
                <svg
                  className="w-7 h-7"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
                </svg>
              </div>

              {/* Quote */}
              <p className="text-sm text-gray-700 leading-relaxed mb-5">
                "{testimonial.quote}"
              </p>

              {/* Author */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-primary-700 font-semibold text-sm">
                  {testimonial.avatar}
                </div>
                <div>
                  <div className="font-semibold text-gray-900 text-sm">
                    {testimonial.author}
                  </div>
                  <div className="text-xs text-gray-600">
                    {testimonial.role}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Trust Badge Row */}
        <div className="mt-12 flex flex-wrap justify-center items-center gap-6 opacity-50">
          <div className="text-gray-400 font-semibold text-xs uppercase tracking-wider">
            Trusted by Leading Brands
          </div>
          {/* Placeholder for brand logos - can add real ones later */}
          <div className="hidden sm:flex gap-6">
            <div className="w-20 h-7 bg-gray-200 rounded"></div>
            <div className="w-20 h-7 bg-gray-200 rounded"></div>
            <div className="w-20 h-7 bg-gray-200 rounded"></div>
            <div className="w-20 h-7 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Testimonials;
