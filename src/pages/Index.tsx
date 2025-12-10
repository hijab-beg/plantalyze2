import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Leaf, Shield, Zap, ArrowRight, Scan } from "lucide-react";
const Index = () => {
  return <div className="min-h-screen gradient-hero">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl gradient-leaf flex items-center justify-center">
              <Leaf className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-display font-semibold text-foreground">Plantalyze</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link to="/auth">
              <Button variant="ghost" size="sm">
                Sign In
              </Button>
            </Link>
            <Link to="/auth?mode=signup">
              <Button variant="hero" size="sm">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center space-y-8 animate-fade-in-up">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-leaf-100 text-leaf-700 text-sm font-medium">
              <Scan className="w-4 h-4" />
              AI-Powered Plant Health Analysis
            </div>
            
            <h1 className="text-5xl md:text-7xl font-display font-bold text-foreground leading-tight">
              Detect Plant Diseases
              <br />
              <span className="text-gradient-leaf">Instantly</span>
            </h1>
            
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">Upload a photo of your plant's leaf and our advanced AI will identify diseases, and help you keep your plants healthy.</p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              <Link to="/auth?mode=signup">
                <Button variant="hero" size="xl" className="w-full sm:w-auto">
                  Start Scanning
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </Link>
              <Link to="/auth">
                <Button variant="outline" size="xl" className="w-full sm:w-auto">
                  Sign In
                </Button>
              </Link>
            </div>
          </div>

          {/* Feature Cards */}
          <div className="mt-24 grid md:grid-cols-3 gap-6">
            <FeatureCard icon={<Scan className="w-6 h-6" />} title="Instant Detection" description="Upload a leaf image and get results in seconds with our advanced AI model." delay="0ms" />
            <FeatureCard icon={<Shield className="w-6 h-6" />} title="Accurate Results" description="Powered by state-of-the-art machine learning for reliable disease identification." delay="100ms" />
            <FeatureCard icon={<Zap className="w-6 h-6" />} title="Treatment Tips" description="Get actionable recommendations to treat and prevent plant diseases." delay="200ms" />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-6 bg-card/50">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-3xl md:text-4xl font-display font-bold text-center mb-16">
            How It Works
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Step number="1" title="Upload" description="Take a clear photo of the affected leaf" />
            <Step number="2" title="Analyze" description="Our AI processes and segments the image" />
            <Step number="3" title="Results" description="Get disease diagnosis" />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-border">
        <div className="container mx-auto max-w-5xl flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <Leaf className="w-5 h-5 text-primary" />
            <span className="font-display font-semibold">Plantalyze</span>
          </div>
          <p className="text-sm text-muted-foreground">© 2025 Plantalyze. Helping plants thrive.</p>
        </div>
      </footer>
    </div>;
};
const FeatureCard = ({
  icon,
  title,
  description,
  delay
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  delay: string;
}) => <div className="p-6 rounded-2xl bg-card border border-border shadow-soft hover:shadow-elevated transition-all duration-300 hover:-translate-y-1 animate-fade-in" style={{
  animationDelay: delay
}}>
    <div className="w-12 h-12 rounded-xl bg-leaf-100 flex items-center justify-center text-leaf-600 mb-4">
      {icon}
    </div>
    <h3 className="text-lg font-display font-semibold mb-2">{title}</h3>
    <p className="text-muted-foreground">{description}</p>
  </div>;
const Step = ({
  number,
  title,
  description
}: {
  number: string;
  title: string;
  description: string;
}) => <div className="text-center">
    <div className="w-16 h-16 rounded-full gradient-leaf flex items-center justify-center text-primary-foreground text-2xl font-display font-bold mx-auto mb-4">
      {number}
    </div>
    <h3 className="text-xl font-display font-semibold mb-2">{title}</h3>
    <p className="text-muted-foreground">{description}</p>
  </div>;
export default Index;