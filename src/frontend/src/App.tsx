import { MetroChatExperience } from '@/components/metro-chat-experience';
import { SilkBackgroundAnimation } from '@/components/ui/silk-background-animation';

function App() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-metro-background text-metro-text">
      <SilkBackgroundAnimation />
      <div className="relative z-10">
        <MetroChatExperience />
      </div>
    </main>
  );
}

export default App;
