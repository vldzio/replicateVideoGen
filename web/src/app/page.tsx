'use client';

import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Play, 
  Film, 
  Key, 
  Layers, 
  Image as ImageIcon, 
  Video, 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  RefreshCw, 
  ArrowRight,
  ExternalLink,
  Sliders,
  ChevronRight,
  Info
} from 'lucide-react';
import { DEMO_STORY } from '@/lib/demoData';
import { StoryData, PipelineStage } from '@/types/pipeline';

export default function Home() {
  const [themeInput, setThemeInput] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [stage, setStage] = useState<PipelineStage>('idle');
  const [statusMessage, setStatusMessage] = useState('');
  const [story, setStory] = useState<StoryData | null>(DEMO_STORY);
  const [isDemoMode, setIsDemoMode] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'characters' | 'scenes' | 'preview'>('overview');
  const [selectedSceneIndex, setSelectedSceneIndex] = useState(0);
  const [llmKey, setLlmKey] = useState('');
  const [llmBase, setLlmBase] = useState('https://api.openai.com/v1');
  const [isPlayingReel, setIsPlayingReel] = useState(false);
  const [currentReelScene, setCurrentReelScene] = useState(0);

  // Load API Key from local storage if available
  useEffect(() => {
    const savedKey = localStorage.getItem('storyforge_replicate_token');
    if (savedKey) setApiKey(savedKey);
    try {
      // the optional LLM key is kept for this tab only (sessionStorage), never localStorage
      setLlmKey(sessionStorage.getItem('storyforge_llm_key') || '');
      setLlmBase(sessionStorage.getItem('storyforge_llm_base') || 'https://api.openai.com/v1');
    } catch { /* private mode */ }
  }, []);

  const saveApiKey = (key: string) => {
    setApiKey(key);
    localStorage.setItem('storyforge_replicate_token', key);
    try {
      sessionStorage.setItem('storyforge_llm_key', llmKey.trim());
      sessionStorage.setItem('storyforge_llm_base', llmBase);
    } catch { /* private mode */ }
    setShowKeyModal(false);
  };

  // Story text comes from the demo API (a free-tier LLM gateway, traced in LangSmith).
  // Without NEXT_PUBLIC_DEMO_API_URL it falls back to Replicate's Gemini using the visitor's own token.
  const DEMO_API = (process.env.NEXT_PUBLIC_DEMO_API_URL || '').replace(/\/+$/, '');
  async function fetchStory(theme: string): Promise<StoryData> {
    if (DEMO_API) {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (llmKey.trim()) {
        headers['X-LLM-Api-Key'] = llmKey.trim();
        headers['X-LLM-Base-Url'] = llmBase;
      }
      let res: Response;
      try {
        res = await fetch(`${DEMO_API}/story`, { method: 'POST', headers, body: JSON.stringify({ theme }) });
      } catch {
        throw new Error('Could not reach the story service. It may be waking up (about a minute); please try again.');
      }
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || `Story service error (${res.status})`);
      return { theme, ...data.story } as StoryData;
    }
    const res = await fetch('/api/story/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ theme, customToken: apiKey }),
    });
    const result = await res.json();
    if (!result.success) throw new Error(result.error);
    return { theme, ...result.story } as StoryData;
  }

  // Free path: only the story is generated (no media, so no Replicate token needed)
  const writeStoryOnly = async () => {
    try {
      setIsDemoMode(false);
      setStage('story');
      setStatusMessage('Writing the story with a live LLM (10-40 s)...');
      const generated = await fetchStory(themeInput || 'a lone cybernetic wanderer restoring an ancient organic conservatory');
      setStory(generated);
      setActiveTab('characters');
      setStage('complete');
      setStatusMessage('Story written live. Add your Replicate token to also generate images and video.');
    } catch (err: any) {
      setStage('idle');
      setStatusMessage(`Error: ${err.message}`);
    }
  };

  // Video Reel auto-advance
  useEffect(() => {
    if (!isPlayingReel || !story) return;
    const currentScene = story.scenes[currentReelScene];
    const duration = (currentScene?.durationSeconds || 5) * 1000;

    const timer = setTimeout(() => {
      if (currentReelScene < story.scenes.length - 1) {
        setCurrentReelScene(prev => prev + 1);
      } else {
        setIsPlayingReel(false);
        setCurrentReelScene(0);
      }
    }, duration);

    return () => clearTimeout(timer);
  }, [isPlayingReel, currentReelScene, story]);

  // Polling helper
  async function pollPrediction(predictionId: string, customToken?: string): Promise<string> {
    const startTime = Date.now();
    const timeoutMs = 240000; // 4 minutes timeout

    while (Date.now() - startTime < timeoutMs) {
      const res = await fetch(`/api/predictions/${predictionId}?customToken=${encodeURIComponent(customToken || '')}`);
      if (!res.ok) {
        throw new Error(`Polling request failed: ${res.statusText}`);
      }
      const data = await res.json();

      if (data.status === 'succeeded') {
        return data.output;
      }
      if (data.status === 'failed' || data.status === 'canceled') {
        throw new Error(data.error || 'Generation failed on Replicate');
      }

      // Wait 3 seconds before next poll
      await new Promise(r => setTimeout(r, 3000));
    }
    throw new Error('Generation timed out');
  }

  // Load Pre-generated Demo Showcase
  const loadDemo = () => {
    setIsDemoMode(true);
    setStory(DEMO_STORY);
    setThemeInput(DEMO_STORY.theme || '');
    setStage('complete');
    setStatusMessage('Loaded pre-generated high-fidelity showcase story & clips.');
  };

  // Run Real End-to-End Pipeline
  const runLivePipeline = async () => {
    if (!apiKey) {
      setShowKeyModal(true);
      return;
    }

    try {
      setIsDemoMode(false);
      setStage('story');
      setStatusMessage('Step 1/4: Synthesizing character arcs & scene breakdowns with Gemini...');
      
      // 1. Generate Story
      const generatedStory: StoryData = await fetchStory(
        themeInput || 'a lone cybernetic wanderer restoring an ancient organic conservatory'
      );
      setStory(generatedStory);
      setActiveTab('characters');

      // 2. Generate Assets (Characters & Setting images)
      setStage('assets');
      setStatusMessage('Step 2/4: Generating high-resolution character and setting visuals with MiniMax...');
      
      // Trigger character art
      for (let i = 0; i < generatedStory.characters.length; i++) {
        const char = generatedStory.characters[i];
        setStatusMessage(`Generating portrait for ${char.name}...`);
        const assetRes = await fetch('/api/assets/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: char.characterPrompt,
            customToken: apiKey,
            type: 'character',
            identifier: char.characterId
          })
        });
        const assetData = await assetRes.json();
        if (assetData.predictionId) {
          const imgUrl = await pollPrediction(assetData.predictionId, apiKey);
          char.imageUrl = imgUrl;
          setStory({ ...generatedStory });
        }
      }

      // Trigger setting images for the scenes
      for (let s = 0; s < Math.min(generatedStory.scenes.length, 2); s++) {
        const sc = generatedStory.scenes[s];
        setStatusMessage(`Generating background art for Scene ${sc.sceneNumber}...`);
        const sceneArtRes = await fetch('/api/assets/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: sc.settingPrompt,
            customToken: apiKey,
            type: 'scene',
            identifier: sc.sceneNumber
          })
        });
        const sceneArtData = await sceneArtRes.json();
        if (sceneArtData.predictionId) {
          const sceneImgUrl = await pollPrediction(sceneArtData.predictionId, apiKey);
          sc.settingImageUrl = sceneImgUrl;
          setStory({ ...generatedStory });
        }
      }

      // 3. Composite Scene (FLUX Kontext)
      setStage('compositing');
      setStatusMessage('Step 3/4: Seamlessly stitching characters into background scenes with FLUX Kontext...');
      const charImage = generatedStory.characters[0]?.imageUrl;
      for (let s = 0; s < Math.min(generatedStory.scenes.length, 2); s++) {
        const sc = generatedStory.scenes[s];
        if (charImage && sc.settingImageUrl) {
          setStatusMessage(`Compositing Scene ${sc.sceneNumber}...`);
          const compRes = await fetch('/api/scenes/composite', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              characterImageUrl: charImage,
              settingImageUrl: sc.settingImageUrl,
              prompt: `${sc.sceneDescription} ${sc.characterContext}`,
              customToken: apiKey,
              sceneNumber: sc.sceneNumber
            })
          });
          const compData = await compRes.json();
          if (compData.predictionId) {
            const compUrl = await pollPrediction(compData.predictionId, apiKey);
            sc.compositeImageUrl = compUrl;
            setStory({ ...generatedStory });
          }
        }
      }

      // 4. Video Generation (Seedance)
      setStage('videos');
      setStatusMessage('Step 4/4: Rendering motion clips with ByteDance Seedance...');
      for (let s = 0; s < Math.min(generatedStory.scenes.length, 2); s++) {
        const sc = generatedStory.scenes[s];
        const motionPrompt = `${sc.sceneDescription} ${sc.startingSettingPrompt || ''} ${sc.endingSettingPrompt || ''} ${sc.motionPrompt || ''}`.trim();
        setStatusMessage(`Generating motion clip for Scene ${sc.sceneNumber}...`);

        const vidRes = await fetch('/api/videos/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: motionPrompt,
            imageUrl: sc.compositeImageUrl || sc.settingImageUrl,
            duration: sc.durationSeconds,
            customToken: apiKey,
            sceneNumber: sc.sceneNumber
          })
        });
        const vidData = await vidRes.json();
        if (vidData.predictionId) {
          const videoUrl = await pollPrediction(vidData.predictionId, apiKey);
          sc.videoUrl = videoUrl;
          setStory({ ...generatedStory });
        }
      }

      setStage('complete');
      setStatusMessage('Complete! All clips have been synthesized and stitched into your reel.');
      setActiveTab('preview');
    } catch (err: any) {
      console.error(err);
      setStatusMessage(`Error during execution: ${err.message || 'Unknown error'}`);
      setStage('idle');
    }
  };

  return (
    <main className="min-h-screen text-slate-100 flex flex-col">
      {/* Navigation Header */}
      <header className="border-b border-slate-800 bg-slate-950/70 backdrop-blur-md sticky top-0 z-40 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Film className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-indigo-200 to-purple-300 bg-clip-text text-transparent">
                StoryForge AI
              </span>
              <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-medium">
                Vercel Demo
              </span>
            </div>
            <p className="text-xs text-slate-400">Autonomous Script-to-Video Reel Pipeline</p>
          </div>
        </div>

        {/* Top Controls */}
        <div className="flex items-center space-x-3">
          <button
            onClick={loadDemo}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 ${
              isDemoMode
                ? 'bg-purple-600/20 text-purple-300 border border-purple-500/30'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Preset Showcase</span>
          </button>

          <button
            onClick={() => setShowKeyModal(true)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 ${
              apiKey
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
            }`}
          >
            <Key className="w-3.5 h-3.5" />
            <span>{apiKey ? 'Replicate Connected' : 'Set API Key'}</span>
          </button>
        </div>
      </header>

      {/* Main Body */}
      <div className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        
        {/* Hero Generator Card */}
        <section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />
          
          <div className="max-w-3xl space-y-4">
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Transform Ideas into Multi-Scene Video Stories
            </h1>
            <p className="text-sm text-slate-400 leading-relaxed">
              StoryForge combines <strong>Gemini 2.5</strong> (structured story writing), <strong>MiniMax</strong> (art), <strong>FLUX Kontext</strong> (multi-image character stitching), and <strong>ByteDance Seedance</strong> (neural motion video) into an autonomous serverless reel generator.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <input
                type="text"
                value={themeInput}
                onChange={(e) => setThemeInput(e.target.value)}
                placeholder="e.g. A solitary botanist uncovering a glowing flora sanctuary in an abandoned cyberpunk city"
                className="flex-1 px-4 py-3 rounded-xl bg-slate-950 border border-slate-700 text-sm focus:outline-none focus:border-indigo-500 transition-colors placeholder:text-slate-500"
                disabled={stage !== 'idle' && stage !== 'complete'}
              />
              
              <button
                onClick={writeStoryOnly}
                disabled={stage !== 'idle' && stage !== 'complete'}
                title="Free: writes the story with a live LLM, no Replicate token needed"
                className="px-5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white font-medium text-sm flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                <span>Write story (free)</span>
              </button>

              <button
                onClick={runLivePipeline}
                disabled={stage !== 'idle' && stage !== 'complete'}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium text-sm flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/25 transition-all disabled:opacity-50"
              >
                {stage !== 'idle' && stage !== 'complete' ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Story + media (your Replicate token)</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Pipeline Stage Tracker */}
          <div className="mt-8 pt-6 border-t border-slate-800/80">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center justify-between">
              <span>Pipeline Progress</span>
              {statusMessage && (
                <span className="text-indigo-400 normal-case font-normal flex items-center gap-1.5 animate-pulse">
                  <Clock className="w-3.5 h-3.5" />
                  {statusMessage}
                </span>
              )}
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { key: 'story', label: '1. Gemini Story', desc: 'JSON screenplay & scenes', icon: Sparkles },
                { key: 'assets', label: '2. MiniMax Art', desc: 'Characters & settings', icon: ImageIcon },
                { key: 'compositing', label: '3. FLUX Kontext', desc: 'Character/Scene stitching', icon: Layers },
                { key: 'videos', label: '4. Seedance Video', desc: 'Motion clips synthesis', icon: Video },
              ].map((step, idx) => {
                const isActive = stage === step.key;
                const isPassed = 
                  (stage === 'complete') ||
                  (stage === 'assets' && idx === 0) ||
                  (stage === 'compositing' && idx <= 1) ||
                  (stage === 'videos' && idx <= 2);

                return (
                  <div 
                    key={step.key}
                    className={`p-3.5 rounded-xl border transition-all ${
                      isActive 
                        ? 'bg-indigo-950/40 border-indigo-500 shadow-md shadow-indigo-500/10'
                        : isPassed
                        ? 'bg-slate-950/40 border-emerald-500/30'
                        : 'bg-slate-950/20 border-slate-800 text-slate-500'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <step.icon className={`w-4 h-4 ${isActive ? 'text-indigo-400 animate-pulse' : isPassed ? 'text-emerald-400' : 'text-slate-600'}`} />
                      {isPassed && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                    </div>
                    <div className={`text-xs font-medium ${isActive ? 'text-indigo-200' : isPassed ? 'text-slate-200' : 'text-slate-500'}`}>
                      {step.label}
                    </div>
                    <div className="text-[11px] text-slate-500">{step.desc}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Pipeline Inspector Tabs */}
        {story && (
          <div className="space-y-4">
            <div className="flex border-b border-slate-800 text-sm font-medium gap-6">
              {[
                { id: 'overview', label: 'Storyboard Overview' },
                { id: 'characters', label: `Characters (${story.characters.length})` },
                { id: 'scenes', label: `Scenes & Stitches (${story.scenes.length})` },
                { id: 'preview', label: 'Cinematic Reel Player' },
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`pb-3 border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-indigo-500 text-indigo-400'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* TAB 1: OVERVIEW */}
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {story.scenes.map((scene, idx) => (
                  <div key={scene.sceneNumber} className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden flex flex-col group hover:border-slate-700 transition-all">
                    <div className="relative aspect-video bg-slate-950 flex items-center justify-center overflow-hidden">
                      {scene.videoUrl ? (
                        <video src={scene.videoUrl} autoPlay loop muted playsInline className="w-full h-full object-cover" />
                      ) : scene.compositeImageUrl ? (
                        <img src={scene.compositeImageUrl} alt={`Scene ${scene.sceneNumber}`} className="w-full h-full object-cover" />
                      ) : scene.settingImageUrl ? (
                        <img src={scene.settingImageUrl} alt={`Scene ${scene.sceneNumber}`} className="w-full h-full object-cover" />
                      ) : (
                        <div className="text-xs text-slate-600 flex flex-col items-center gap-1">
                          <ImageIcon className="w-6 h-6 text-slate-700" />
                          <span>Awaiting render</span>
                        </div>
                      )}
                      <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-black/70 backdrop-blur-md text-[10px] font-semibold text-slate-200">
                        Scene {scene.sceneNumber}
                      </div>
                      <div className="absolute bottom-2 right-2 px-2 py-0.5 rounded bg-black/70 backdrop-blur-md text-[10px] font-semibold text-indigo-300">
                        {scene.durationSeconds}s
                      </div>
                    </div>
                    
                    <div className="p-4 flex-1 flex flex-col justify-between space-y-3">
                      <div>
                        <p className="text-xs text-slate-300 line-clamp-3 leading-relaxed">
                          {scene.sceneDescription}
                        </p>
                      </div>

                      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                        <span className="italic line-clamp-1">"{scene.audioText}"</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* TAB 2: CHARACTERS */}
            {activeTab === 'characters' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {story.characters.map((char) => (
                  <div key={char.characterId} className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 flex flex-col sm:flex-row gap-5">
                    <div className="w-full sm:w-44 aspect-square rounded-lg bg-slate-950 border border-slate-800 overflow-hidden flex-shrink-0 flex items-center justify-center">
                      {char.imageUrl ? (
                        <img src={char.imageUrl} alt={char.name} className="w-full h-full object-cover" />
                      ) : (
                        <div className="text-xs text-slate-600 flex flex-col items-center gap-1">
                          <ImageIcon className="w-8 h-8 text-slate-700" />
                          <span>Generating art...</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-base text-white">{char.name}</h3>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                          ID: {char.characterId}
                        </span>
                      </div>
                      
                      <div className="text-xs text-slate-400 space-y-1">
                        <span className="font-medium text-slate-300 block">Character Visual Prompt:</span>
                        <p className="leading-relaxed bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 font-mono text-[11px] text-slate-300">
                          {char.characterPrompt}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* TAB 3: SCENES & COMPOSITING */}
            {activeTab === 'scenes' && (
              <div className="space-y-6">
                {/* Scene selector pills */}
                <div className="flex gap-2">
                  {story.scenes.map((sc, i) => (
                    <button
                      key={sc.sceneNumber}
                      onClick={() => setSelectedSceneIndex(i)}
                      className={`px-4 py-2 rounded-lg text-xs font-medium border transition-all ${
                        selectedSceneIndex === i
                          ? 'bg-indigo-600 text-white border-indigo-500'
                          : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      Scene {sc.sceneNumber}
                    </button>
                  ))}
                </div>

                {/* Selected Scene Breakdown */}
                {story.scenes[selectedSceneIndex] && (() => {
                  const sc = story.scenes[selectedSceneIndex];
                  return (
                    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Step A: Setting Prompt */}
                        <div className="space-y-2">
                          <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider block">
                            Stage 1: Setting Art (MiniMax)
                          </span>
                          <div className="aspect-video bg-slate-950 rounded-lg border border-slate-800 overflow-hidden flex items-center justify-center">
                            {sc.settingImageUrl ? (
                              <img src={sc.settingImageUrl} alt="Setting" className="w-full h-full object-cover" />
                            ) : (
                              <span className="text-xs text-slate-600">Pending image</span>
                            )}
                          </div>
                          <p className="text-[11px] text-slate-400 line-clamp-3">
                            {sc.settingPrompt}
                          </p>
                        </div>

                        {/* Step B: FLUX Kontext Composite */}
                        <div className="space-y-2">
                          <span className="text-xs font-semibold text-purple-400 uppercase tracking-wider block">
                            Stage 2: Stitched Composite (FLUX)
                          </span>
                          <div className="aspect-video bg-slate-950 rounded-lg border border-slate-800 overflow-hidden flex items-center justify-center">
                            {sc.compositeImageUrl ? (
                              <img src={sc.compositeImageUrl} alt="Composite" className="w-full h-full object-cover" />
                            ) : (
                              <span className="text-xs text-slate-600">Pending composite</span>
                            )}
                          </div>
                          <p className="text-[11px] text-slate-400 line-clamp-3">
                            Context: {sc.characterContext}
                          </p>
                        </div>

                        {/* Step C: Motion Video */}
                        <div className="space-y-2">
                          <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider block">
                            Stage 3: Rendered Clip (Seedance)
                          </span>
                          <div className="aspect-video bg-slate-950 rounded-lg border border-slate-800 overflow-hidden flex items-center justify-center">
                            {sc.videoUrl ? (
                              <video src={sc.videoUrl} controls loop playsInline className="w-full h-full object-cover" />
                            ) : (
                              <span className="text-xs text-slate-600">Pending video clip</span>
                            )}
                          </div>
                          <p className="text-[11px] text-slate-400 line-clamp-3">
                            Motion: {sc.motionPrompt || 'Dynamic motion animation'}
                          </p>
                        </div>
                      </div>

                      {/* Screenplay & Dialogue Info */}
                      <div className="p-4 rounded-lg bg-slate-950 border border-slate-800/80 space-y-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-semibold text-slate-300">Narrative & Audio Prompt</span>
                          <span className="text-slate-500">Duration: {sc.durationSeconds}s</span>
                        </div>
                        <p className="text-xs text-slate-400 italic">
                          "{sc.audioText}"
                        </p>
                      </div>
                    </div>
                  );
                })()}
              </div>
            )}

            {/* TAB 4: CINEMATIC REEL PLAYER */}
            {activeTab === 'preview' && (
              <div className="max-w-4xl mx-auto bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
                <div className="relative aspect-video bg-black rounded-xl overflow-hidden shadow-2xl border border-slate-800">
                  {story.scenes[currentReelScene]?.videoUrl ? (
                    <video 
                      key={story.scenes[currentReelScene].videoUrl}
                      src={story.scenes[currentReelScene].videoUrl} 
                      autoPlay 
                      playsInline
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 space-y-2">
                      <Film className="w-12 h-12 text-slate-700" />
                      <span className="text-sm">No video clip rendered for Scene {currentReelScene + 1}</span>
                    </div>
                  )}

                  {/* On-screen subtitle overlay */}
                  <div className="absolute bottom-4 left-6 right-6 p-3 rounded-lg bg-black/60 backdrop-blur-md border border-white/10 text-center">
                    <p className="text-xs md:text-sm text-slate-200 font-medium">
                      {story.scenes[currentReelScene]?.audioText}
                    </p>
                  </div>

                  <div className="absolute top-4 left-4 px-2.5 py-1 rounded-md bg-black/70 backdrop-blur-md text-xs font-semibold text-indigo-300">
                    Scene {currentReelScene + 1} / {story.scenes.length}
                  </div>
                </div>

                {/* Reel Controls */}
                <div className="flex items-center justify-between bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => setIsPlayingReel(!isPlayingReel)}
                      className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs flex items-center space-x-2 transition-colors"
                    >
                      <Play className={`w-3.5 h-3.5 ${isPlayingReel ? 'fill-current' : ''}`} />
                      <span>{isPlayingReel ? 'Pause Reel' : 'Play Full Reel'}</span>
                    </button>
                    
                    <span className="text-xs text-slate-400">
                      {isPlayingReel ? 'Playing sequential scenes...' : 'Paused'}
                    </span>
                  </div>

                  {/* Scene quick scrubber */}
                  <div className="flex gap-1.5">
                    {story.scenes.map((_, i) => (
                      <button
                        key={i}
                        onClick={() => {
                          setIsPlayingReel(false);
                          setCurrentReelScene(i);
                        }}
                        className={`w-7 h-7 rounded text-xs font-semibold flex items-center justify-center transition-all ${
                          currentReelScene === i
                            ? 'bg-indigo-600 text-white'
                            : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                        }`}
                      >
                        {i + 1}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* API Key Modal */}
      {showKeyModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 max-w-md w-full rounded-2xl p-6 space-y-4 shadow-2xl">
            <div className="flex items-center space-x-3 text-indigo-400">
              <Key className="w-5 h-5" />
              <h3 className="text-base font-bold text-white">Replicate API Configuration</h3>
            </div>
            
            <p className="text-xs text-slate-400 leading-relaxed">
              To trigger real model runs on Replicate (Gemini, MiniMax, FLUX, Seedance), enter your Replicate API Token. It is stored securely in your browser and used only for requests.
            </p>

            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-300">Replicate API Token (r8_...)</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="r8_xxxxxxxxxxxxxxxxxxxxxxxx"
                className="w-full px-3 py-2.5 rounded-lg bg-slate-950 border border-slate-700 text-xs focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-2 pt-1 border-t border-slate-800">
              <label className="text-xs font-medium text-slate-300">Optional: your own LLM key for the story step</label>
              <p className="text-[11px] text-slate-500">The free story step has a small daily allowance per visitor. An OpenAI-compatible key lifts it; kept in this tab only.</p>
              <select
                value={llmBase}
                onChange={(e) => setLlmBase(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-xs"
              >
                <option value="https://api.openai.com/v1">OpenAI</option>
                <option value="https://api.groq.com/openai/v1">Groq</option>
                <option value="https://openrouter.ai/api/v1">OpenRouter</option>
                <option value="https://generativelanguage.googleapis.com/v1beta/openai">Google Gemini</option>
              </select>
              <input
                type="password"
                value={llmKey}
                onChange={(e) => setLlmKey(e.target.value)}
                placeholder="LLM API key (optional)"
                className="w-full px-3 py-2.5 rounded-lg bg-slate-950 border border-slate-700 text-xs focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              <button
                type="button"
                onClick={() => setShowKeyModal(false)}
                className="px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              
              <button
                type="button"
                onClick={() => saveApiKey(apiKey)}
                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors"
              >
                Save & Continue
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 px-6 py-4 text-center text-xs text-slate-500">
        StoryForge Video Pipeline • Ready for deployment on Vercel
      </footer>
    </main>
  );
}
