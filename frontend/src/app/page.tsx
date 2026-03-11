"use client"

import { useState, useEffect, useRef } from "react"
import { SendHorizontal, Bot } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

type Message = {
  id: string
  role: "user" | "ai"
  content: string
}

type Session = {
  id: string
  createdAt: string
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [sessions, setSessions] = useState<Session[]>([])
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null)
  const [inputValue, setInputValue] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Fetch all sessions on load
  useEffect(() => {
    fetch("http://localhost:8000/sessions")
      .then((res) => res.json())
      .then((data) => {
        setSessions(data)
        if (data.length > 0 && !activeSessionId) {
          setActiveSessionId(data[0].id)
        }
      })
      .catch((err) => console.error("Failed to fetch sessions:", err))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Fetch messages when a session is selected
  useEffect(() => {
    if (!activeSessionId) return
    
    // Optimistic clear
    setMessages([])

    fetch(`http://localhost:8000/sessions/${activeSessionId}/messages`)
      .then((res) => res.json())
      .then((data) => {
        setMessages(
          data.map((m: { role: "user" | "ai"; content: string }, i: number) => ({
            id: i.toString(),
            role: m.role,
            content: m.content,
          }))
        )
      })
      .catch((err) => console.error("Failed to fetch messages:", err))
  }, [activeSessionId])

  const handleNewSession = () => {
    setActiveSessionId(crypto.randomUUID())
    setMessages([{
        id: "intro", role: "ai", content: "Hello! I am your autonomous AI agent. Let's start a new session."
    }])
  }

  const handleSend = async () => {
    if (!inputValue.trim()) return

    const messageText = inputValue;

    // Optimistically update UI with user message.
    const newUserMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: messageText,
    }

    setMessages((prev) => [...prev, newUserMessage])
    setInputValue("")

    let currentSessionId = activeSessionId;
    if (!currentSessionId) {
      currentSessionId = crypto.randomUUID();
      setActiveSessionId(currentSessionId);
      setSessions((prev) => [{ id: currentSessionId!, createdAt: new Date().toISOString() }, ...prev]);
    }

    const aiMessageId = (Date.now() + 1).toString();
    setMessages((prev) => [...prev, { id: aiMessageId, role: "ai", content: "" }]);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: messageText, session_id: currentSessionId }),
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let done = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const dataStr = line.slice(6).trim();
              if (dataStr === "[DONE]") break;
              if (dataStr) {
                try {
                  const data = JSON.parse(dataStr);
                  if (data.type === "content") {
                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === aiMessageId
                          ? { ...msg, content: msg.content + data.data }
                          : msg
                      )
                    );
                  }
                } catch {
                  // Ignore parsing errors
                }
              }
            }
          }
        }
      }
    } catch (err) {
      console.error("Chat error:", err);
    }
  }

  return (
    <div className="flex h-screen w-full bg-zinc-950 text-zinc-50 font-sans">
      {/* Sidebar (Feature 5) */}
      <div className="hidden w-64 border-r border-zinc-800 bg-zinc-950 p-4 md:flex flex-col gap-4">
        <h2 className="text-xl font-bold tracking-tight text-zinc-100 px-2 pb-2">Chat History</h2>
        <Button onClick={handleNewSession} variant="secondary" className="justify-start opacity-90 transition-opacity hover:opacity-100">
          + New Session
        </Button>
        <ScrollArea className="flex-1 w-full mt-2">
            <div className="flex flex-col gap-2">
                {sessions.length === 0 ? (
                    <p className="text-sm text-zinc-500 px-2">No previous sessions.</p>
                ) : (
                    sessions.map((s) => (
                        <Button
                            key={s.id}
                            variant="ghost"
                            onClick={() => setActiveSessionId(s.id)}
                            className={`justify-start text-xs font-normal truncate ${
                                activeSessionId === s.id ? "bg-zinc-800 text-zinc-100" : "text-zinc-400 hover:text-zinc-200"
                            }`}
                        >
                            {new Date(s.createdAt).toLocaleString()}
                        </Button>
                    ))
                )}
            </div>
        </ScrollArea>
      </div>

      {/* Main Chat Area */}
      <div className="flex flex-1 flex-col h-full relative">
        {/* Header */}
        <header className="flex h-14 shrink-0 items-center justify-between border-b border-zinc-800 bg-zinc-950 px-6">
          <h1 className="text-lg font-semibold text-zinc-100">AI Agent</h1>
        </header>

        {/* Scrollable Messages */}
        <ScrollArea className="flex-1 min-h-0 w-full pt-4">
          <div className="flex flex-col gap-6 px-6 pt-2 pb-6 max-w-4xl mx-auto">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex gap-4 ${
                  m.role === "user" ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <Avatar className="h-8 w-8 mt-1 border border-zinc-700 bg-zinc-900">
                  {m.role === "user" ? (
                    <AvatarFallback className="bg-zinc-800 text-xs">US</AvatarFallback>
                  ) : (
                    <Bot className="h-5 w-5 m-auto text-emerald-500" />
                  )}
                </Avatar>

                <Card
                  className={`px-4 py-3 max-w-[85%] text-sm rounded-2xl break-words overflow-hidden ${
                    m.role === "user"
                      ? "bg-zinc-100 text-zinc-950 rounded-tr-sm border-none"
                      : "bg-zinc-900 text-zinc-200 border-zinc-800 rounded-tl-sm shadow-md"
                  }`}
                >
                  <p className="leading-relaxed whitespace-pre-wrap break-words">{m.content}</p>
                </Card>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="shrink-0 w-full bg-zinc-950 border-t border-zinc-800/50 pt-4 pb-6">
          <div className="mx-auto max-w-3xl px-4">
            <div className="relative flex items-center bg-zinc-900 border border-zinc-800 rounded-2xl p-2 shadow-xl focus-within:ring-1 focus-within:ring-emerald-500/50 transition-shadow">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault()
                    handleSend()
                  }
                }}
                placeholder="Message the agent..."
                className="flex-1 border-0 bg-transparent text-zinc-100 placeholder:text-zinc-500 focus-visible:ring-0 shadow-none h-12 text-base"
              />
              <Button
                onClick={handleSend}
                size="icon"
                disabled={!inputValue.trim()}
                className={`ml-2 h-10 w-10 shrink-0 rounded-xl transition-all ${
                  inputValue.trim()
                    ? "bg-emerald-600 hover:bg-emerald-500 text-white"
                    : "bg-zinc-800 text-zinc-500"
                }`}
              >
                <SendHorizontal className="h-5 w-5" />
              </Button>
            </div>
            <p className="text-center text-xs text-zinc-600 mt-3 font-medium">
              AI Agent can make mistakes. Consider verifying important information.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
