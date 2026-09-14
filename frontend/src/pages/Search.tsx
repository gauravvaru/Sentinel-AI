import * as React from 'react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Panel } from '@/components/ui/Panel';
import { Badge } from '@/components/ui/Badge';
import { api } from '@/api/client';
import { Search as SearchIcon, Loader2 } from 'lucide-react';

export function Search() {
  const [query, setQuery] = React.useState('');
  const [isSearching, setIsSearching] = React.useState(false);
  const [results, setResults] = React.useState<any[] | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [hasSearched, setHasSearched] = React.useState(false);

  const handleSearch = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!query.trim()) return;
    
    setIsSearching(true);
    setError(null);
    setHasSearched(true);
    
    try {
      const response = await api.search(query, 20);
      setResults(response.results);
    } catch (err) {
      setError('Search failed. Please verify connection to the Semantic Engine.');
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="flex flex-col w-full h-full min-h-0 gap-6">
      {/* Header Banner */}
      <section className="w-full bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] px-6 lg:px-8 py-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-5 shrink-0">
        <div className="flex items-start gap-4 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-surface-secondary flex items-center justify-center shrink-0 text-text-secondary mt-0.5">
            <span className="material-symbols-outlined text-[18px] text-primary">search</span>
          </div>
          <div className="flex flex-col min-w-0">
            <div className="flex flex-col xl:flex-row xl:items-baseline gap-x-3 gap-y-0.5">
              <h1 className="font-sans text-[20px] text-text-primary font-semibold tracking-tight">
                Semantic Search
              </h1>
              <p className="font-sans text-[13px] text-text-secondary">
                Vector-based discovery of narratives and influence nodes
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="w-full bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] p-2 shrink-0 z-10 sticky top-0">
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none text-text-muted">
              <span className="material-symbols-outlined text-[18px]">search</span>
            </div>
            <Input 
              type="text" 
              placeholder="Search influence nodes, signals, campaigns..." 
              className="pl-11 h-12 text-[14px] font-sans bg-transparent border-transparent shadow-none focus-visible:ring-0 focus-visible:border-transparent"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <button type="submit" disabled={isSearching || !query.trim()} className="h-12 px-6 rounded-lg bg-primary hover:bg-primary/90 text-white font-sans text-[14px] font-medium transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shrink-0 flex items-center justify-center min-w-[120px]">
            {isSearching ? <span className="material-symbols-outlined animate-spin text-[18px]">progress_activity</span> : 'Search'}
          </button>
        </form>
      </section>

      <div className="flex-1 min-h-0 flex flex-col gap-4">
        {!hasSearched ? (
          <div className="flex-1 rounded-xl border border-dashed border-border-strong flex flex-col items-center justify-center text-text-muted p-12 text-center bg-surface-secondary/20">
            <div className="w-16 h-16 rounded-full bg-surface-primary shadow-sm flex items-center justify-center mb-4">
              <span className="material-symbols-outlined text-[32px] text-border-strong">manage_search</span>
            </div>
            <h3 className="text-[15px] font-semibold text-text-primary mb-2 font-sans">Initialize Semantic Search</h3>
            <p className="text-[13px] max-w-md font-sans text-text-secondary leading-relaxed">
              Enter a query above to search through the vector store. Natural language queries are supported and will be matched against event embeddings.
            </p>
          </div>
        ) : error ? (
          <div className="p-4 bg-threat/10 text-threat rounded-md border border-threat/20 font-mono text-[13px]">
            {error}
          </div>
        ) : (
          <div className="space-y-4 flex-1 flex flex-col min-h-0">
            <div className="text-[12px] text-text-secondary font-mono px-2 shrink-0">
              Found {results?.length || 0} results for <span className="text-text-primary font-medium">"{query}"</span>
            </div>
            
            <div className="flex flex-col gap-3 overflow-y-auto pb-8 pr-2">
              {results?.map((result, idx) => (
                <div key={idx} className="p-5 bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] hover:border-primary/50 transition-colors border border-transparent flex flex-col gap-3">
                  <div className="flex justify-between items-start gap-4">
                    <div className="font-sans text-[14px] text-text-primary leading-relaxed">{result.text}</div>
                    <Badge variant="primary" className="shrink-0 font-mono text-[11px] h-fit">
                      {(result.similarity * 100).toFixed(1)}% MATCH
                    </Badge>
                  </div>
                  <div className="text-[11px] text-text-muted font-mono flex flex-wrap gap-x-6 gap-y-2 pt-3 border-t border-border-subtle">
                    <span className="flex items-center gap-1.5"><span className="material-symbols-outlined text-[14px]">tag</span> ID: {result.id}</span>
                    {result.platform && <span className="flex items-center gap-1.5"><span className="material-symbols-outlined text-[14px]">public</span> {result.platform}</span>}
                    {result.user_id && <span className="flex items-center gap-1.5"><span className="material-symbols-outlined text-[14px]">person</span> {result.user_id}</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
