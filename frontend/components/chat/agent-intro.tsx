/**
 * Agent Intro - Welcome screen for first-time Chronos users.
 *
 * Features:
 * - Displays Chronos's name, personality, and key capabilities
 * - Clickable example prompts to start conversations
 * - Glassmorphism theme matching dashboard
 * - Smooth animations
 *
 * Per User Story 6 (FR-024 through FR-027): Agent Introduction Screen.
 */

"use client"

import { motion } from "framer-motion"
import { MessageSquare, Sparkles, Mic, Search, Languages, Clock, Plus } from "lucide-react"

// =============================================================================
// Types
// =============================================================================

export interface AgentIntroProps {
  /** Callback when user clicks an example prompt */
  onExampleClick: (prompt: string) => void
}

// =============================================================================
// Example Prompts
// =============================================================================

/**
 * Predefined example prompts that demonstrate Chronos's capabilities.
 * Each prompt has an icon and text.
 */
const EXAMPLE_PROMPTS = [
  {
    icon: <Plus className="w-4 h-4" />,
    text: 'Create a high priority task "Buy groceries" due tomorrow',
  },
  {
    icon: <Search className="w-4 h-4" />,
    text: "Show me all my incomplete tasks",
  },
  {
    icon: <Clock className="w-4 h-4" />,
    text: "Help me plan my week",
  },
  {
    icon: <Mic className="w-4 h-4" />,
    text: "What can you help me with?",
  },
] as const

// =============================================================================
// Capability Cards
// =============================================================================

/**
 * Individual capability feature card.
 */
function CapabilityCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="p-4 rounded-xl border"
      style={{
        background: "rgba(255, 255, 255, 0.03)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
      }}
    >
      <div className="flex items-start gap-3">
        <div
          className="p-2 rounded-lg flex-shrink-0"
          style={{
            background: "linear-gradient(135deg, rgba(0, 245, 255, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%)",
          }}
        >
          {icon}
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-white mb-1">{title}</h4>
          <p className="text-xs text-white/50">{description}</p>
        </div>
      </div>
    </motion.div>
  )
}

// =============================================================================
// Example Prompt Button
// =============================================================================

/**
 * Clickable example prompt button.
 */
function ExamplePromptButton({
  icon,
  text,
  onClick,
}: {
  icon: React.ReactNode
  text: string
  onClick: () => void
}) {
  return (
    <motion.button
      whileHover={{ scale: 1.01, x: 4 }}
      whileTap={{ scale: 0.99 }}
      onClick={onClick}
      className="w-full px-4 py-3 rounded-xl text-left text-sm transition-all"
      style={{
        background: "rgba(255, 255, 255, 0.04)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
      }}
    >
      <div className="flex items-center gap-3">
        <div
          className="p-1.5 rounded-md flex-shrink-0"
          style={{
            background: "linear-gradient(135deg, rgba(0, 245, 255, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%)",
            color: "#00f5ff",
          }}
        >
          {icon}
        </div>
        <span className="text-white/80 flex-1">{text}</span>
      </div>
    </motion.button>
  )
}

// =============================================================================
// Animation Variants
// =============================================================================

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0 },
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * Agent Introduction Screen component.
 *
 * Displays a welcoming introduction to Chronos with capabilities
 * and clickable example prompts.
 *
 * @example
 * ```tsx
 * import { AgentIntro } from "@/components/chat/agent-intro"
 *
 * {messages.length === 0 && (
 *   <AgentIntro onExampleClick={(prompt) => setInputValue(prompt)} />
 * )}
 * ```
 */
export function AgentIntro({ onExampleClick }: AgentIntroProps) {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="flex flex-col items-center h-full px-6 py-8 text-center"
    >
      {/* Chronos Avatar */}
      <motion.div
        variants={itemVariants}
        className="relative mb-6"
      >
        {/* Glow effect */}
        <div
          className="absolute inset-0 blur-3xl rounded-full"
          style={{
            background: "linear-gradient(135deg, rgba(0, 245, 255, 0.3) 0%, rgba(168, 85, 247, 0.3) 100%)",
          }}
        />
        {/* Avatar circle */}
        <div
          className="relative w-20 h-20 rounded-full flex items-center justify-center"
          style={{
            background: "linear-gradient(135deg, #00f5ff 0%, #a855f7 100%)",
            boxShadow: "0 0 30px rgba(0, 245, 255, 0.3), 0 0 60px rgba(168, 85, 247, 0.2)",
          }}
        >
          <MessageSquare className="w-10 h-10 text-white" strokeWidth={2} />
        </div>
        {/* Sparkle decorations */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="absolute -top-1 -right-1"
        >
          <Sparkles className="w-5 h-5 text-cyan-400" />
        </motion.div>
      </motion.div>

      {/* Title and Greeting */}
      <motion.div variants={itemVariants} className="mb-2">
        <h1 className="text-2xl font-bold text-white mb-1">Meet Chronos</h1>
        <p className="text-sm" style={{ color: "rgba(255, 255, 255, 0.6)" }}>
          Your AI Time Guardian
        </p>
      </motion.div>

      {/* Description */}
      <motion.p
        variants={itemVariants}
        className="text-sm text-white/50 max-w-xs mb-8"
      >
        I can help you manage tasks naturally — just tell me what you need
        in plain English or Urdu (اردو).
      </motion.p>

      {/* Capabilities Grid */}
      <motion.div
        variants={itemVariants}
        className="w-full max-w-sm grid grid-cols-2 gap-3 mb-8"
      >
        <CapabilityCard
          icon={<Sparkles className="w-4 h-4 text-cyan-400" />}
          title="Natural Tasks"
          description="Create tasks using plain language"
        />
        <CapabilityCard
          icon={<Mic className="w-4 h-4 text-purple-400" />}
          title="Voice Input"
          description="Speak naturally, I'll transcribe"
        />
        <CapabilityCard
          icon={<Search className="w-4 h-4 text-cyan-400" />}
          title="Smart Search"
          description="Find tasks by meaning, not words"
        />
        <CapabilityCard
          icon={<Languages className="w-4 h-4 text-purple-400" />}
          title="Bilingual"
          description="English aur Urdu (اردو) support"
        />
      </motion.div>

      {/* Example Prompts Section */}
      <motion.div variants={itemVariants} className="w-full max-w-sm">
        <p className="text-xs text-white/40 mb-3 text-left uppercase tracking-wider">
          Try saying something like...
        </p>
        <div className="space-y-2">
          {EXAMPLE_PROMPTS.map((prompt, index) => (
            <ExamplePromptButton
              key={index}
              icon={prompt.icon}
              text={prompt.text}
              onClick={() => onExampleClick(prompt.text)}
            />
          ))}
        </div>
      </motion.div>
    </motion.div>
  )
}
