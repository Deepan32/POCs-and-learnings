"use client";

import React, { useState, useCallback } from "react";
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  Handle,
  Position,
} from "reactflow";
import "reactflow/dist/style.css";
import { AppShell } from "@/components/layout/AppShell";
import {
  Sparkles,
  Zap,
  Play,
  Save,
  Plus,
  ArrowRight,
  Bot,
  Headphones,
  FileText,
  Users,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Clock,
  Layers,
} from "lucide-react";
import { ApiClient } from "@/lib/api";

// Custom React Flow Nodes
function TriggerNode({ data }: { data: any }) {
  return (
    <div className="p-3.5 rounded-2xl bg-slate-900 border-2 border-emerald-500 shadow-xl shadow-emerald-500/10 w-60">
      <div className="flex items-center gap-2 mb-1">
        <div className="p-1 rounded-lg bg-emerald-500/20 text-emerald-400">
          <Zap className="w-4 h-4" />
        </div>
        <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-400">
          Trigger
        </span>
      </div>
      <p className="font-bold text-xs text-white">{data.label}</p>
      <p className="text-[10px] text-slate-400 mt-1">WHEN customer sends &ldquo;{data.keyword || "Hi"}&rdquo;</p>
      <Handle type="source" position={Position.Bottom} className="w-2.5 h-2.5 bg-emerald-500 border border-slate-950" />
    </div>
  );
}

function ConditionNode({ data }: { data: any }) {
  return (
    <div className="p-3.5 rounded-2xl bg-slate-900 border-2 border-amber-500 shadow-xl shadow-amber-500/10 w-60">
      <Handle type="target" position={Position.Top} className="w-2.5 h-2.5 bg-amber-500 border border-slate-950" />
      <div className="flex items-center gap-2 mb-1">
        <div className="p-1 rounded-lg bg-amber-500/20 text-amber-400">
          <HelpCircle className="w-4 h-4" />
        </div>
        <span className="text-[10px] uppercase font-bold tracking-wider text-amber-400">
          Condition
        </span>
      </div>
      <p className="font-bold text-xs text-white">{data.label}</p>
      <div className="flex justify-between mt-2 pt-2 border-t border-slate-800 text-[10px] text-slate-400">
        <span>Yes (New)</span>
        <span>No (Existing)</span>
      </div>
      <Handle type="source" position={Position.Bottom} id="yes" className="w-2.5 h-2.5 bg-emerald-500 left-16" />
      <Handle type="source" position={Position.Bottom} id="no" className="w-2.5 h-2.5 bg-rose-500 right-16" />
    </div>
  );
}

function ActionNode({ data }: { data: any }) {
  const isHandover = data.actionType === "HUMAN_HANDOVER";
  return (
    <div
      className={`p-3.5 rounded-2xl bg-slate-900 border-2 shadow-xl w-60 ${
        isHandover ? "border-purple-500 shadow-purple-500/10" : "border-blue-500 shadow-blue-500/10"
      }`}
    >
      <Handle type="target" position={Position.Top} className="w-2.5 h-2.5 bg-blue-500 border border-slate-950" />
      <div className="flex items-center gap-2 mb-1">
        <div
          className={`p-1 rounded-lg ${
            isHandover ? "bg-purple-500/20 text-purple-400" : "bg-blue-500/20 text-blue-400"
          }`}
        >
          {isHandover ? <Headphones className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
        </div>
        <span
          className={`text-[10px] uppercase font-bold tracking-wider ${
            isHandover ? "text-purple-400" : "text-blue-400"
          }`}
        >
          {isHandover ? "Human Handover" : "Action"}
        </span>
      </div>
      <p className="font-bold text-xs text-white">{data.label}</p>
      {data.buttons && (
        <div className="flex flex-wrap gap-1 mt-2">
          {data.buttons.map((b: string, i: number) => (
            <span key={i} className="px-1.5 py-0.5 rounded bg-slate-800 text-[9px] text-slate-300">
              [{b}]
            </span>
          ))}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} className="w-2.5 h-2.5 bg-blue-500 border border-slate-950" />
    </div>
  );
}

const nodeTypes = {
  triggerNode: TriggerNode,
  conditionNode: ConditionNode,
  actionNode: ActionNode,
};

const initialNodes: Node[] = [
  {
    id: "1",
    type: "triggerNode",
    position: { x: 250, y: 30 },
    data: { label: "Incoming Message: 'Hi'", keyword: "Hi" },
  },
  {
    id: "2",
    type: "conditionNode",
    position: { x: 250, y: 170 },
    data: { label: "Check If New Contact" },
  },
  {
    id: "3",
    type: "actionNode",
    position: { x: 80, y: 320 },
    data: {
      label: "Send Welcome Menu",
      actionType: "SEND_TEXT",
      buttons: ["Sales", "Support", "Pricing", "Talk to Human"],
    },
  },
  {
    id: "4",
    type: "actionNode",
    position: { x: 80, y: 470 },
    data: { label: "Capture Lead (+20 Score)", actionType: "CREATE_LEAD" },
  },
  {
    id: "5",
    type: "actionNode",
    position: { x: 420, y: 320 },
    data: {
      label: "Handover to Human Agent Queue",
      actionType: "HUMAN_HANDOVER",
    },
  },
];

const initialEdges: Edge[] = [
  { id: "e1-2", source: "1", target: "2", animated: true },
  { id: "e2-3", source: "2", sourceHandle: "yes", target: "3", label: "Yes", animated: true },
  { id: "e3-4", source: "3", target: "4", animated: true },
  { id: "e2-5", source: "2", sourceHandle: "no", target: "5", label: "No" },
];

export default function VisualFlowBuilderPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [testModalOpen, setTestModalOpen] = useState(false);
  const [testInput, setTestInput] = useState("Hi");
  const [simulationResult, setSimulationResult] = useState<any>(null);
  const [simulating, setSimulating] = useState(false);

  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const handleTestFlow = async () => {
    setSimulating(true);
    try {
      const res = await ApiClient.testSimulation(testInput);
      setSimulationResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setSimulating(false);
    }
  };

  const handleSaveFlow = () => {
    alert("Flow published successfully as Version 2!");
  };

  return (
    <AppShell>
      <div className="h-full flex flex-col bg-slate-950 overflow-hidden relative">
        {/* Canvas Toolbar Top Header */}
        <div className="h-14 px-6 bg-slate-900 border-b border-slate-800 flex items-center justify-between z-10">
          <div className="flex items-center gap-3">
            <div className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <h1 className="font-bold text-sm text-white">
                Main Customer Welcome Flow (v2)
              </h1>
              <span className="text-[10px] text-slate-400">
                Trigger: Keyword &ldquo;Hi&rdquo; • Priority 1 • Published
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setTestModalOpen(true)}
              className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition"
            >
              <Play className="w-3.5 h-3.5 text-amber-400" />
              <span>Test Flow Simulation</span>
            </button>
            <button
              onClick={handleSaveFlow}
              className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold flex items-center gap-1.5 transition shadow-md shadow-emerald-950"
            >
              <Save className="w-3.5 h-3.5" />
              <span>Publish Flow</span>
            </button>
          </div>
        </div>

        {/* React Flow Canvas */}
        <div className="flex-1 w-full h-full bg-slate-950">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            fitView
          >
            <Background color="#1e293b" gap={16} />
            <Controls className="bg-slate-900 border border-slate-800 text-slate-200 fill-slate-200" />
            <MiniMap
              nodeColor="#10b981"
              maskColor="rgba(15, 23, 42, 0.7)"
              className="bg-slate-900 border border-slate-800 rounded-xl"
            />
          </ReactFlow>
        </div>

        {/* Test Simulation Modal */}
        {testModalOpen && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <Play className="w-4 h-4 text-emerald-400" />
                  <h3 className="font-bold text-sm text-white">Test Flow Execution</h3>
                </div>
                <button
                  onClick={() => setTestModalOpen(false)}
                  className="text-slate-400 hover:text-white text-xs"
                >
                  Close
                </button>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Simulated Customer Input
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={testInput}
                    onChange={(e) => setTestInput(e.target.value)}
                    className="flex-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                  <button
                    onClick={handleTestFlow}
                    disabled={simulating}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs rounded-xl transition"
                  >
                    {simulating ? "Simulating..." : "Run"}
                  </button>
                </div>
              </div>

              {simulationResult && (
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2.5 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-emerald-400 flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>{simulationResult.matched ? "Flow Triggered!" : "No Match"}</span>
                    </span>
                    {simulationResult.triggered_handover && (
                      <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-bold text-[10px]">
                        Handover Triggered
                      </span>
                    )}
                  </div>

                  <div className="space-y-1 text-[11px] text-slate-400 border-t border-slate-800 pt-2">
                    {simulationResult.execution_steps?.map((st: string, idx: number) => (
                      <div key={idx} className="flex items-center gap-1.5">
                        <ArrowRight className="w-3 h-3 text-emerald-400 shrink-0" />
                        <span>{st}</span>
                      </div>
                    ))}
                  </div>

                  {simulationResult.response_preview && (
                    <div className="mt-3 p-3 rounded-lg bg-slate-900 border border-slate-800 text-slate-200">
                      <p className="font-bold text-[10px] uppercase text-slate-400 mb-1">
                        Response Preview:
                      </p>
                      <p className="whitespace-pre-line">{simulationResult.response_preview}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
