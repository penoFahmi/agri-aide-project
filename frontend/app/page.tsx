'use client'; // Pastikan ini ada untuk client-side interactivity

import { useState, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent } from '@/components/ui/card';

// Definisikan tipe untuk pesan chat
interface Message {
  role: 'user' | 'assistant'; // Siapa yang mengirim: 'user' atau 'assistant'
  content: string;            // Isi pesan
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]); // State untuk menyimpan semua pesan
  const [input, setInput] = useState<string>('');          // State untuk input pengguna
  const [isLoading, setIsLoading] = useState<boolean>(false); // State untuk indikator loading
  const messagesEndRef = useRef<HTMLDivElement>(null); // Ref untuk scroll otomatis ke bawah

  // Fungsi untuk scroll otomatis ke pesan terakhir
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Efek samping untuk scroll setiap kali ada pesan baru
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (input.trim() === '') return; // Jangan kirim pesan kosong

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]); // Tambahkan pesan pengguna
    setInput(''); // Kosongkan input
    setIsLoading(true); // Tampilkan loading

    try {
      const response = await fetch('http://localhost:5000/chat', { // Panggil API backend kita
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: input }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const aiMessage: Message = { role: 'assistant', content: data.answer };
      setMessages((prevMessages) => [...prevMessages, aiMessage]); // Tambahkan jawaban AI

    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: 'assistant', content: 'Maaf, terjadi kesalahan saat memproses permintaan Anda. Silakan coba lagi.' },
      ]);
    } finally {
      setIsLoading(false); // Sembunyikan loading
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { // Kirim saat Enter ditekan (tanpa Shift)
      e.preventDefault(); // Mencegah baris baru di input
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-4">
      <h1 className="text-3xl font-bold text-center text-emerald-800 mb-6">
        🌿 Agri-Aide: Asisten Pertanian Anda 🌿
      </h1>
      <div className="flex flex-col flex-grow bg-white rounded-lg shadow-xl overflow-hidden max-w-2xl mx-auto w-full">
        {/* Area Pesan Chat */}
        <ScrollArea className="flex-grow p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-10">
              Ketik pertanyaan Anda tentang pertanian di sini...
            </div>
          )}
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <Card
                className={`max-w-[70%] p-3 rounded-lg shadow-md ${
                  msg.role === 'user'
                    ? 'bg-emerald-500 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <CardContent className="p-0">
                  <p>{msg.content}</p>
                </CardContent>
              </Card>
            </div>
          ))}
          <div ref={messagesEndRef} /> {/* Element untuk scroll */}
        </ScrollArea>

        {/* Input dan Tombol Kirim */}
        <div className="p-4 border-t bg-gray-50 flex items-center gap-2">
          <Input
            placeholder="Tanyakan tentang hama, penyakit, pupuk, atau budidaya..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-grow p-3 text-lg rounded-lg border-2 focus:ring-emerald-500 focus:border-emerald-500"
            disabled={isLoading}
          />
          <Button onClick={handleSendMessage} className="p-3 text-lg bg-emerald-600 hover:bg-emerald-700" disabled={isLoading}>
            {isLoading ? (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              'Kirim'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}