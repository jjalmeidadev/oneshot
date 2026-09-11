import { MotionConfig } from 'framer-motion';
import { AppShell } from '@/components/layout/app-shell';
import { TooltipProvider } from '@/components/ui/tooltip';
import { ChatStoreProvider } from '@/state/chat-store';
import { ThemeProvider } from '@/state/theme-provider';

function App() {
  return (
    <MotionConfig reducedMotion="user">
      <ThemeProvider>
        <TooltipProvider delayDuration={200}>
          <ChatStoreProvider>
            <AppShell />
          </ChatStoreProvider>
        </TooltipProvider>
      </ThemeProvider>
    </MotionConfig>
  );
}

export default App;
