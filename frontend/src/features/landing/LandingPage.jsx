import { Navigation } from '../shared/Navigation';
import { Footer } from '../shared/Footer';
import { Hero } from './Hero';
import { Features } from './Features';
import { HowItWorks } from './HowItWorks';
import { Benefits } from './Benefits';
import { Testimonials } from './Testimonials';
import { CTASection } from './CTASection';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      <Navigation />
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <Benefits />
        <Testimonials />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}

export default LandingPage;
