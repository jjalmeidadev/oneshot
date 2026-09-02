import { MeshGradient } from '@paper-design/shaders-react'
import HeroSection from './sections/heroSection'
import NavbarSection from './sections/navbarSection'
import ChatSection from './sections/chatSection'
import ChatSwapSection from './sections/chatSwapSection'
import TrySection from './sections/trySection'
import IntegrationSection from './sections/integrationSection'
import FooterSection from './sections/footer'
import FloatingChat from './components/chat/floating-chat'
import { useChatSectionsTransition } from './lib/chatTransition'
import { useScrollTriggerRefresh } from './lib/useScrollTriggerRefresh'

function App() {
  useChatSectionsTransition()
  useScrollTriggerRefresh()

  return (
    <div className="App relative min-h-screen">
      {/* Background global: MeshGradient do @paper-design/shaders-react
          (pacote open-source original do componente do 21st.dev). */}
      <MeshGradient
        className="fixed inset-0 -z-10 h-full w-full"
        colors={['#0a0a12', '#3730a3', '#7c3aed', '#1e1b4b']}
        distortion={0.9}
        swirl={0.6}
        speed={0.15}
      />
      <NavbarSection />
      <HeroSection />

      {/* Área do chat: fundo cinza opaco que cobre o background enquanto as
          seções de conversa estão em tela, com borda limpa (sem gradiente). */}
      <div className="relative isolate bg-neutral-800">
        <ChatSection />
        <ChatSwapSection />
        <TrySection />
        {/* Uma única janela de chat, compartilhada pelas duas últimas seções:
            ela acompanha o slot de cada uma e cresce entre eles. */}
        <FloatingChat />
      </div>

      <IntegrationSection />
      <FooterSection />
    </div>
  )
}

export default App
