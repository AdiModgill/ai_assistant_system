/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  Terminal, 
  LayoutGrid, 
  History, 
  Settings, 
  Zap, 
  ArrowRight, 
  Filter, 
  ExternalLink, 
  AlarmClock, 
  FileText, 
  Calendar, 
  Home,
  ChevronDown,
  BrainCircuit,
  RefreshCw,
  Plus,
  CheckCircle2,
  XCircle,
  Shield,
  Mail,
  Smartphone,
  Search,
  Play,
  Pause,
  MessageCircle,
  CloudSun,
  Clipboard,
  Square,
  RotateCcw,
  Copy,
  Trash2,
  Eye,
  Image as ImageIcon,
  Link as LinkIcon,
  Bell,
  BellRing,
  Music
} from 'lucide-react';

interface SubAgentTask {
  id: string;
  name: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'IN PROGRESS' | 'COMPLETED';
}

interface ActivityItem {
  id: string;
  task: string;
  agent: string;
  time: string;
  output?: string;
}

interface ClipboardItem {
  id: string;
  type: 'text' | 'image' | 'link';
  content: string;
  time: string;
  preview?: string;
}

interface ToastItem {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
}

interface SubAgent {
  id: string;
  name: string;
  description: string;
  status: 'ONLINE' | 'OFFLINE' | 'BUSY';
  icon: React.ReactNode;
  color: string;
  lastActive: string;
  capabilities: string[];
  currentTasks: SubAgentTask[];
}

const SUB_AGENTS_DATA: SubAgent[] = [
  {
    id: '1',
    name: 'Alarm Sub-Agent',
    description: 'Manages alarms and timers.',
    status: 'ONLINE',
    icon: <AlarmClock className="w-6 h-6" />,
    color: 'bg-blue-100 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400',
    lastActive: '2 mins ago',
    capabilities: ['Alarms', 'Timers'],
    currentTasks: []
  },
  {
    id: '2',
    name: 'Email Sub-Agent',
    description: 'Sends emails and writes emails using user input.',
    status: 'BUSY',
    icon: <Mail className="w-6 h-6" />,
    color: 'bg-teal-100 text-teal-600 dark:bg-teal-500/20 dark:text-teal-400',
    lastActive: 'Just now',
    capabilities: ['Send email', 'Write email'],
    currentTasks: []
  },
  {
    id: '3',
    name: 'WhatsApp Sub-Agent',
    description: 'Converses with people in real time using AI.',
    status: 'ONLINE',
    icon: <MessageCircle className="w-6 h-6" />,
    color: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400',
    lastActive: '5 mins ago',
    capabilities: ['Real-time conversation', 'AI assistance'],
    currentTasks: []
  },
  {
    id: '4',
    name: 'Weather Sub-Agent',
    description: 'Provides real-time weather updates and hyper-local forecasts.',
    status: 'ONLINE',
    icon: <CloudSun className="w-6 h-6" />,
    color: 'bg-sky-100 text-sky-600 dark:bg-sky-500/20 dark:text-sky-400',
    lastActive: '10 mins ago',
    capabilities: ['Hyper-local forecasts', 'Activity planning', 'UV monitoring'],
    currentTasks: []
  },
  {
    id: '8',
    name: 'Clipboard Sub-Agent',
    description: 'Manages clipboard history, search option, media independent',
    status: 'ONLINE',
    icon: <Clipboard className="w-6 h-6" />,
    color: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-400',
    lastActive: 'Just now',
    capabilities: ['history tracking', 'media', 'search'],
    currentTasks: []
  },
  {
    id: '9',
    name: 'Music Sub-Agent',
    description: 'Suggests songs based on mood, activity, or request.',
    status: 'ONLINE',
    icon: <Music className="w-6 h-6" />,
    color: 'bg-pink-100 text-pink-600 dark:bg-pink-500/20 dark:text-pink-400',
    lastActive: 'Just now',
    capabilities: ['Song suggestions', 'Mood-based music', 'YouTube links'],
    currentTasks: []
  }
];

const RECENT_ACTIVITY: ActivityItem[] = [
  { id: '1', task: 'Synced "Morning Workout" alarm', agent: 'Alarm Sub-Agent', time: '2 mins ago', output: 'Successfully synchronized 3 alarms across 2 devices.' },
  { id: '2', task: 'Summarized "Project Update" thread', agent: 'Email Sub-Agent', time: '5 mins ago', output: 'Summary: Project is 80% complete. Next milestone is Friday.' },
  { id: '3', task: 'Summarized "Family Trip" group', agent: 'WhatsApp Sub-Agent', time: '12 mins ago', output: 'Key points: Destination confirmed as Hawaii. Budget approved.' },
  { id: '6', task: 'Synced clipboard history', agent: 'Clipboard Sub-Agent', time: 'Just now', output: 'Synced 12 new snippets to cloud storage.' }
];


// ─── Toast Component ──────────────────────────────────────────────────────────
function ToastNotification({ toasts, onRemove }: { toasts: ToastItem[]; onRemove: (id: string) => void }) {
  return (
    <div className="fixed top-6 right-6 z-[200] flex flex-col gap-3 pointer-events-none">
      {toasts.map(toast => (
        <div
          key={toast.id}
          className={`flex items-center gap-3 px-5 py-4 rounded-2xl shadow-2xl border backdrop-blur-md pointer-events-auto
            animate-in slide-in-from-right-4 fade-in duration-300
            ${toast.type === 'success' ? 'bg-emerald-50 dark:bg-emerald-950/80 border-emerald-200 dark:border-emerald-700 text-emerald-800 dark:text-emerald-200' :
              toast.type === 'error' ? 'bg-red-50 dark:bg-red-950/80 border-red-200 dark:border-red-700 text-red-800 dark:text-red-200' :
              'bg-blue-50 dark:bg-blue-950/80 border-blue-200 dark:border-blue-700 text-blue-800 dark:text-blue-200'}
          `}
        >
          <span className="text-xl">
            {toast.type === 'success' ? '✅' : toast.type === 'error' ? '❌' : 'ℹ️'}
          </span>
          <span className="text-sm font-semibold">{toast.message}</span>
          <button
            onClick={() => onRemove(toast.id)}
            className="ml-2 opacity-50 hover:opacity-100 transition-opacity"
          >
            <XCircle className="w-4 h-4" />
          </button>
        </div>
      ))}
    </div>
  );
}


export default function App() {
  const [command, setCommand] = useState('');
  const [activeTab, setActiveTab] = useState('Commander');
  const [selectedAgent, setSelectedAgent] = useState<SubAgent | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isDeleteMode, setIsDeleteMode] = useState(false);
  const [agentSearchQuery, setAgentSearchQuery] = useState('');
  const [clipboardSearchQuery, setClipboardSearchQuery] = useState('');
  const [agents, setAgents] = useState<SubAgent[]>(SUB_AGENTS_DATA);
  const [activities, setActivities] = useState<ActivityItem[]>(RECENT_ACTIVITY);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const [lastResponse, setLastResponse] = useState<string | null>(null);
  const [lastOutput, setLastOutput] = useState<ActivityItem | null>(null);

  // ── Music Sub-Agent state ────────────────────────────────────────────────────
  const [musicMood, setMusicMood] = useState('');
  const [musicActivity, setMusicActivity] = useState('');
  const [musicCount, setMusicCount] = useState<number>(3);

  // ── Toast system ────────────────────────────────────────────────────────────
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const showToast = (message: string, type: ToastItem['type'] = 'info', duration = 4000) => {
    const id = Date.now().toString();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), duration);
  };

  const removeToast = (id: string) => setToasts(prev => prev.filter(t => t.id !== id));

  // Clipboard Monitor State
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [clipboardItems, setClipboardItems] = useState<ClipboardItem[]>([
    { id: '1', type: 'link', content: 'https://github.com/luffy-ai/dashboard', time: '2 mins ago' },
    { id: '2', type: 'text', content: 'npm install lucide-react framer-motion', time: '15 mins ago' },
    { id: '3', type: 'image', content: 'Design_Mockup_v2.png', time: '1 hour ago', preview: 'https://picsum.photos/seed/design/400/300' },
    { id: '4', type: 'text', content: 'Meeting notes: Focus on sub-agent scalability.', time: '3 hours ago' },
    { id: '5', type: 'image', content: 'Architecture_Diagram.jpg', time: '5 hours ago', preview: 'https://picsum.photos/seed/tech/400/300' },
    { id: '6', type: 'image', content: 'Profile_Avatar_Draft.png', time: '1 day ago', preview: 'https://picsum.photos/seed/avatar/400/300' },
  ]);
  const [clipboardMonitorSearch, setClipboardMonitorSearch] = useState('');
  const [previewItem, setPreviewItem] = useState<ClipboardItem | null>(null);

  const lastClipboardText = useRef('');

  // ── Alarm state ─────────────────────────────────────────────────────────────
  interface AlarmItem {
    id: string;
    label: string;
    time: string;
    status: 'active' | 'ringing' | 'snoozed' | 'done';
    snoozed_until: string | null;
  }
  const [alarms, setAlarms] = React.useState<AlarmItem[]>([]);
  const [ringingAlarm, setRingingAlarm] = React.useState<AlarmItem | null>(null);
  const seenRingingIds = useRef<Set<string>>(new Set());

  // ── FIXED: Alarm polling every 5 seconds ──────────────────────────────────
  useEffect(() => {
    const playBeep = () => {
      try {
        const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
        const playTone = (freq: number, startTime: number, duration: number) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.frequency.value = freq;
          osc.type = 'sine';
          gain.gain.setValueAtTime(0, startTime);
          gain.gain.linearRampToValueAtTime(0.4, startTime + 0.05);
          gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
          osc.start(startTime);
          osc.stop(startTime + duration);
        };
        // Three-beep pattern
        playTone(880, ctx.currentTime, 0.4);
        playTone(880, ctx.currentTime + 0.5, 0.4);
        playTone(1100, ctx.currentTime + 1.0, 0.6);
      } catch {
        // Web Audio not available, skip sound
      }
    };

    const poll = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/alarms');
        if (!res.ok) return;
        const data = await res.json();
        const allAlarms: AlarmItem[] = data.alarms || [];
        setAlarms(allAlarms);

        const ringing = allAlarms.find(
          a => a.status === 'ringing' && !seenRingingIds.current.has(a.id)
        );
        if (ringing) {
          seenRingingIds.current.add(ringing.id);
          setRingingAlarm(ringing);
          playBeep();
        }
      } catch {
        // Backend unreachable, silently fail
      }
    };

    poll(); // run immediately on mount
    const interval = setInterval(poll, 5000);
    return () => clearInterval(interval);
  }, []);

  const snoozeAlarm = async (id: string, minutes = 5) => {
    try {
      await fetch(`http://127.0.0.1:8000/alarms/${id}/snooze?minutes=${minutes}`, { method: 'POST' });
      setRingingAlarm(null);
      seenRingingIds.current.delete(id); // allow re-trigger after snooze expires
      showToast(`Alarm snoozed for ${minutes} minutes`, 'info');
    } catch {
      showToast('Could not snooze alarm — backend unreachable', 'error');
    }
  };

  const dismissAlarm = async (id: string) => {
    try {
      await fetch(`http://127.0.0.1:8000/alarms/${id}/dismiss`, { method: 'POST' });
      setRingingAlarm(null);
      showToast('Alarm dismissed', 'success');
    } catch {
      showToast('Could not dismiss alarm — backend unreachable', 'error');
    }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isMonitoring) {
      interval = setInterval(async () => {
        try {
          if (!document.hasFocus()) return;

          const text = await navigator.clipboard.readText();
          if (text && text !== lastClipboardText.current) {
            const isDuplicate = clipboardItems.some(item => item.content === text);
            if (!isDuplicate) {
              lastClipboardText.current = text;
              
              const newItem: ClipboardItem = {
                id: Date.now().toString(),
                type: text.startsWith('http') ? 'link' : 'text',
                content: text,
                time: 'Just now'
              };
              
              setClipboardItems(prev => [newItem, ...prev]);
              
              const newActivity: ActivityItem = {
                id: Date.now().toString(),
                task: `Captured new ${newItem.type} from clipboard`,
                agent: 'Clipboard Sub-Agent',
                time: 'Just now',
                output: text.length > 50 ? text.substring(0, 50) + '...' : text
              };
              setActivities(prev => [newActivity, ...prev]);
            }
          }
        } catch (err) {
          // Silently fail
        }
      }, 1500);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isMonitoring, clipboardItems]);

  const deleteAgent = (id: string) => {
    setAgents(agents.filter(agent => agent.id !== id));
  };

  const handleCommand = async () => {
    if (!command.trim() || isProcessing) return;

    setIsProcessing(true);
    setLastResponse(null);
    setProcessingStatus('Sending to Nova...');

    const userCommand = command;
    setCommand('');

    try {
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userCommand }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const data: { response: string; agent: string } = await res.json();

      setProcessingStatus(`Handled by ${data.agent}`);
      setLastResponse(data.response);

      const newActivity: ActivityItem = {
        id: Date.now().toString(),
        task: userCommand,
        agent: data.agent || 'Nova',
        time: 'Just now',
        output: data.response,
      };

      setActivities(prev => [newActivity, ...prev]);
      setLastOutput(newActivity);

      if (data.agent?.toLowerCase().includes('alarm') || userCommand.toLowerCase().includes('alarm') || userCommand.toLowerCase().includes('remind')) {
        showToast(`${data.response.substring(0, 80)}`, 'success', 6000);
      } else {
        showToast(`${data.agent} responded`, 'success', 3000);
      }

    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      setLastResponse(`Could not reach Nova backend: ${msg}. Make sure uvicorn is running on port 8000.`);
      setProcessingStatus('Error');
      showToast('Could not reach Nova backend', 'error');
    }

    setIsProcessing(false);
    setProcessingStatus('');
  };

  // ── Music Sub-Agent handler ──────────────────────────────────────────────────
  const handleMusicRequest = async () => {
    const parts: string[] = [];
    if (musicMood.trim()) parts.push(musicMood.trim());
    if (musicActivity.trim()) parts.push(`songs for ${musicActivity.trim()}`);
    parts.push(String(musicCount));

    const query = parts.join(' ') || `suggest ${musicCount} songs`;

    setSelectedAgent(null);
    setActiveTab('Commander');
    setIsProcessing(true);
    setProcessingStatus('Music Sub-Agent thinking...');

    const userActivity: ActivityItem = {
      id: Date.now().toString(),
      task: query,
      agent: 'Music Sub-Agent',
      time: 'Just now',
    };
    setActivities(prev => [userActivity, ...prev]);

    try {
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const data: { response: string } = await res.json();

      const responseActivity: ActivityItem = {
        id: (Date.now() + 1).toString(),
        task: query,
        agent: 'Music Sub-Agent',
        time: 'Just now',
        output: data.response,
      };

      setActivities(prev => [responseActivity, ...prev.slice(1)]);
      setLastOutput(responseActivity);
      showToast('Music suggestions ready!', 'success', 4000);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      const errorActivity: ActivityItem = {
        id: (Date.now() + 1).toString(),
        task: query,
        agent: 'Music Sub-Agent',
        time: 'Just now',
        output: `Could not reach Music backend: ${msg}.`,
      };
      setActivities(prev => [errorActivity, ...prev.slice(1)]);
      setLastOutput(errorActivity);
      showToast('Music Sub-Agent unreachable', 'error');
    }

    setIsProcessing(false);
    setProcessingStatus('');
  };

  const [logFilter, setLogFilter] = useState<'ALL' | 'INFO' | 'SUCCESS' | 'ERROR'>('ALL');

  // Form state for new agent
  const [newAgent, setNewAgent] = useState({
    name: '',
    description: '',
    icon: 'BrainCircuit',
    color: 'bg-blue-100 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400',
    capabilities: '',
    currentTasks: ''
  });

  const iconMap: Record<string, React.ReactNode> = {
    BrainCircuit: <BrainCircuit className="w-6 h-6" />,
    AlarmClock: <AlarmClock className="w-6 h-6" />,
    Mail: <Mail className="w-6 h-6" />,
    MessageCircle: <MessageCircle className="w-6 h-6" />,
    CloudSun: <CloudSun className="w-6 h-6" />,
    Shield: <Shield className="w-6 h-6" />,
    Smartphone: <Smartphone className="w-6 h-6" />,
    Zap: <Zap className="w-6 h-6" />,
    Clipboard: <Clipboard className="w-6 h-6" />,
    Music: <Music className="w-6 h-6" />
  };

  const colorOptions = [
    { label: 'Blue', value: 'bg-blue-100 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400' },
    { label: 'Teal', value: 'bg-teal-100 text-teal-600 dark:bg-teal-500/20 dark:text-teal-400' },
    { label: 'Indigo', value: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-400' },
    { label: 'Slate', value: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400' },
    { label: 'Red', value: 'bg-red-100 text-red-600 dark:bg-red-500/20 dark:text-red-400' },
    { label: 'Emerald', value: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400' },
    { label: 'Amber', value: 'bg-amber-100 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400' },
    { label: 'Pink', value: 'bg-pink-100 text-pink-600 dark:bg-pink-500/20 dark:text-pink-400' }
  ];

  const filteredAgents = agents.filter(agent => 
    agent.name.toLowerCase().includes(agentSearchQuery.toLowerCase()) ||
    agent.status.toLowerCase().includes(agentSearchQuery.toLowerCase())
  );

  const handleAddAgent = (e: React.FormEvent) => {
    e.preventDefault();
    const id = (agents.length + 1).toString();
    const agentToAdd: SubAgent = {
      id,
      name: newAgent.name,
      description: newAgent.description,
      status: 'ONLINE',
      icon: iconMap[newAgent.icon],
      color: newAgent.color,
      lastActive: 'Just now',
      capabilities: newAgent.capabilities.split(',').map(s => s.trim()).filter(Boolean),
      currentTasks: newAgent.currentTasks.split(',').map(s => s.trim()).filter(Boolean).map((task, idx) => ({ 
        id: `${id}-${idx}`,
        name: task, 
        priority: 'MEDIUM',
        status: 'IN PROGRESS'
      }))
    };
    setAgents([...agents, agentToAdd]);
    setIsAddModalOpen(false);
    setNewAgent({
      name: '',
      description: '',
      icon: 'BrainCircuit',
      color: 'bg-blue-100 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400',
      capabilities: '',
      currentTasks: ''
    });
    showToast(`${agentToAdd.name} deployed!`, 'success');
  };


  return (
    <div className="flex h-screen overflow-hidden bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 transition-colors duration-300">

      {/* Toast Notifications */}
      <ToastNotification toasts={toasts} onRemove={removeToast} />

      {/* Sidebar */}
      <aside className="w-64 bg-card-light dark:bg-card-dark border-r border-slate-200 dark:border-slate-800 flex flex-col transition-colors duration-300">
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center text-white shadow-lg overflow-hidden border border-slate-800">
            <img 
              src="https://image2url.com/r2/default/images/1775754613385-f5e949d0-8616-47b5-bc54-4a5dcc730f10.png" 
              alt="NOVA Logo" 
              className="w-full h-full object-cover"
              referrerPolicy="no-referrer"
            />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-slate-800 dark:text-white leading-tight font-sans">
            NOVA
          </h1>
        </div>

        <nav className="flex-1 px-4 space-y-1 mt-4">
          <SidebarLink 
            icon={<Terminal className="w-5 h-5" />} 
            label="Commander" 
            active={activeTab === 'Commander'} 
            onClick={() => setActiveTab('Commander')}
          />
          <SidebarLink 
            icon={<History className="w-5 h-5" />} 
            label="Monitor" 
            active={activeTab === 'Monitor'} 
            onClick={() => setActiveTab('Monitor')}
          />
          <SidebarLink 
            icon={<LayoutGrid className="w-5 h-5" />} 
            label="Sub-Agents" 
            active={activeTab === 'Sub-Agents'} 
            onClick={() => setActiveTab('Sub-Agents')}
          />
          <SidebarLink 
            icon={<CheckCircle2 className="w-5 h-5" />} 
            label="Goals" 
            active={activeTab === 'Goals'} 
            onClick={() => setActiveTab('Goals')}
          />
        </nav>

        {/* Active alarms mini-panel in sidebar */}
        {alarms.filter(a => a.status === 'active' || a.status === 'snoozed').length > 0 && (
          <div className="mx-4 mb-4 p-3 bg-blue-50 dark:bg-blue-500/10 rounded-xl border border-blue-100 dark:border-blue-500/20">
            <p className="text-[10px] font-bold text-blue-500 uppercase tracking-wider mb-2 flex items-center gap-1">
              <BellRing className="w-3 h-3" /> Active Alarms
            </p>
            {alarms.filter(a => a.status === 'active' || a.status === 'snoozed').map(alarm => (
              <div key={alarm.id} className="flex items-center justify-between py-1">
                <div>
                  <p className="text-xs font-semibold text-slate-700 dark:text-slate-200">{alarm.label}</p>
                  <p className="text-[10px] text-slate-400">{alarm.time} · {alarm.status}</p>
                </div>
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                  alarm.status === 'snoozed' ? 'bg-amber-100 text-amber-600' : 'bg-emerald-100 text-emerald-600'
                }`}>
                  {alarm.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden flex flex-col">
        {/* Header */}
        <header className="h-16 flex items-center justify-between px-8 bg-card-light/80 dark:bg-card-dark/80 backdrop-blur-md sticky top-0 z-10 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 dark:bg-emerald-500/10 rounded-full border border-emerald-100 dark:border-emerald-500/20">
              <span className="w-2 h-2 bg-emerald-500 rounded-full"></span>
              <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">
                Main Agent Online
              </span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {ringingAlarm && (
              <button
                onClick={() => setActiveTab('Commander')}
                className="flex items-center gap-2 px-3 py-1.5 bg-red-50 dark:bg-red-500/10 rounded-full border border-red-200 dark:border-red-500/30 animate-pulse"
              >
                <BellRing className="w-4 h-4 text-red-500" />
                <span className="text-xs font-bold text-red-600 dark:text-red-400">ALARM RINGING</span>
              </button>
            )}
          </div>
        </header>

        <div className="p-8 space-y-8 max-w-6xl mx-auto w-full flex-1 flex flex-col overflow-hidden">
          {activeTab === 'Commander' ? (
            <div className="space-y-8 overflow-y-auto scrollbar-hide flex-1">
              {/* Commander Section */}
              <section className="bg-card-light dark:bg-card-dark rounded-3xl shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-800 p-10 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-10">
                  <img 
                    src="https://image2url.com/r2/default/images/1775754613385-f5e949d0-8616-47b5-bc54-4a5dcc730f10.png" 
                    alt="NOVA Logo" 
                    className="w-[120px] h-[120px] object-contain grayscale opacity-20"
                    referrerPolicy="no-referrer"
                  />
                </div>
                
                <div className="flex flex-col items-center text-center space-y-8 relative z-10">
                  <div className="space-y-4">
                    <div className="w-24 h-24 bg-slate-900 rounded-full flex items-center justify-center mx-auto overflow-hidden border-2 border-primary/20 shadow-xl">
                      <img 
                        src="https://image2url.com/r2/default/images/1775754613385-f5e949d0-8616-47b5-bc54-4a5dcc730f10.png" 
                        alt="NOVA Logo" 
                        className="w-full h-full object-cover"
                        referrerPolicy="no-referrer"
                      />
                    </div>
                    <div>
                      <h2 className="text-3xl font-bold text-slate-800 dark:text-white uppercase tracking-tight font-serif">NOVA</h2>
                    </div>
                  </div>

                  <div className="w-full max-w-2xl relative">
                    <div className="relative group">
                      <input 
                        disabled={isProcessing}
                        className={`w-full bg-slate-50 dark:bg-slate-900 border-2 rounded-2xl px-6 py-5 pl-14 text-lg transition-all placeholder:text-slate-400 outline-none disabled:opacity-50 ${
                          isProcessing 
                            ? 'border-primary shadow-[0_0_15px_rgba(37,171,188,0.2)]' 
                            : 'border-slate-100 dark:border-slate-800 focus:ring-4 focus:ring-primary/10 focus:border-primary'
                        }`} 
                        placeholder={isProcessing ? processingStatus : "Initiate a command or ask NOVA..."} 
                        type="text"
                        value={command}
                        onChange={(e) => setCommand(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleCommand()}
                      />
                      <Zap className={`absolute left-5 top-1/2 -translate-y-1/2 group-focus-within:text-primary transition-colors w-6 h-6 ${isProcessing ? 'text-primary animate-pulse' : 'text-slate-400'}`} />
                      
                      <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
                        <button 
                          onClick={handleCommand}
                          disabled={isProcessing}
                          className="bg-primary text-white p-3 rounded-xl shadow-lg shadow-primary/30 hover:bg-primary/90 transition-all flex items-center justify-center disabled:opacity-50 disabled:shadow-none"
                        >
                          {isProcessing ? <RefreshCw className="w-5 h-5 animate-spin" /> : <ArrowRight className="w-5 h-5" />}
                        </button>
                      </div>
                    </div>

                    {lastOutput && (
                      <div className="mt-6 w-full text-left bg-slate-900 rounded-2xl border border-slate-800 shadow-2xl overflow-hidden group animate-in fade-in slide-in-from-top-4 duration-500">
                        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-900/50">
                          <div className="flex items-center gap-2">
                            <div className="flex gap-1.5">
                              <div className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
                              <div className="w-2.5 h-2.5 rounded-full bg-amber-500/50" />
                              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/50" />
                            </div>
                            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-2">System Output</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-[10px] font-mono text-slate-600">{lastOutput.agent}</span>
                            <button 
                              onClick={() => { navigator.clipboard.writeText(lastOutput.output || ''); }}
                              className="p-1.5 text-slate-500 hover:text-primary transition-colors"
                              title="Copy output"
                            >
                              <Copy className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                        <div className="p-5 font-mono text-sm space-y-3">
                          <div className="flex gap-2">
                            <span className="text-emerald-500 shrink-0">$</span>
                            <span className="text-slate-300 break-all">{lastOutput.task}</span>
                          </div>
                          <div className="text-slate-400 pl-4 border-l border-slate-800 ml-1 py-1 leading-relaxed whitespace-pre-line">
                            {lastOutput.output}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </section>

              {/* NOVA Terminal Section */}
              <div className="bg-slate-900 rounded-3xl border border-slate-800 shadow-2xl overflow-hidden">
                <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1.5">
                      <div className="w-3 h-3 rounded-full bg-red-500/50" />
                      <div className="w-3 h-3 rounded-full bg-amber-500/50" />
                      <div className="w-3 h-3 rounded-full bg-emerald-500/50" />
                    </div>
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-widest ml-2">NOVA Terminal</span>
                  </div>
                </div>
                <div className="p-8 font-mono text-sm space-y-8 max-h-[600px] overflow-y-auto scrollbar-hide">
                  {activities.map((activity) => (
                    <div key={activity.id} className="space-y-3 group">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="text-emerald-500 font-bold">➜</span>
                          <span className="text-slate-500 text-xs">[{activity.time}]</span>
                          <span className="text-primary font-bold">{activity.agent}</span>
                        </div>
                        {activity.output && (
                          <button 
                            onClick={() => { navigator.clipboard.writeText(activity.output || ''); }}
                            className="opacity-0 group-hover:opacity-100 p-1.5 text-slate-500 hover:text-primary transition-all"
                            title="Copy output"
                          >
                            <Copy className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                      <div className="flex gap-3 pl-6">
                        <span className="text-slate-500">input:</span>
                        <span className="text-slate-300 break-all">{activity.task}</span>
                      </div>
                      {activity.output && (
                        <div className="flex gap-3 pl-6">
                          <span className="text-slate-500 shrink-0">output:</span>
                          <span className="text-slate-400 leading-relaxed whitespace-pre-line">{activity.output}</span>
                        </div>
                      )}
                    </div>
                  ))}
                  <div className="flex items-center gap-3 animate-pulse">
                    <span className="text-emerald-500 font-bold">➜</span>
                    <span className="w-2 h-4 bg-primary/50" />
                  </div>
                </div>
              </div>
            </div>
          ) : activeTab === 'Monitor' ? (
            <div className="space-y-8 flex-1 flex flex-col overflow-hidden">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-slate-50/50 dark:bg-slate-800/20 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 backdrop-blur-sm">
                <div>
                  <h2 className="text-2xl font-bold text-slate-800 dark:text-white">System Monitor</h2>
                  <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">Real-time clipboard tracking and system status.</p>
                </div>
                <div className="flex items-center gap-3">
                  <button 
                    onClick={() => setIsMonitoring(!isMonitoring)}
                    className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center gap-2 shadow-lg ${
                      isMonitoring 
                        ? 'bg-red-500 text-white shadow-red-500/20 hover:bg-red-600' 
                        : 'bg-emerald-500 text-white shadow-emerald-500/20 hover:bg-emerald-600'
                    }`}
                  >
                    {isMonitoring ? <Square className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current" />}
                    {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
                  </button>
                  <button 
                    onClick={() => setClipboardItems([])}
                    className="px-6 py-2.5 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 rounded-xl text-sm font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition-all flex items-center gap-2 border border-slate-200 dark:border-slate-800 shadow-sm"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Reset History
                  </button>
                </div>
              </div>

              {/* Clipboard Monitor Section */}
              <div className="bg-card-light dark:bg-card-dark rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl overflow-hidden flex-1 flex flex-col">
                <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-indigo-500/10 rounded-xl flex items-center justify-center text-indigo-500">
                      <Clipboard className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold">Clipboard Monitor</h3>
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${isMonitoring ? 'bg-emerald-500 animate-pulse' : 'bg-slate-300'}`} />
                        <span className="text-xs text-slate-500 font-medium">{isMonitoring ? 'Monitoring Active' : 'Monitoring Paused'}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 flex-1 max-w-md">
                    <div className="flex-1 relative group">
                      <input 
                        type="text"
                        placeholder="Search clipboard history..."
                        value={clipboardMonitorSearch}
                        onChange={(e) => setClipboardMonitorSearch(e.target.value)}
                        className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2.5 pl-10 pr-10 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all group-hover:border-slate-300 dark:group-hover:border-slate-700"
                      />
                      <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-primary transition-colors" />
                      {clipboardMonitorSearch && (
                        <button 
                          onClick={() => setClipboardMonitorSearch('')}
                          className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-red-500 transition-colors"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                <div className="divide-y divide-slate-100 dark:divide-slate-800 flex-1 overflow-y-auto scrollbar-hide">
                  {clipboardItems.filter(item => 
                    item.content.toLowerCase().includes(clipboardMonitorSearch.toLowerCase())
                  ).length > 0 ? (
                    clipboardItems
                      .filter(item => item.content.toLowerCase().includes(clipboardMonitorSearch.toLowerCase()))
                      .map((item) => (
                        <div key={item.id} className="p-6 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors group">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex gap-4 flex-1 min-w-0">
                              <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 ${
                                item.type === 'image' ? 'bg-purple-500/10 text-purple-500' :
                                item.type === 'link' ? 'bg-blue-500/10 text-blue-500' :
                                'bg-slate-500/10 text-slate-500'
                              }`}>
                                {item.type === 'image' ? <ImageIcon className="w-6 h-6" /> :
                                 item.type === 'link' ? <LinkIcon className="w-6 h-6" /> :
                                 <FileText className="w-6 h-6" />}
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">{item.type}</span>
                                  <span className="text-[10px] text-slate-400">•</span>
                                  <span className="text-[10px] text-slate-400">{item.time}</span>
                                </div>
                                <p className="text-sm font-mono text-slate-700 dark:text-slate-300 break-all line-clamp-2">
                                  {item.content}
                                </p>
                                {item.preview && (
                                  <div className="mt-4 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 max-w-xs">
                                    <img src={item.preview} alt="Preview" className="w-full h-auto" referrerPolicy="no-referrer" />
                                  </div>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                              <button 
                                onClick={() => { navigator.clipboard.writeText(item.content); }}
                                className="p-2 text-slate-400 hover:text-primary hover:bg-primary/10 rounded-lg transition-all"
                                title="Copy to clipboard"
                              >
                                <Copy className="w-4 h-4" />
                              </button>
                              <button 
                                onClick={() => setPreviewItem(item)}
                                className="p-2 text-slate-400 hover:text-blue-500 hover:bg-blue-500/10 rounded-lg transition-all"
                                title="Preview"
                              >
                                <Eye className="w-4 h-4" />
                              </button>
                              <button 
                                onClick={() => setClipboardItems(clipboardItems.filter(i => i.id !== item.id))}
                                className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all"
                                title="Delete"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        </div>
                      ))
                  ) : (
                    <div className="p-20 text-center">
                      <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Search className="w-8 h-8 text-slate-300" />
                      </div>
                      <p className="text-slate-500 font-medium">No items found in clipboard history</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : activeTab === 'Sub-Agents' ? (
            <div className="space-y-8 overflow-y-auto scrollbar-hide flex-1">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-slate-800 dark:text-white">Sub-Agent Registry</h2>
                  <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">Manage and monitor your specialized AI workforce.</p>
                </div>
              </div>

              <div className="relative max-w-md">
                <input 
                  type="text"
                  placeholder="Search agents by name or status..."
                  value={agentSearchQuery}
                  onChange={(e) => setAgentSearchQuery(e.target.value)}
                  className="w-full bg-card-light dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-3 pl-11 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                />
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredAgents.map((agent) => (
                  <div 
                    key={agent.id}
                    onClick={() => !isDeleteMode && setSelectedAgent(agent)}
                    className={`bg-card-light dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all relative ${
                      isDeleteMode ? 'cursor-default ring-2 ring-red-500/20' : 'cursor-pointer'
                    }`}
                  >
                    {isDeleteMode && (
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteAgent(agent.id);
                        }}
                        className="absolute top-4 right-4 p-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors shadow-lg shadow-red-500/20 z-10"
                      >
                        <XCircle className="w-4 h-4" />
                      </button>
                    )}
                    <div className="mb-4">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${agent.color}`}>
                        {agent.icon}
                      </div>
                    </div>
                    <h3 className="text-lg font-bold text-slate-800 dark:text-white">{agent.name}</h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
                      {agent.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : activeTab === 'Goals' ? (
            <GoalsPanel onSendCommand={async (msg) => {
              setActiveTab('Commander');
              setIsProcessing(true);
              try {
                const res = await fetch('http://127.0.0.1:8000/chat', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ message: msg }),
                });
                const data = await res.json();
                const newActivity: ActivityItem = {
                  id: Date.now().toString(),
                  task: msg,
                  agent: data.agent || 'GoalAgent',
                  time: 'Just now',
                  output: data.response,
                };
                setActivities(prev => [newActivity, ...prev]);
                setLastOutput(newActivity);
              } catch {}
              setIsProcessing(false);
            }} />
          ) : (
            <div className="flex flex-col items-center justify-center py-20 text-slate-400">
              <RefreshCw className="w-12 h-12 mb-4 opacity-20" />
              <p className="text-lg font-medium">Screen under construction...</p>
            </div>
          )}
        </div>

        {/* Agent Action Modal */}
        {selectedAgent && (
          <AgentActionModal
            agent={selectedAgent}
            onClose={() => setSelectedAgent(null)}
            showToast={showToast}
            musicMood={musicMood}
            musicActivity={musicActivity}
            musicCount={musicCount}
            onMusicMoodChange={setMusicMood}
            onMusicActivityChange={setMusicActivity}
            onMusicCountChange={setMusicCount}
            onMusicRequest={handleMusicRequest}
            onSend={async (message: string) => {
              setSelectedAgent(null);
              setActiveTab('Commander');
              setIsProcessing(true);
              setProcessingStatus(`Running ${selectedAgent.name}...`);
              try {
                const res = await fetch('http://127.0.0.1:8000/chat', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ message }),
                });
                const data = await res.json();
                const newActivity: ActivityItem = {
                  id: Date.now().toString(),
                  task: message,
                  agent: data.agent || selectedAgent.name,
                  time: 'Just now',
                  output: data.response,
                };
                setActivities(prev => [newActivity, ...prev]);
                setLastOutput(newActivity);

                if (selectedAgent.name.toLowerCase().includes('alarm')) {
                  showToast(`${data.response?.substring(0, 80) || 'Alarm set!'}`, 'success', 6000);
                } else {
                  showToast(`${data.agent || selectedAgent.name} task complete`, 'success', 3000);
                }
              } catch (err) {
                const msg = err instanceof Error ? err.message : 'Unknown error';
                const newActivity: ActivityItem = {
                  id: Date.now().toString(),
                  task: message,
                  agent: selectedAgent.name,
                  time: 'Just now',
                  output: `Error: ${msg}`,
                };
                setActivities(prev => [newActivity, ...prev]);
                setLastOutput(newActivity);
                showToast(`${selectedAgent.name} error: ${msg}`, 'error');
              }
              setIsProcessing(false);
              setProcessingStatus('');
            }}
          />
        )}

        {/* Add Agent Modal */}
        {isAddModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div 
              onClick={() => setIsAddModalOpen(false)}
              className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
            />
            <div className="relative w-full max-w-2xl bg-card-light dark:bg-card-dark rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
              <form onSubmit={handleAddAgent} className="p-8">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-2xl font-bold text-slate-800 dark:text-white">Create New Sub-Agent</h3>
                  <button 
                    type="button"
                    onClick={() => setIsAddModalOpen(false)}
                    className="p-2 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
                  >
                    <XCircle className="w-6 h-6" />
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Agent Name</label>
                      <input 
                        required
                        type="text"
                        value={newAgent.name}
                        onChange={(e) => setNewAgent({...newAgent, name: e.target.value})}
                        className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600"
                        placeholder="e.g. Research Assistant"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Description</label>
                      <textarea 
                        required
                        rows={3}
                        value={newAgent.description}
                        onChange={(e) => setNewAgent({...newAgent, description: e.target.value})}
                        className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all resize-none placeholder:text-slate-400 dark:placeholder:text-slate-600"
                        placeholder="What does this agent do?"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Icon</label>
                      <div className="grid grid-cols-4 gap-2">
                        {Object.keys(iconMap).map((iconName) => (
                          <button
                            key={iconName}
                            type="button"
                            onClick={() => setNewAgent({...newAgent, icon: iconName})}
                            className={`p-3 rounded-xl flex items-center justify-center transition-all ${
                              newAgent.icon === iconName 
                                ? 'bg-primary text-white shadow-lg shadow-primary/20' 
                                : 'bg-slate-100 dark:bg-slate-800 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200'
                            }`}
                          >
                            {React.cloneElement(iconMap[iconName] as React.ReactElement<{ className?: string }>, { className: 'w-5 h-5' })}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Theme Color</label>
                      <div className="grid grid-cols-2 gap-2">
                        {colorOptions.map((option) => (
                          <button
                            key={option.value}
                            type="button"
                            onClick={() => setNewAgent({...newAgent, color: option.value})}
                            className={`px-3 py-2 rounded-xl text-xs font-bold transition-all border-2 ${
                              newAgent.color === option.value 
                                ? 'border-primary' 
                                : 'border-transparent'
                            } ${option.value}`}
                          >
                            {option.label}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Capabilities (comma separated)</label>
                      <input 
                        type="text"
                        value={newAgent.capabilities}
                        onChange={(e) => setNewAgent({...newAgent, capabilities: e.target.value})}
                        className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600"
                        placeholder="e.g. Web Search, Data Analysis"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Initial Tasks (comma separated)</label>
                      <input 
                        type="text"
                        value={newAgent.currentTasks}
                        onChange={(e) => setNewAgent({...newAgent, currentTasks: e.target.value})}
                        className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600"
                        placeholder="e.g. Indexing new files"
                      />
                    </div>
                  </div>
                </div>

                <div className="mt-10 flex gap-3">
                  <button 
                    type="submit"
                    className="flex-1 bg-primary text-white py-4 rounded-xl font-bold shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all"
                  >
                    Deploy Sub-Agent
                  </button>
                  <button 
                    type="button"
                    onClick={() => setIsAddModalOpen(false)}
                    className="px-8 py-4 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-xl font-bold hover:bg-slate-200 dark:hover:bg-slate-700 transition-all"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Clipboard Preview Modal */}
        {previewItem && (
          <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div 
              onClick={() => setPreviewItem(null)}
              className="absolute inset-0 bg-slate-900/80 backdrop-blur-md"
            />
            <div className="relative w-full max-w-3xl bg-card-light dark:bg-card-dark rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden animate-in zoom-in-95 duration-200">
              <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                    previewItem.type === 'image' ? 'bg-purple-500/10 text-purple-500' :
                    previewItem.type === 'link' ? 'bg-blue-500/10 text-blue-500' :
                    'bg-slate-500/10 text-slate-500'
                  }`}>
                    {previewItem.type === 'image' ? <ImageIcon className="w-5 h-5" /> :
                     previewItem.type === 'link' ? <LinkIcon className="w-5 h-5" /> :
                     <FileText className="w-5 h-5" />}
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-800 dark:text-white">Content Preview</h3>
                    <p className="text-xs text-slate-500">{previewItem.time}</p>
                  </div>
                </div>
                <button 
                  onClick={() => setPreviewItem(null)}
                  className="p-2 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>
              <div className="p-8 overflow-y-auto max-h-[70vh]">
                {previewItem.type === 'image' && previewItem.preview ? (
                  <div className="space-y-6">
                    <div className="rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-700 shadow-lg">
                      <img src={previewItem.preview} alt="Full Preview" className="w-full h-auto" referrerPolicy="no-referrer" />
                    </div>
                    <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-100 dark:border-slate-800">
                      <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">File Name</p>
                      <p className="text-sm font-mono text-slate-700 dark:text-slate-300 break-all">{previewItem.content}</p>
                    </div>
                  </div>
                ) : (
                  <div className="p-6 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Raw Content</p>
                    <pre className="text-sm font-mono text-slate-700 dark:text-slate-300 whitespace-pre-wrap break-all leading-relaxed">
                      {previewItem.content}
                    </pre>
                  </div>
                )}
              </div>
              <div className="p-6 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/20 flex gap-3">
                <button 
                  onClick={() => {
                    navigator.clipboard.writeText(previewItem.content);
                    setPreviewItem(null);
                  }}
                  className="flex-1 bg-primary text-white py-3 rounded-xl font-bold shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all flex items-center justify-center gap-2"
                >
                  <Copy className="w-4 h-4" />
                  Copy to Clipboard
                </button>
                <button 
                  onClick={() => setPreviewItem(null)}
                  className="px-8 py-3 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-xl font-bold hover:bg-slate-200 dark:hover:bg-slate-700 transition-all"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* ════════════════════════════════════════════════════════════════════════
          FIXED ALARM RINGING POPUP - Full screen overlay with animations
          ════════════════════════════════════════════════════════════════════════ */}
      {ringingAlarm && (
        <>
          {/* Keyframe styles */}
          <style>{`
            @keyframes alarmRingPulse {
              0%   { transform: scale(1);    opacity: 0.6; }
              50%  { transform: scale(1.12); opacity: 0.15; }
              100% { transform: scale(1),    opacity: 0.6; }
            }
            @keyframes alarmBellShake {
              0%, 100% { transform: rotate(-12deg) scale(1.05); }
              25%       { transform: rotate( 12deg) scale(1.05); }
              50%       { transform: rotate(-8deg)  scale(1.05); }
              75%       { transform: rotate(  8deg) scale(1.05); }
            }
            @keyframes alarmSlideUp {
              from { transform: translateY(40px); opacity: 0; }
              to   { transform: translateY(0);    opacity: 1; }
            }
          `}</style>

          {/* Blurred backdrop */}
          <div style={{
            position: 'fixed', inset: 0, zIndex: 9998,
            background: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(12px)',
          }} />

          {/* Pulsing rings (decorative, behind card) */}
          <div style={{
            position: 'fixed', inset: 0, zIndex: 9999,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            pointerEvents: 'none',
          }}>
            {[500, 400, 300].map((size, i) => (
              <div key={size} style={{
                position: 'absolute',
                width: size, height: size,
                borderRadius: '50%',
                border: '2px solid rgba(99,102,241,0.3)',
                animation: `alarmRingPulse 2s ease-out infinite ${i * 0.35}s`,
              }} />
            ))}
          </div>

          {/* Alarm card */}
          <div style={{
            position: 'fixed', inset: 0, zIndex: 10000,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            padding: '1rem',
          }}>
            <div style={{
              background: 'white',
              borderRadius: 32,
              padding: '48px 40px 44px',
              textAlign: 'center',
              width: '100%',
              maxWidth: 400,
              boxShadow: '0 40px 100px rgba(0,0,0,0.5), 0 0 0 1.5px rgba(99,102,241,0.25)',
              animation: 'alarmSlideUp 0.4s cubic-bezier(0.34,1.56,0.64,1)',
            }}
            className="dark:bg-slate-900"
            >
              {/* Bell icon with shake animation */}
              <div style={{
                width: 88, height: 88,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #6366f1 0%, #4338ca 100%)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 24px',
                boxShadow: '0 16px 40px rgba(99,102,241,0.5)',
                animation: 'alarmBellShake 0.6s ease-in-out infinite',
                fontSize: 40,
              }}>
                ⏰
              </div>

              {/* Label */}
              <p style={{
                fontSize: 11, fontWeight: 700,
                letterSpacing: '0.15em',
                color: '#6366f1',
                textTransform: 'uppercase',
                marginBottom: 10,
              }}>
                Alarm
              </p>

              {/* Alarm name */}
              <h2 style={{
                fontSize: 30, fontWeight: 800,
                color: '#0f172a',
                margin: '0 0 8px',
                letterSpacing: '-0.5px',
                lineHeight: 1.2,
              }}
              className="dark:text-white"
              >
                {ringingAlarm.label}
              </h2>

              {/* Time */}
              <p style={{
                fontSize: 16,
                color: '#64748b',
                marginBottom: 36,
                fontWeight: 500,
              }}>
                {ringingAlarm.time}
              </p>

              {/* Snooze row */}
              <p style={{
                fontSize: 11, fontWeight: 700, color: '#94a3b8',
                textTransform: 'uppercase', letterSpacing: '0.1em',
                marginBottom: 10,
              }}>
                Snooze for
              </p>
              <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
                {[5, 10, 15].map((mins) => (
                  <button
                    key={mins}
                    onClick={() => snoozeAlarm(ringingAlarm.id, mins)}
                    style={{
                      flex: 1, padding: '13px 0',
                      borderRadius: 14,
                      border: '1.5px solid #e2e8f0',
                      background: '#f8fafc',
                      fontSize: 14, fontWeight: 700,
                      cursor: 'pointer', color: '#334155',
                      transition: 'all 0.15s ease',
                    }}
                    onMouseEnter={e => {
                      const el = e.currentTarget;
                      el.style.background = '#eef2ff';
                      el.style.borderColor = '#6366f1';
                      el.style.color = '#4338ca';
                      el.style.transform = 'translateY(-2px)';
                    }}
                    onMouseLeave={e => {
                      const el = e.currentTarget;
                      el.style.background = '#f8fafc';
                      el.style.borderColor = '#e2e8f0';
                      el.style.color = '#334155';
                      el.style.transform = 'translateY(0)';
                    }}
                    className="dark:bg-slate-800 dark:border-slate-700 dark:text-slate-200"
                  >
                     {mins} min
                  </button>
                ))}
              </div>

              {/* Dismiss button */}
              <button
                onClick={() => dismissAlarm(ringingAlarm.id)}
                style={{
                  width: '100%',
                  padding: '18px 0',
                  borderRadius: 16,
                  border: 'none',
                  background: 'linear-gradient(135deg, #6366f1 0%, #4338ca 100%)',
                  fontSize: 17, fontWeight: 800,
                  cursor: 'pointer', color: 'white',
                  boxShadow: '0 10px 30px rgba(99,102,241,0.45)',
                  transition: 'all 0.15s ease',
                  letterSpacing: '0.01em',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 16px 40px rgba(99,102,241,0.55)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 10px 30px rgba(99,102,241,0.45)';
                }}
              >
                ✓  Dismiss Alarm
              </button>
            </div>
          </div>
        </>
      )}

    </div>
  );
}

// ─── Agent Action Modal ────────────────────────────────────────────────────────

// ── Goals Panel ───────────────────────────────────────────────────────────────
interface Goal { goal: string; target: number; done: number; date: string; }

function GoalsPanel({ onSendCommand }: { onSendCommand: (msg: string) => void }) {
  const [goals, setGoals] = React.useState<Goal[]>([]);
  const [numGoals, setNumGoals] = React.useState(0);
  const [goalInputs, setGoalInputs] = React.useState<{name: string; target: string}[]>([]);
  const [step, setStep] = React.useState<'count' | 'inputs' | 'view'>('view');
  const [doneInputs, setDoneInputs] = React.useState<Record<string, string>>({});
  const [reminder, setReminder] = React.useState('');

  const fetchGoals = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/goals');
      const data = await res.json();
      setGoals(data.goals || []);
    } catch {}
  };

  const fetchReminder = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/goals/reminder');
      const data = await res.json();
      setReminder(data.reminder || '');
    } catch {}
  };

  React.useEffect(() => {
    fetchGoals();
    fetchReminder();
  }, []);

  const handleCreateGoals = async () => {
    const payload = goalInputs
      .filter(g => g.name.trim() && g.target)
      .map(g => ({ name: g.name.trim(), target: parseInt(g.target) || 1 }));
    if (!payload.length) return;
    await fetch('http://127.0.0.1:8000/goals', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    setStep('view');
    fetchGoals();
    fetchReminder();
  };

  const handleUpdateGoal = async (name: string) => {
    const val = parseInt(doneInputs[name] || '1');
    await fetch('http://127.0.0.1:8000/goals/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify([{ name, done: val }]),
    });
    setDoneInputs(prev => ({ ...prev, [name]: '' }));
    fetchGoals();
    fetchReminder();
  };

  return (
    <div className="space-y-6 overflow-y-auto flex-1 scrollbar-hide">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white">Daily Goals</h2>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">Track your daily targets.</p>
        </div>
        <button
          onClick={() => { setStep('count'); setNumGoals(0); setGoalInputs([]); }}
          className="flex items-center gap-2 px-4 py-2.5 bg-primary text-white rounded-xl text-sm font-bold shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all"
        >
          <Plus className="w-4 h-4" /> Add Goals
        </button>
      </div>

      {reminder && reminder !== 'All goals completed for today!' && (
        <div className="p-4 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-2xl flex items-center gap-3">
          <span className="text-lg">⏰</span>
          <p className="text-sm font-medium text-amber-700 dark:text-amber-400">{reminder}</p>
        </div>
      )}
      {reminder === 'All goals completed for today!' && (
        <div className="p-4 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-2xl flex items-center gap-3">
          <span className="text-lg">🎉</span>
          <p className="text-sm font-medium text-emerald-700 dark:text-emerald-400">All goals completed for today!</p>
        </div>
      )}

      {step === 'count' && (
        <div className="bg-card-light dark:bg-card-dark rounded-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-4">
          <h3 className="font-bold text-slate-700 dark:text-white">How many goals today?</h3>
          <div className="flex gap-2">
            {[1,2,3,4,5].map(n => (
              <button key={n} onClick={() => { setNumGoals(n); setGoalInputs(Array(n).fill({name:'',target:''})); setStep('inputs'); }}
                className="w-10 h-10 rounded-xl bg-slate-100 dark:bg-slate-800 font-bold text-slate-700 dark:text-white hover:bg-primary hover:text-white transition-all">
                {n}
              </button>
            ))}
          </div>
        </div>
      )}

      {step === 'inputs' && (
        <div className="bg-card-light dark:bg-card-dark rounded-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-4">
          <h3 className="font-bold text-slate-700 dark:text-white">Set your {numGoals} goals</h3>
          {goalInputs.map((g, i) => (
            <div key={i} className="flex gap-3">
              <input
                placeholder={`Goal ${i+1} name`}
                value={g.name}
                onChange={e => {
                  const updated = [...goalInputs];
                  updated[i] = { ...updated[i], name: e.target.value };
                  setGoalInputs(updated);
                }}
                className="flex-1 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-primary dark:text-white"
              />
              <input
                placeholder="Target"
                type="number"
                min="1"
                value={g.target}
                onChange={e => {
                  const updated = [...goalInputs];
                  updated[i] = { ...updated[i], target: e.target.value };
                  setGoalInputs(updated);
                }}
                className="w-24 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-primary dark:text-white"
              />
            </div>
          ))}
          <div className="flex gap-3 pt-2">
            <button onClick={handleCreateGoals} className="flex-1 bg-primary text-white py-3 rounded-xl font-bold hover:bg-primary/90 transition-all">
              Create Goals
            </button>
            <button onClick={() => setStep('view')} className="px-6 py-3 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-xl font-bold hover:bg-slate-200 transition-all">
              Cancel
            </button>
          </div>
        </div>
      )}

      {goals.length === 0 && step === 'view' ? (
        <div className="text-center py-16">
          <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-8 h-8 text-slate-300" />
          </div>
          <p className="text-slate-500 font-medium">No goals set for today</p>
          <p className="text-slate-400 text-sm mt-1">Click "Add Goals" or type "goal: study 2, gym 1" in Commander</p>
        </div>
      ) : (
        <div className="space-y-3">
          {goals.map((g, i) => {
            const pct = Math.min(100, Math.round((g.done / g.target) * 100));
            const done = g.done >= g.target;
            return (
              <div key={i} className="bg-card-light dark:bg-card-dark rounded-2xl border border-slate-200 dark:border-slate-800 p-5">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{done ? '✅' : '🎯'}</span>
                    <div>
                      <p className="font-bold text-slate-800 dark:text-white capitalize">{g.goal}</p>
                      <p className="text-xs text-slate-500">{g.done}/{g.target} completed</p>
                    </div>
                  </div>
                  <span className={`text-sm font-bold px-3 py-1 rounded-full ${done ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400' : 'bg-amber-100 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400'}`}>
                    {done ? 'Done!' : `${g.target - g.done} left`}
                  </span>
                </div>
                <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 mb-3">
                  <div
                    className={`h-2 rounded-full transition-all ${done ? 'bg-emerald-500' : 'bg-primary'}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                {!done && (
                  <div className="flex gap-2">
                    <input
                      type="number"
                      min="1"
                      placeholder="Add done"
                      value={doneInputs[g.goal] || ''}
                      onChange={e => setDoneInputs(prev => ({ ...prev, [g.goal]: e.target.value }))}
                      className="flex-1 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-sm outline-none focus:border-primary dark:text-white"
                    />
                    <button
                      onClick={() => handleUpdateGoal(g.goal)}
                      className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-bold hover:bg-primary/90 transition-all"
                    >
                      Add
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function AgentActionModal({ agent, onClose, onSend, showToast, musicMood, musicActivity, musicCount, onMusicMoodChange, onMusicActivityChange, onMusicCountChange, onMusicRequest }: {
  agent: SubAgent;
  onClose: () => void;
  onSend: (message: string) => void;
  showToast: (msg: string, type: 'success' | 'error' | 'info', duration?: number) => void;
  musicMood: string;
  musicActivity: string;
  musicCount: number;
  onMusicMoodChange: (val: string) => void;
  onMusicActivityChange: (val: string) => void;
  onMusicCountChange: (val: number) => void;
  onMusicRequest: () => void;
}) {
  const [fields, setFields] = React.useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = React.useState(false);

  const agentType = agent.name.toLowerCase();

  const handleSubmit = async () => {
    setIsLoading(true);
    let message = '';

    if (agentType.includes('alarm')) {
      const time = fields.time || '';
      const label = fields.label || 'Alarm';
      if (!time) {
        showToast('Please select a time for the alarm', 'error');
        setIsLoading(false);
        return;
      }
      message = `set alarm for ${time} label ${label}`;
    } else if (agentType.includes('weather')) {
      if (!fields.city) {
        showToast('Please enter a city name', 'error');
        setIsLoading(false);
        return;
      }
      message = `weather in ${fields.city}`;
    } else if (agentType.includes('email')) {
      message = `send email to ${fields.to} subject ${fields.subject} message ${fields.body}`;
    } else if (agentType.includes('whatsapp')) {
      message = `send WhatsApp to ${fields.contact} saying ${fields.message}`;
    } else if (agentType.includes('clipboard')) {
      if (fields.action === 'copy') {
        message = `copy this to clipboard: ${fields.text}`;
      } else if (fields.action === 'read') {
        message = 'read my clipboard';
      } else {
        message = 'show clipboard history';
      }
    }

    if (message) {
      await onSend(message);
    }
    setIsLoading(false);
  };

  const renderFields = () => {
    if (agentType.includes('alarm')) {
      return (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Time</label>
            <input
              type="time"
              value={fields.time || ''}
              onChange={e => setFields({...fields, time: e.target.value})}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary dark:text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Label (optional)</label>
            <input
              type="text"
              placeholder="e.g. Wake up, Meeting..."
              value={fields.label || ''}
              onChange={e => setFields({...fields, label: e.target.value})}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary placeholder:text-slate-400 dark:text-white"
            />
          </div>
          <p className="text-xs text-slate-400 bg-slate-50 dark:bg-slate-800 rounded-xl px-4 py-3">
            After setting, a popup will appear on screen when the alarm rings. You can snooze or dismiss it from there.
          </p>
        </div>
      );
    }

    if (agentType.includes('weather')) {
      return (
        <div>
          <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">City</label>
          <input
            type="text"
            placeholder="e.g. Delhi, Mumbai, London..."
            value={fields.city || ''}
            onChange={e => setFields({...fields, city: e.target.value})}
            className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary placeholder:text-slate-400 dark:text-white"
          />
        </div>
      );
    }

    if (agentType.includes('email')) {
      return (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">To</label>
            <input
              type="email"
              placeholder="recipient@email.com"
              value={fields.to || ''}
              onChange={e => setFields({...fields, to: e.target.value})}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary placeholder:text-slate-400 dark:text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Subject</label>
            <input
              type="text"
              placeholder="Email subject..."
              value={fields.subject || ''}
              onChange={e => setFields({...fields, subject: e.target.value})}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary placeholder:text-slate-400 dark:text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Message</label>
            <textarea
              rows={3}
              placeholder="Write your email..."
              value={fields.body || ''}
              onChange={e => setFields({...fields, body: e.target.value})}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary placeholder:text-slate-400 dark:text-white resize-none"
            />
          </div>
        </div>
      );
    }

    if (agentType.includes('whatsapp')) {
      return (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Contact Name</label>
            <input
              type="text"
              placeholder="e.g. Abhinav, Mom, Rahul..."
              value={fields.contact || ''}
              onChange={e => setFields({...fields, contact: e.target.value})}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary placeholder:text-slate-400 dark:text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Message</label>
            <textarea
              rows={3}
              placeholder="Type your message..."
              value={fields.message || ''}
              onChange={e => setFields({...fields, message: e.target.value})}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary placeholder:text-slate-400 dark:text-white resize-none"
            />
          </div>
        </div>
      );
    }

    if (agentType.includes('clipboard')) {
      return (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Action</label>
            <div className="grid grid-cols-3 gap-2">
              {['copy', 'read', 'history'].map(a => (
                <button
                  key={a}
                  onClick={() => setFields({...fields, action: a})}
                  className={`py-2.5 rounded-xl text-sm font-bold transition-all capitalize ${
                    fields.action === a
                      ? 'bg-primary text-white'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300'
                  }`}
                >
                  {a}
                </button>
              ))}
            </div>
          </div>
          {fields.action === 'copy' && (
            <div>
              <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Text to Copy</label>
              <textarea
                rows={3}
                placeholder="Text to copy to clipboard..."
                value={fields.text || ''}
                onChange={e => setFields({...fields, text: e.target.value})}
                className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary placeholder:text-slate-400 dark:text-white resize-none"
              />
            </div>
          )}
        </div>
      );
    }

    if (agentType.includes('music')) {
      return (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Mood</label>
            <input
              type="text"
              placeholder="e.g. happy, sad, energetic, chill..."
              value={musicMood}
              onChange={e => onMusicMoodChange(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-pink-400/20 focus:border-pink-400 placeholder:text-slate-400 dark:text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Activity</label>
            <input
              type="text"
              placeholder="e.g. study, workout, sleep, drive..."
              value={musicActivity}
              onChange={e => onMusicActivityChange(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-pink-400/20 focus:border-pink-400 placeholder:text-slate-400 dark:text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">
              Number of Songs
              <span className="ml-2 font-normal text-slate-500 normal-case">(1–10)</span>
            </label>
            <input
              type="number"
              min={1}
              max={10}
              value={musicCount}
              onChange={e => onMusicCountChange(Math.min(10, Math.max(1, Number(e.target.value))))}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-pink-400/20 focus:border-pink-400 dark:text-white"
            />
          </div>
          <p className="text-xs text-slate-400 bg-pink-50 dark:bg-pink-500/10 rounded-xl px-4 py-3 border border-pink-100 dark:border-pink-500/20">
            Songs will appear in the Commander terminal with YouTube links.
          </p>
        </div>
      );
    }

    return <p className="text-slate-400 text-sm">Use the Commander tab to interact with this agent.</p>;
  };

  const isMusicAgent = agentType.includes('music');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div onClick={onClose} className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" />
      <div className="relative w-full max-w-lg bg-card-light dark:bg-card-dark rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        <div className="p-8">
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${agent.color}`}>
                {React.cloneElement(agent.icon as React.ReactElement<{ className?: string }>, { className: 'w-7 h-7' })}
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-800 dark:text-white">{agent.name}</h3>
                <p className="text-sm text-slate-500 mt-0.5">{agent.description}</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors">
              <XCircle className="w-5 h-5" />
            </button>
          </div>

          <div className="mb-6">
            {renderFields()}
          </div>

          <div className="flex gap-3">
            {isMusicAgent ? (
              <button
                onClick={onMusicRequest}
                className="flex-1 bg-gradient-to-r from-pink-500 to-rose-500 text-white py-3.5 rounded-xl font-bold shadow-lg shadow-pink-500/20 hover:from-pink-600 hover:to-rose-600 transition-all flex items-center justify-center gap-2"
              >
                <Music className="w-4 h-4" />
                Get Songs
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={isLoading}
                className="flex-1 bg-primary text-white py-3.5 rounded-xl font-bold shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                {isLoading ? 'Running...' : 'Run Agent'}
              </button>
            )}
            <button
              onClick={onClose}
              className="px-6 py-3.5 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-xl font-bold hover:bg-slate-200 dark:hover:bg-slate-700 transition-all"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Sidebar Link ─────────────────────────────────────────────────────────────
function SidebarLink({ 
  icon, 
  label, 
  active = false, 
  onClick 
}: { 
  icon: React.ReactNode, 
  label: string, 
  active?: boolean,
  onClick?: () => void
}) {
  return (
    <button 
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
        active 
          ? 'bg-primary/10 text-primary shadow-sm' 
          : 'text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'
      }`}
    >
      {icon}
      <span className="font-medium">{label}</span>
    </button>
  );
}