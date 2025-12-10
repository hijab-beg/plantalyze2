import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { toast } from "sonner";
import { Leaf, Upload, LogOut, Loader2, AlertTriangle, CheckCircle2, X, ImageIcon } from "lucide-react";
import { User } from "@supabase/supabase-js";
interface AnalysisResult {
  isLeaf: boolean;
  segmentationMask?: string;
  maskStats?: {
    backgroundPercent: number;
    healthyPercent: number;
    diseasedPercent: number;
  };
  disease?: string | null;
  confidence?: number;
  description?: string;
}
const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  useEffect(() => {
    const {
      data: {
        subscription
      }
    } = supabase.auth.onAuthStateChange((event, session) => {
      setUser(session?.user ?? null);
      setIsLoading(false);
      if (!session?.user) {
        navigate("/auth");
      }
    });
    supabase.auth.getSession().then(({
      data: {
        session
      }
    }) => {
      setUser(session?.user ?? null);
      setIsLoading(false);
      if (!session?.user) {
        navigate("/auth");
      }
    });
    return () => subscription.unsubscribe();
  }, [navigate]);
  const handleSignOut = async () => {
    await supabase.auth.signOut();
    toast.success("Signed out successfully");
    navigate("/");
  };
  const validateFile = (file: File): boolean => {
    const validTypes = ["image/jpeg", "image/png", "image/jpg"];
    if (!validTypes.includes(file.type)) {
      toast.error("Please upload a JPG or PNG image");
      return false;
    }
    if (file.size > 10 * 1024 * 1024) {
      toast.error("Image must be less than 10MB");
      return false;
    }
    return true;
  };
  const handleFileSelect = (file: File) => {
    if (!validateFile(file)) return;
    setSelectedFile(file);
    setResult(null);
    const reader = new FileReader();
    reader.onload = e => {
      setPreviewUrl(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  }, []);
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };
  const analyzeImage = async () => {
    if (!selectedFile || !previewUrl) return;
    setIsAnalyzing(true);
    try {
      const base64Data = previewUrl.split(",")[1];
      
      // Call Python Flask backend directly
      const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";
      
      const response = await fetch(`${BACKEND_URL}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image: base64Data,
          mimeType: selectedFile.type
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: "Unknown error" }));
        throw new Error(errorData.error || `Server error: ${response.status}`);
      }

      const data = await response.json();
      
      setResult(data);
      if (!data.isLeaf) {
        toast.error("No leaf detected in the image. Please upload a clear photo of a plant leaf.");
      } else {
        toast.success("Segmentation complete! Check the mask output.");
      }
    } catch (error: any) {
      console.error("Analysis error:", error);
      if (error.message?.includes("Failed to fetch")) {
        toast.error("Cannot connect to backend. Make sure the Python server is running on http://localhost:5000");
      } else {
        toast.error(error.message || "Failed to analyze image. Please try again.");
      }
    } finally {
      setIsAnalyzing(false);
    }
  };
  const resetUpload = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
  };
  if (isLoading) {
    return <div className="min-h-screen gradient-hero flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>;
  }
  return <div className="min-h-screen gradient-hero">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl gradient-leaf flex items-center justify-center">
              <Leaf className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-display font-semibold text-foreground">Plantalyze</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground hidden sm:block">
              {user?.email}
            </span>
            <Button variant="ghost" size="sm" onClick={handleSignOut}>
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12 max-w-4xl">
        <div className="text-center mb-10 animate-fade-in">
          <h1 className="text-3xl md:text-4xl font-display font-bold mb-3">
            Analyze Your Plant
          </h1>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Upload a clear photo of a leaf to detect diseases.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Upload Card */}
          <Card className="shadow-elevated animate-fade-in" style={{
          animationDelay: "100ms"
        }}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="w-5 h-5 text-primary" />
                Upload Image
              </CardTitle>
              <CardDescription>
                Supported formats: JPG, PNG (max 10MB)
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!previewUrl ? <label onDrop={handleDrop} onDragOver={handleDragOver} onDragLeave={handleDragLeave} className={`
                    relative flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-300
                    ${isDragging ? "border-primary bg-leaf-50" : "border-border hover:border-primary/50 hover:bg-leaf-50/50"}
                  `}>
                  <input type="file" accept="image/jpeg,image/png,image/jpg" onChange={handleInputChange} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
                  <div className="w-16 h-16 rounded-full bg-leaf-100 flex items-center justify-center mb-4">
                    <ImageIcon className="w-8 h-8 text-leaf-600" />
                  </div>
                  <p className="font-medium mb-1">Drop your image here</p>
                  <p className="text-sm text-muted-foreground">or click to browse</p>
                </label> : <div className="space-y-4">
                  <div className="relative rounded-xl overflow-hidden bg-muted aspect-square">
                    <img src={previewUrl} alt="Selected leaf" className="w-full h-full object-contain" />
                    <button onClick={resetUpload} className="absolute top-2 right-2 w-8 h-8 rounded-full bg-background/80 backdrop-blur-sm flex items-center justify-center hover:bg-background transition-colors">
                      <X className="w-4 h-4" />
                    </button>
                    {isAnalyzing && <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex flex-col items-center justify-center">
                        <div className="relative w-24 h-24">
                          <div className="absolute inset-0 rounded-full border-4 border-leaf-200" />
                          <div className="absolute inset-0 rounded-full border-4 border-primary border-t-transparent animate-spin" />
                        </div>
                        <p className="mt-4 font-medium text-foreground">Analyzing...</p>
                        <p className="text-sm text-muted-foreground">Processing your image</p>
                      </div>}
                  </div>
                  
                  <Button variant="hero" size="lg" className="w-full" onClick={analyzeImage} disabled={isAnalyzing}>
                    {isAnalyzing ? <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Analyzing...
                      </> : "Analyze Leaf"}
                  </Button>
                </div>}
            </CardContent>
          </Card>

          {/* Results Card */}
          <Card className="shadow-elevated animate-fade-in" style={{
          animationDelay: "200ms"
        }}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Leaf className="w-5 h-5 text-primary" />
                Segmentation Results
              </CardTitle>
              <CardDescription>
                {result ? result.isLeaf ? "Segmentation mask shows background (black), healthy tissue (grey), and diseased areas (white)" : "Invalid image" : "Results will appear here after analysis"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!result ? <div className="h-64 flex flex-col items-center justify-center text-muted-foreground">
                  <Leaf className="w-12 h-12 mb-4 opacity-30" />
                  <p className="text-center">
                    Upload and analyze a leaf image to see results
                  </p>
                </div> : !result.isLeaf ? <div className="p-6 rounded-xl bg-destructive/10 border border-destructive/20">
                  <div className="flex items-start gap-4">
                    <AlertTriangle className="w-6 h-6 text-destructive flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-destructive mb-2">No Leaf Detected</h4>
                      <p className="text-sm text-muted-foreground">
                        The uploaded image doesn't appear to contain a plant leaf. 
                        Please upload a clear, well-lit photo of a single leaf for accurate analysis.
                      </p>
                    </div>
                  </div>
                </div> : <div className="space-y-6">
                  {/* Segmentation Mask */}
                  {result.segmentationMask && (
                    <div>
                      <h4 className="font-semibold mb-3">Segmentation Mask</h4>
                      <img 
                        src={result.segmentationMask} 
                        alt="Segmentation Mask" 
                        className="w-full rounded-lg border border-border"
                      />
                    </div>
                  )}

                  {/* Mask Statistics */}
                  {result.maskStats && (
                    <div>
                      <h4 className="font-semibold mb-3">Pixel Distribution</h4>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-muted-foreground">Background (Black)</span>
                            <span className="font-medium">{result.maskStats.backgroundPercent.toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-muted rounded-full h-2">
                            <div 
                              className="bg-gray-900 h-2 rounded-full transition-all" 
                              style={{ width: `${result.maskStats.backgroundPercent}%` }}
                            />
                          </div>
                        </div>
                        
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-muted-foreground">Healthy Tissue (Grey)</span>
                            <span className="font-medium">{result.maskStats.healthyPercent.toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-muted rounded-full h-2">
                            <div 
                              className="bg-green-500 h-2 rounded-full transition-all" 
                              style={{ width: `${result.maskStats.healthyPercent}%` }}
                            />
                          </div>
                        </div>
                        
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-muted-foreground">Diseased Areas (White)</span>
                            <span className="font-medium">{result.maskStats.diseasedPercent.toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-muted rounded-full h-2">
                            <div 
                              className="bg-red-500 h-2 rounded-full transition-all" 
                              style={{ width: `${result.maskStats.diseasedPercent}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                </div>}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>;
};
export default Dashboard;