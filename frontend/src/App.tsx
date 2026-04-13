import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useParams } from 'react-router-dom';
import { scrapeRestaurant, getJobStatus, getRestaurant, analyzeRestaurant } from './api';
import './App.css';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Search, Loader2, AlertCircle, ShieldCheck, TrendingUp, BarChart3, AlertTriangle } from 'lucide-react';

function Home() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState<{message: string, percent: number} | null>(null);
  const navigate = useNavigate();

  const handleScrape = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.includes('google.com/maps')) {
      setError('Please enter a valid Google Maps URL.');
      return;
    }
    
    setLoading(true);
    setError('');
    setProgress({ message: 'Initializing...', percent: 0 });

    try {
      const { job_id } = await scrapeRestaurant(url);
      
      const interval = setInterval(async () => {
        try {
          const job = await getJobStatus(job_id);
          setProgress({ message: job.message || 'Processing...', percent: job.progress });
          
          if (job.status === 'done') {
            clearInterval(interval);
            setLoading(false);
            if (job.restaurant_slug) {
              navigate(`/dashboard/${job.restaurant_slug}`);
            } else {
               setError('Scraping finished but no restaurant found.');
            }
          } else if (job.status === 'failed') {
            clearInterval(interval);
            setLoading(false);
            setError(job.error_message || 'Scraping failed.');
          }
        } catch (err) {
          clearInterval(interval);
          setLoading(false);
          setError('Error checking job status.');
        }
      }, 2000);
    } catch (err: any) {
      setLoading(false);
      setError(err.response?.data?.detail || 'Failed to start scraping.');
    }
  };

  return (
    <div className="home-container">
      <div className="hero-section">
        <h1>VoidRV</h1>
        <p>Analyze the trustworthiness of restaurant reviews using Explainable AI</p>
        
        <form onSubmit={handleScrape} className="search-form">
          <div className="input-wrapper">
            <Search className="search-icon" />
            <input 
              type="text" 
              placeholder="Paste Google Maps Restaurant URL here..." 
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={loading}
            />
            <button type="submit" disabled={loading || !url}>
              {loading ? <Loader2 className="spinner" /> : 'Analyze'}
            </button>
          </div>
        </form>

        {error && <div className="error-message"><AlertCircle size={16}/> {error}</div>}
        
        {loading && progress && (
          <div className="progress-container">
            <div className="progress-bar-bg">
              <div className="progress-bar-fill" style={{ width: `${progress.percent}%` }}></div>
            </div>
            <p>{progress.message} ({progress.percent}%)</p>
          </div>
        )}
      </div>
    </div>
  );
}

function Dashboard() {
  const { slug } = useParams<{slug: string}>();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (slug) {
      loadData(slug);
    }
  }, [slug]);

  const loadData = async (restaurantSlug: string) => {
    try {
      setLoading(true);
      const restaurant = await getRestaurant(restaurantSlug);
      // Ensure we have analyzed data
      if (restaurant && restaurant.id) {
         const analysis = await analyzeRestaurant(restaurant.id);
         setData({ restaurant, analysis });
      }
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
      setLoading(false);
    }
  };

  if (loading) return <div className="loading-screen"><Loader2 className="spinner lg" /> Loading Dashboard...</div>;
  if (error) return <div className="error-screen">{error}</div>;
  if (!data) return <div className="error-screen">No data available.</div>;

  const { restaurant, analysis } = data;
  const reviews = analysis.reviews || [];

  // Metrics
  const totalReviews = reviews.length;
  const trustedReviews = reviews.filter((r: any) => r.trust_score?.badge === 'trusted').length;
  const suspiciousReviews = reviews.filter((r: any) => r.trust_score?.badge === 'suspicious').length;
  const avgTrustScore = (reviews.reduce((acc: number, r: any) => acc + (r.trust_score?.trust_score || 0), 0) / totalReviews).toFixed(1);

  // Charts Data
  const COLORS = ['#10b981', '#f59e0b', '#ef4444'];
  const pieData = [
    { name: 'Trusted', value: trustedReviews },
    { name: 'Caution', value: totalReviews - trustedReviews - suspiciousReviews },
    { name: 'Suspicious', value: suspiciousReviews }
  ];

  const timelineData = [...reviews].sort((a,b) => new Date(a.posted_at).getTime() - new Date(b.posted_at).getTime()).map(r => ({
    date: new Date(r.posted_at).toLocaleDateString(),
    rating: r.star_rating,
    trust: r.trust_score?.trust_score || 0
  }));

  const topTrusted = [...reviews].sort((a,b) => (b.trust_score?.trust_score || 0) - (a.trust_score?.trust_score || 0)).slice(0, 5);

  return (
    <div className="dashboard-container">
       <header className="dashboard-header">
         <h2>{restaurant.name}</h2>
         <p>{restaurant.address}</p>
       </header>

       <div className="metrics-grid">
         <div className="metric-card">
           <BarChart3 className="metric-icon blue" />
           <div className="metric-info">
             <h3>Total Reviews</h3>
             <p>{totalReviews}</p>
           </div>
         </div>
         <div className="metric-card">
           <ShieldCheck className="metric-icon green" />
           <div className="metric-info">
             <h3>Trusted Reviews</h3>
             <p>{trustedReviews} ({((trustedReviews/totalReviews)*100).toFixed(0)}%)</p>
           </div>
         </div>
         <div className="metric-card">
           <AlertTriangle className="metric-icon red" />
           <div className="metric-info">
             <h3>Suspicious Reviews</h3>
             <p>{suspiciousReviews}</p>
           </div>
         </div>
         <div className="metric-card">
           <TrendingUp className="metric-icon purple" />
           <div className="metric-info">
             <h3>Avg Trust Score</h3>
             <p>{avgTrustScore}/100</p>
           </div>
         </div>
       </div>

       <div className="charts-grid">
          <div className="chart-card">
            <h3>Review Archetypes</h3>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={pieData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                    {pieData.map((_entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div className="chart-card span-2">
            <h3>Timeline & Burst Detection</h3>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={timelineData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" domain={[0, 5]} />
                  <YAxis yAxisId="right" orientation="right" domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="rating" stroke="#8884d8" name="Star Rating" />
                  <Line yAxisId="right" type="monotone" dataKey="trust" stroke="#82ca9d" name="Trust Score" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
       </div>

       <div className="reviews-section">
         <h3>Top Trusted Reviews</h3>
         <div className="reviews-list">
           {topTrusted.map((review: any) => (
             <div key={review.id} className="review-card">
               <div className="review-header">
                 <div className="reviewer-info">
                    <strong>{review.reviewer_name}</strong>
                    <span className="stars">{'★'.repeat(review.star_rating)}</span>
                 </div>
                 <div className={`trust-badge ${review.trust_score?.badge}`}>
                    {review.trust_score?.trust_score.toFixed(1)} - {review.trust_score?.badge}
                 </div>
               </div>
               <p className="review-content">{review.content}</p>
               <div className="xai-breakdown">
                  <strong>XAI Breakdown:</strong>
                  <ul>
                    {review.trust_score?.explanation?.map((exp: string, idx: number) => (
                      <li key={idx}>{exp}</li>
                    ))}
                  </ul>
                  <div className="scores-row">
                    <span>Content: {review.trust_score?.content_score.toFixed(1)}</span>
                    <span>Behavior: {review.trust_score?.behavior_score?.toFixed(1) || 'N/A'}</span>
                  </div>
               </div>
             </div>
           ))}
         </div>
       </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <nav className="navbar">
          <div className="logo" onClick={() => window.location.href = '/'}>VoidRV <span className="beta">BETA</span></div>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard/:slug" element={<Dashboard />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
