import { useState, useEffect } from 'react';
import {
  Search, MapPin, Upload, FileText, Sparkles, Download,
  Briefcase, User, Building2, Globe, Ghost,
  CheckCircle, ChevronRight, Bell, Settings,
  LayoutGrid, Bookmark
} from 'lucide-react';

const API_BASE = "http://localhost:8000";

// Get greeting based on local time
const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour >= 5 && hour < 12) return "Good Morning";
  if (hour >= 12 && hour < 17) return "Good Afternoon";
  return "Good Evening";
};

function App() {
  const [jobs, setJobs] = useState([]);
  const [query, setQuery] = useState("");
  const [location, setLocation] = useState("Bangalore, India");
  const [loading, setLoading] = useState(false);
  const [resumeId, setResumeId] = useState(null);
  const [resumeData, setResumeData] = useState(null);
  const [atsScores, setAtsScores] = useState({});
  const [tailoredResumes, setTailoredResumes] = useState({});
  const [activeTab, setActiveTab] = useState('jobs');

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      const resp = await fetch(`${API_BASE}/resumes/upload`, { method: "POST", body: formData });
      if (resp.ok) {
        const data = await resp.json();
        setResumeId(data.resume_id);
        try {
          const analyzeResp = await fetch(`${API_BASE}/resumes/analyze?resume_id=${data.resume_id}`, { method: "POST" });
          if (analyzeResp.ok) {
            const analyzed = await analyzeResp.json();
            setResumeData(analyzed.parsed_data);
          }
        } catch (err) { console.error("Analysis error:", err); }
      } else { alert("Upload failed"); }
    } catch (err) { alert("Network error"); }
  };

  const calculateATS = async (jobId) => {
    if (!resumeId) { alert("⚠️ Please upload a resume first!"); return; }
    setAtsScores(prev => ({ ...prev, [jobId]: { loading: true } }));
    try {
      const resp = await fetch(`${API_BASE}/jobs/${jobId}/ats-score?resume_id=${resumeId}`, { method: "POST" });
      if (resp.ok) {
        const data = await resp.json();
        setAtsScores(prev => ({ ...prev, [jobId]: data }));
      } else { setAtsScores(prev => ({ ...prev, [jobId]: { error: true } })); }
    } catch (err) { setAtsScores(prev => ({ ...prev, [jobId]: { error: true } })); }
  };

  const tailorResume = async (jobId) => {
    if (!resumeId) return;
    setTailoredResumes(prev => ({ ...prev, [jobId]: { loading: true } }));
    try {
      const resp = await fetch(`${API_BASE}/jobs/${jobId}/tailor-resume?resume_id=${resumeId}`, { method: "POST" });
      if (resp.ok) {
        const data = await resp.json();
        setTailoredResumes(prev => ({ ...prev, [jobId]: data }));
        setAtsScores(prev => ({ ...prev, [jobId]: { ...prev[jobId], ats_score: data.new_ats_score, improved: true } }));
      } else { setTailoredResumes(prev => ({ ...prev, [jobId]: { error: true } })); }
    } catch (err) { setTailoredResumes(prev => ({ ...prev, [jobId]: { error: true } })); }
  };

  const downloadResume = async (resumeId, filename) => {
    try {
      const response = await fetch(`${API_BASE}/resumes/${resumeId}/download`);
      if (!response.ok) throw new Error("Download failed");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename.replace('.md', '.docx');
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) { alert("❌ Failed to download resume"); }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setJobs([]);
    try {
      const resp = await fetch(`${API_BASE}/jobs/scrape?search_term=${encodeURIComponent(query)}&location=${encodeURIComponent(location)}&results_wanted=10`, { method: "POST" });
      if (resp.ok) {
        const data = await resp.json();
        setJobs(data.jobs || []);
      }
    } catch (err) { console.error("Search error:", err); } finally { setLoading(false); }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-black text-white font-sans selection:bg-blue-500/30">

      {/* iOS Sidebar / Dock */}
      <aside className="w-24 lg:w-64 h-full p-4 flex flex-col gap-4 z-20 hidden md:flex">
        <div className="h-full ios-card flex flex-col p-4">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-8 px-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Sparkles className="text-white w-6 h-6" />
            </div>
            <span className="text-xl font-bold tracking-tight hidden lg:block">JobHunter</span>
          </div>

          {/* Nav */}
          <nav className="space-y-2 flex-1">
            {[
              { id: 'jobs', icon: LayoutGrid, label: 'Dashboard' },
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all duration-200 ${activeTab === item.id
                  ? 'bg-white/10 text-white font-semibold'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
                  }`}
              >
                <item.icon className="w-6 h-6" />
                <span className="hidden lg:block">{item.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 h-full overflow-y-auto p-4 lg:p-6 relative">
        {/* Top Bar */}
        <div className="flex justify-between items-center mb-8 animate-slide-up">
          <div>
            <h1 className="text-3xl font-bold text-sf-display">{getGreeting()}</h1>
            <p className="text-gray-400">Ready to find your next opportunity?</p>
          </div>
          <button className="w-10 h-10 rounded-full ios-glass flex items-center justify-center hover:bg-white/10 transition active:scale-95">
            <Bell className="w-5 h-5 text-white" />
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          {/* Center Column - Search & Feed */}
          <div className="lg:col-span-8 space-y-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>

            {/* iOS Search Widget */}
            <div className="ios-card p-1.5 flex items-center gap-2">
              <div className="flex-1 relative h-12 bg-white/5 rounded-xl flex items-center px-4 transition-all focus-within:bg-white/10 focus-within:ring-2 focus-within:ring-blue-500/50">
                <Search className="w-5 h-5 text-gray-400 mr-3" />
                <input
                  type="text"
                  placeholder="Search for jobs (e.g. iOS Developer)..."
                  className="bg-transparent border-none outline-none text-white w-full placeholder-gray-500 h-full"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
              <div className="w-px h-8 bg-white/10"></div>
              <div className="relative h-12 bg-white/5 rounded-xl flex items-center px-4 w-1/3 transition-all focus-within:bg-white/10">
                <MapPin className="w-5 h-5 text-gray-400 mr-3" />
                <input
                  type="text"
                  placeholder="Location"
                  className="bg-transparent border-none outline-none text-white w-full placeholder-gray-500 h-full"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
              <button
                onClick={handleSearch}
                disabled={loading}
                className="h-12 px-6 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold transition active:scale-95 flex items-center gap-2 shadow-lg shadow-blue-600/20"
              >
                {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : "Search"}
              </button>
            </div>

            {/* Job Feed */}
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-sf-display flex items-center gap-2">
                Recommended Jobs <span className="text-sm font-normal text-gray-500 bg-white/10 px-2 py-0.5 rounded-full">{jobs.length}</span>
              </h2>

              {jobs.length === 0 && !loading ? (
                <div className="ios-card p-12 text-center flex flex-col items-center justify-center min-h-[300px]">
                  <div className="w-24 h-24 rounded-full bg-white/5 flex items-center justify-center mb-4">
                    <Search className="w-10 h-10 text-gray-600" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-300">No Jobs Found</h3>
                  <p className="text-gray-500 mt-2 max-w-xs">Try searching for "iOS Developer" in "San Francisco" to see results.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-4">
                  {jobs.map((job, idx) => <JobCard key={idx} job={job} atsScores={atsScores} tailoredResumes={tailoredResumes} calculateATS={calculateATS} tailorResume={tailorResume} downloadResume={downloadResume} />)}
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Widgets */}
          <div className="lg:col-span-4 space-y-6 animate-slide-up" style={{ animationDelay: '0.2s' }}>

            {/* Profile Widget */}
            <div className="ios-card p-6 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/20 blur-3xl rounded-full -mr-10 -mt-10"></div>

              <div className="flex items-center justify-between mb-6">
                <h3 className="font-bold text-lg">My Profile</h3>
              </div>

              <div className="flex flex-col items-center text-center mb-6">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-gray-700 to-gray-800 border-4 border-black shadow-xl flex items-center justify-center mb-3 relative">
                  {resumeData ? <span className="text-3xl">👨‍💻</span> : <User className="w-8 h-8 text-gray-500" />}
                  {resumeData && <div className="absolute bottom-0 right-0 w-6 h-6 bg-green-500 rounded-full border-4 border-black"></div>}
                </div>
                <h4 className="text-xl font-bold">{resumeData?.name || (resumeData ? "Candidate Ready" : "Guest User")}</h4>
                <p className="text-gray-400 text-sm">{resumeData ? "Senior Developer" : "Upload resume to begin"}</p>
              </div>

              {!resumeId ? (
                <label className="w-full h-12 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold flex items-center justify-center gap-2 cursor-pointer transition active:scale-95 shadow-lg shadow-blue-600/20">
                  <Upload className="w-4 h-4" />
                  Upload Resume
                  <input type="file" className="hidden" onChange={handleUpload} accept=".pdf,.docx,.txt" />
                </label>
              ) : (
                <div className="space-y-3">
                  <div className="bg-white/5 rounded-xl p-4">
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-400">Profile Strength</span>
                      <span className="text-green-400 font-bold">85%</span>
                    </div>
                    <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                      <div className="h-full w-[85%] bg-gradient-to-r from-green-400 to-emerald-500 rounded-full"></div>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {resumeData?.skills?.slice(0, 6).map((skill, i) => (
                      <span key={i} className="px-2.5 py-1 bg-white/5 text-gray-300 rounded-lg text-xs font-medium border border-white/5">{skill}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Stats Widget */}
            <div className="grid grid-cols-2 gap-4">
              <div className="ios-card p-4 flex flex-col items-center justify-center text-center h-32">
                <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center mb-2 text-purple-400">
                  <Briefcase className="w-5 h-5" />
                </div>
                <span className="text-2xl font-bold">{jobs.length}</span>
                <span className="text-xs text-gray-500">Jobs Found</span>
              </div>
              <div className="ios-card p-4 flex flex-col items-center justify-center text-center h-32">
                <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center mb-2 text-green-400">
                  <CheckCircle className="w-5 h-5" />
                </div>
                <span className="text-2xl font-bold">{Object.keys(tailoredResumes).length}</span>
                <span className="text-xs text-gray-500">Tailored</span>
              </div>
            </div>

            {/* Tech News Widget */}
            <TechNewsWidget />

          </div>
        </div>
      </main>
    </div>
  );
}

function TechNewsWidget() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchNews = async () => {
    try {
      const resp = await fetch(`${API_BASE}/news/latest`);
      if (resp.ok) {
        const data = await resp.json();
        setNews(data.news || []);
      }
    } catch (err) { console.error("News fetch error:", err); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    fetchNews();
    const interval = setInterval(fetchNews, 60000); // Refresh every 1 min
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="ios-card p-5 h-[400px] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-lg flex items-center gap-2">
          <Globe className="w-5 h-5 text-blue-400" /> Tech News
        </h3>
        <span className="text-[10px] bg-red-500 text-white px-2 py-0.5 rounded-full animate-pulse">LIVE</span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar">
        {loading ? (
          <div className="flex flex-col gap-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-16 bg-white/5 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : (
          news.map((item, idx) => (
            <a
              key={idx}
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block p-3 rounded-xl bg-white/5 hover:bg-white/10 transition group border border-transparent hover:border-white/10"
            >
              <div className="flex justify-between items-start mb-1">
                <span className="text-[10px] text-blue-400 font-bold uppercase tracking-wider">{item.source}</span>
                <span className="text-[10px] text-gray-500">{item.time ? new Date(item.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Just now'}</span>
              </div>
              <h4 className="text-sm font-medium text-gray-200 group-hover:text-white leading-snug line-clamp-2">
                {item.title}
              </h4>
            </a>
          ))
        )}
        {!loading && news.length === 0 && (
          <div className="text-center text-gray-500 text-sm py-10">
            No news updates available.
          </div>
        )}
      </div>
    </div>
  );
}

function JobCard({ job, atsScores, tailoredResumes, calculateATS, tailorResume, downloadResume }) {
  const [expanded, setExpanded] = useState(false);

  // Normalize ghost score
  let rawScore = job.ghost_score || 0;
  if (rawScore > 1) rawScore = rawScore / 100;
  const ghostScore = Math.round(rawScore * 100);
  const ghostColor = ghostScore > 50 ? 'text-red-400' : ghostScore > 25 ? 'text-yellow-400' : 'text-green-400';

  const atsData = atsScores[job.id];
  const hasAtsScore = atsData && atsData.ats_score !== undefined;
  const atsLoading = atsData && atsData.loading;

  let matchScoreDisplay = '--';
  let matchColor = 'text-gray-500';

  if (hasAtsScore) {
    const score = atsData.ats_score;
    matchScoreDisplay = `${score}%`;
    matchColor = score >= 70 ? 'text-green-400' : score >= 50 ? 'text-yellow-400' : 'text-red-400';
  }

  return (
    <div className="ios-card p-5 group cursor-pointer transition-all duration-300" onClick={() => setExpanded(!expanded)}>
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center text-xl font-bold text-gray-400 border border-white/10 shrink-0">
            {job.company.charAt(0)}
          </div>
          <div>
            <h3 className="text-lg font-bold text-white leading-tight group-hover:text-blue-400 transition">{job.title}</h3>
            <p className="text-gray-400 text-sm mt-0.5">{job.company}</p>
          </div>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-xs font-medium text-gray-500 bg-white/5 px-2 py-1 rounded-lg">
            {job.days_ago === 0 ? 'Today' : `${job.days_ago}d ago`}
          </span>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-4 pl-[4.5rem]">
        <span className="text-xs px-2.5 py-1 rounded-md bg-white/5 text-gray-300 flex items-center gap-1.5">
          <MapPin className="w-3 h-3" /> {job.location}
        </span>
        {job.salary_min && (
          <span className="text-xs px-2.5 py-1 rounded-md bg-green-500/10 text-green-400 flex items-center gap-1.5">
            <Briefcase className="w-3 h-3" /> ${(job.salary_min / 1000).toFixed(0)}k - ${(job.salary_max / 1000).toFixed(0)}k
          </span>
        )}
        <span className={`text-xs px-2.5 py-1 rounded-md bg-white/5 flex items-center gap-1.5 ${ghostColor}`}>
          <Ghost className="w-3 h-3" /> Risk: {ghostScore}%
        </span>
      </div>

      {/* Description Summary (Always Visible) */}
      {!expanded && (
        <div className="pl-[4.5rem] mb-4">
          <p className="text-sm text-gray-400 line-clamp-2 leading-relaxed">
            {job.description || "No description available."}
          </p>
        </div>
      )}

      {/* Expanded Description */}
      {expanded && (
        <div className="pl-[4.5rem] mb-4 animate-slide-up">
          <div className="bg-white/5 rounded-xl p-4 text-sm text-gray-300 leading-relaxed border border-white/5">
            <h4 className="font-bold text-white mb-2 flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-400" /> Job Description
            </h4>
            <p className="whitespace-pre-wrap">{job.description || "No description available."}</p>
            <a href={job.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 text-xs font-bold mt-2 inline-block">
              View Full Posting on {job.site || "Source"} &rarr;
            </a>
          </div>

          {/* Missing Skills Analysis */}
          {hasAtsScore && atsData.breakdown && (
            <div className="mt-3 bg-red-500/10 rounded-xl p-4 border border-red-500/20">
              <h4 className="font-bold text-red-400 text-xs uppercase tracking-wider mb-2">Missing Skills</h4>
              <div className="flex flex-wrap gap-2">
                {atsData.breakdown.missing_skills.length > 0 ? (
                  atsData.breakdown.missing_skills.map((skill, i) => (
                    <span key={i} className="text-xs px-2 py-1 rounded bg-red-500/20 text-red-300 border border-red-500/20">
                      {skill}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-green-400">No missing skills found! Great match.</span>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="pl-[4.5rem] flex items-center justify-between border-t border-white/5 pt-4 mt-2">
        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          {!hasAtsScore ? (
            <button
              onClick={(e) => { e.stopPropagation(); calculateATS(job.id); }}
              disabled={atsLoading}
              className="text-xs bg-white/5 hover:bg-white/10 text-white px-4 py-2 rounded-full transition font-medium flex items-center gap-2"
            >
              {atsLoading ? <div className="w-3 h-3 border-2 border-gray-400 border-t-white rounded-full animate-spin" /> : <Sparkles className="w-3 h-3 text-yellow-400" />}
              Match Score
            </button>
          ) : (
            <div className="flex items-center gap-3">
              <div className="flex flex-col">
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">ATS Match</span>
                <div className={`text-lg font-bold ${matchColor}`}>{matchScoreDisplay}</div>
              </div>

              {!tailoredResumes[job.id]?.tailored_content ? (
                <button
                  onClick={(e) => { e.stopPropagation(); tailorResume(job.id); }}
                  disabled={tailoredResumes[job.id]?.loading}
                  className="text-xs bg-purple-500 text-white px-4 py-2 rounded-full hover:bg-purple-600 transition font-medium flex items-center gap-2 shadow-lg shadow-purple-500/20"
                >
                  {tailoredResumes[job.id]?.loading ? "✨ Magic..." : "✨ Tailor Resume"}
                </button>
              ) : (
                <button
                  onClick={(e) => { e.stopPropagation(); downloadResume(tailoredResumes[job.id].tailored_resume_id, `Resume_${job.company}_Tailored.docx`); }}
                  className="text-xs bg-green-500 text-white px-4 py-2 rounded-full hover:bg-green-600 transition font-medium flex items-center gap-2 shadow-lg shadow-green-500/20"
                >
                  <Download className="w-3 h-3" /> Download DOCX
                </button>
              )}
            </div>
          )}
        </div>

        <button
          onClick={(e) => { e.stopPropagation(); setExpanded(!expanded); }}
          className={`w-8 h-8 rounded-full flex items-center justify-center transition ${expanded ? 'bg-white/20 rotate-90' : 'bg-white/10 hover:bg-blue-500 hover:text-white'}`}
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

export default App;
