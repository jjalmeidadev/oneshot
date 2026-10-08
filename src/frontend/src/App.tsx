import { MotionConfig } from 'framer-motion';
import { AccessScreen } from '@/components/access/access-screen';
import { AppShell } from '@/components/layout/app-shell';
import { TooltipProvider } from '@/components/ui/tooltip';
import { ChatStoreProvider } from '@/state/chat-store';
import { AccessSessionProvider, useAccessSession } from '@/state/access-session';
import { ThemeProvider } from '@/state/theme-provider';

function SessionBoundary() {
  const { session } = useAccessSession();
  if (!session) return <AccessScreen />;
  return (
    <ChatStoreProvider key={session.sessionKey} accessToken={session.accessToken}>
      <AppShell />
    </ChatStoreProvider>
  );
}

function App() {
  return (
    <MotionConfig reducedMotion="user">
      <ThemeProvider>
        <TooltipProvider delayDuration={200}>
          <AccessSessionProvider>
            <SessionBoundary />
          </AccessSessionProvider>
        </TooltipProvider>
      </ThemeProvider>
    </MotionConfig>
  );
}

export default App;
