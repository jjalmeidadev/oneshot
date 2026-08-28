import { useState } from 'react';

import {
  ChatInput,
  ChatInputSubmit,
  ChatInputTextArea,
} from '@/components/ui/chat-input';

function ChatInputDemo() {
  const [value, setValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = () => {
    setIsLoading(true);

    window.setTimeout(() => {
      setValue('');
      setIsLoading(false);
    }, 900);
  };

  return (
    <div className="w-full max-w-2xl">
      <ChatInput
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onSubmit={handleSubmit}
        loading={isLoading}
        onStop={() => setIsLoading(false)}
      >
        <ChatInputTextArea placeholder="Pergunte sobre projetos do Metro de Sao Paulo..." />
        <ChatInputSubmit />
      </ChatInput>
    </div>
  );
}

export { ChatInputDemo };
