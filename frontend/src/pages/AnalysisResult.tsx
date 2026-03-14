import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, Sparkles, Share2, Download } from 'lucide-react';
import { AnalysisResult, WorldMonitorEvent, DebateResult } from '../services/api';
import AnalysisHeader from '../components/analysis/AnalysisHeader';
import EventSummary from '../components/analysis/EventSummary';
import PredictionPanel from '../components/analysis/PredictionPanel';
import RoleMatrix from '../components/analysis/RoleMatrix';
import CrossAnalysis from '../components/analysis/CrossAnalysis';
import TimelineView from '../components/analysis/TimelineView';
import SentimentRadar from '../components/analysis/SentimentRadar';
import ConflictHeatmap from '../components/analysis/ConflictHeatmap';

// Avoid unused variable warnings
void Share2;
void Download;

// ============ Design System Colors ============
const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

// Check if result is a DebateResult
const isDebateResult = (r: AnalysisResult | DebateResult | null): r is DebateResult =>
  r !== null && 'rounds' in r && Array.isArray(r.rounds);

export default function AnalysisResultPage() {
  const navigate = useNavigate();
  const [result, setResult] = useState<AnalysisResult | DebateResult | null>(null);
  const [event, setEvent] = useState<WorldMonitorEvent | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Load data from sessionStorage
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const storedResult = sessionStorage.getItem('analysisResult');
        const storedEvent = sessionStorage.getItem('selectedEvent');
        if (storedResult) setResult(JSON.parse(storedResult));
        if (storedEvent) setEvent(JSON.parse(storedEvent));
      } catch (err) {
        console.error('Failed to load data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // Handle refresh
  const handleRefresh = async () => {
    setRefreshing(true);
    // In a real implementation, this would re-run the analysis
    setTimeout(() => {
      setRefreshing(false);
    }, 1500);
  };

  // Handle export
  const handleExport = () => {
    if (result && event) {
      const exportData = {
        event: event,
        analysis: result,
        exportedAt: new Date().toISOString(),
        version: '1.0'
      };
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analysis-${event.id}-${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  // Handle share
  const handleShare = () => {
    // In a real implementation, this would open a share modal
    if (event) {
      const shareUrl = `${window.location.origin}/analysis?event=${event.id}`;
      if (navigator.share) {
        navigator.share({ title: event.title, url: shareUrl });
      } else {
        navigator.clipboard.writeText(shareUrl);
        console.log('Link copied to clipboard');
      }
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: COLORS.bg.dark }}>
        <div className="text-center">
          <div className="relative w-20 h-20 mx-auto mb-6">
            <div className="absolute inset-0 rounded-full animate-pulse" style={{ backgroundColor: `${COLORS.primary.cyan}20` }} />
            <div className="absolute inset-2 rounded-full animate-spin border-4" style={{ borderColor: `${COLORS.primary.cyan}30`, borderTopColor: COLORS.primary.cyan }} />
          </div>
          <p style={{ color: COLORS.primary.cyan }} className="text-lg font-medium">Loading analysis result...</p>
        </div>
      </div>
    );
  }

  // Empty state
  if (!result || !event) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center" style={{ backgroundColor: COLORS.bg.dark }}>
        <div className="text-center">
          <div className="w-24 h-24 mx-auto mb-6 rounded-2xl flex items-center justify-center transition-all duration-300"
            style={{ backgroundColor: `${COLORS.primary.cyan}10` }}>
            <span className="text-5xl">📭</span>
          </div>
          <p style={{ color: COLORS.text.primary }} className="text-xl font-medium mb-2">No analysis result found</p>
          <p style={{ color: COLORS.text.muted }} className="mb-8">Please select an event from the dashboard first</p>
          <button
            onClick={() => navigate('/')}
            className="px-8 py-4 rounded-xl font-medium transition-all duration-200 hover:scale-105"
            style={{
              background: `linear-gradient(135deg, ${COLORS.primary.cyan} 0%, ${COLORS.primary.blue} 100%)`,
              color: COLORS.bg.dark,
              boxShadow: `0 0 30px ${COLORS.primary.cyan}40`
            }}
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const conflictsCount = result.cross_analysis?.conflicts?.length || 0;
  const consensusCount = result.cross_analysis?.consensus?.length || 0;

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: COLORS.bg.dark }}>
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(0,229,255,0.03),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,rgba(0,119,255,0.03),transparent_50%)]" />
        <div className="absolute inset-0 opacity-20 bg-[linear-gradient(rgba(0,229,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(0,229,255,0.02)_1px,transparent_1px)] bg-[size:60px_60px]" />
      </div>

      {/* Header */}
      <AnalysisHeader
        event={event}
        overallConfidence={result.overall_confidence}
        analysesCount={result.analyses.length}
        conflictsCount={conflictsCount}
        onBack={() => navigate('/')}
        onRefresh={handleRefresh}
        onExport={handleExport}
        onShare={handleShare}
      />

      {/* Main Content */}
      <main className="flex-1 px-6 py-6 overflow-auto">
        <div className="max-w-[1800px] mx-auto space-y-6">
          {/* Top Section: Event Summary (35%) + Prediction Panel (65%) */}
          <div className="grid gap-6 lg:grid-cols-12">
            {/* Event Summary - 35% */}
            <div className="lg:col-span-4 xl:col-span-4">
              <EventSummary event={event} result={result} />
            </div>

            {/* Prediction Panel - 65% */}
            <div className="lg:col-span-8 xl:col-span-8">
              <PredictionPanel result={result} />
            </div>
          </div>

          {/* Role Analysis Matrix - Full Width */}
          <section>
            <RoleMatrix
              result={result}
              onEditRoles={() => console.log('Edit roles')}
              onExpandDetail={(roleId) => console.log('Expand role:', roleId)}
            />
          </section>

          {/* Cross-Analysis + Timeline Section */}
          <div className="grid gap-6 lg:grid-cols-5">
            {/* Cross-Analysis - 35% */}
            <div className="lg:col-span-2 xl:col-span-2">
              <CrossAnalysis
                result={result}
                onExport={() => console.log('Export cross-analysis')}
              />
            </div>

            {/* Timeline - 65% */}
            <div className="lg:col-span-3 xl:col-span-3">
              <TimelineView
                result={result}
                onExport={() => console.log('Export timeline')}
                onSettings={() => console.log('Timeline settings')}
              />
            </div>
          </div>

          {/* Sentiment & Conflict Analysis Section - NEW */}
          <section>
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-lg font-semibold" style={{ color: COLORS.text.primary }}>
                深度分析
              </h2>
              <span
                className="px-2 py-0.5 rounded text-xs"
                style={{ backgroundColor: `${COLORS.primary.cyan}15`, color: COLORS.primary.cyan }}
              >
                Enhanced
              </span>
            </div>
            <div className="grid gap-6 lg:grid-cols-2">
              {/* Sentiment Radar */}
              <div>
                <SentimentRadar result={result} maxRoles={5} />
              </div>

              {/* Conflict Heatmap */}
              <div>
                <ConflictHeatmap
                  result={result}
                  onCellClick={(r1, r2, intensity) =>
                    console.log(`Conflict: ${r1} vs ${r2} = ${intensity}`)
                  }
                />
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer
        className="flex-shrink-0 border-t backdrop-blur-xl"
        style={{
          height: '40px',
          backgroundColor: `${COLORS.bg.dark}E6`,
          borderColor: `${COLORS.border}80`
        }}
      >
        <div className="h-full px-6 flex items-center justify-between text-xs">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              {refreshing ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" style={{ color: COLORS.status.warning }} />
              ) : (
                <Sparkles className="w-3.5 h-3.5" style={{ color: COLORS.status.success }} />
              )}
              <span style={{ color: COLORS.text.muted }}>
                {refreshing ? 'Refreshing...' : 'Analysis Complete'}
              </span>
            </div>
            <span style={{ color: `${COLORS.border}60` }}>|</span>
            <span style={{ color: COLORS.text.muted }}>
              {isDebateResult(result) ? `Debate Mode · ${result.depth}` : 'Multi-Agent Analysis'}
            </span>
          </div>

          <div className="flex items-center gap-4">
            <span style={{ color: COLORS.text.muted }}>
              {result.analyses.length} roles analyzed
            </span>
            <span style={{ color: COLORS.text.muted }}>
              {consensusCount} consensus points
            </span>
            <span style={{ color: `${COLORS.border}60` }}>|</span>
            <span style={{ color: COLORS.text.muted }}>
              Confidence: {Math.round(result.overall_confidence * 100)}%
            </span>
            <span style={{ color: `${COLORS.border}60` }}>|</span>
            <div className="flex items-center gap-1.5">
              <span style={{ color: COLORS.text.muted }}>EventPredictor</span>
              <span style={{ color: COLORS.primary.cyan }}>v1.0</span>
            </div>
          </div>
        </div>
      </footer>

      {/* Refreshing Overlay */}
      {refreshing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ backgroundColor: `${COLORS.bg.dark}80`, backdropFilter: 'blur(8px)' }}>
          <div className="text-center">
            <div className="relative w-16 h-16 mx-auto mb-4">
              <div className="absolute inset-0 rounded-full border-4 animate-spin" style={{ borderColor: `${COLORS.primary.cyan}30`, borderTopColor: COLORS.primary.cyan }} />
            </div>
            <p style={{ color: COLORS.primary.cyan }} className="text-sm font-medium">Refreshing analysis...</p>
          </div>
        </div>
      )}
    </div>
  );
}
