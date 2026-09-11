import { MeshGradient } from '@paper-design/shaders-react'
import HeroSection from './sections/heroSection'
import NavbarSection from './sections/navbarSection'
import ChatSection from './sections/chatSection'
import ChatSwapSection from './sections/chatSwapSection'
import TrySection from './sections/trySection'
import IntegrationSection from './sections/integrationSection'
import TeamSection from './sections/teamSection'
import AvatarHandoff from './components/team/avatar-handoff'
import ProgressBar from './components/ui/progress-bar'
import FooterSection from './sections/footer'
import FloatingChat from './components/chat/floating-chat'
import LoadingScreen from './components/ui/loading-screen'
import LiveSessionProvider from './components/live/live-session-provider'
import GhostDocuments from './components/ui/ghost-documents'
import DocumentCarousel from './components/ui/document-carousel'
import DocumentDispatch from './components/ui/document-dispatch'
import ChatFragments from './components/ui/chat-fragments'
import { useChatSectionsTransition } from './lib/chatTransition'
import { useScrollTriggerRefresh } from './lib/useScrollTriggerRefresh'
import { useScrollSpeedLimit } from './lib/useScrollSpeedLimit'
import { useCoarsePointer } from './lib/useCoarsePointer'

function App() {
  useChatSectionsTransition()
  useScrollTriggerRefresh()
  useScrollSpeedLimit('[data-choreography-zone]')
  // As camadas decorativas são calibradas para tela larga; no celular elas
  // saem de proporção. O conteúdo não depende de nenhuma delas.
  const enfeites = !useCoarsePointer()

  return (
    // O provedor entra na sala ao vivo uma vez e empresta o id da sessão
    // para o painel de presença e para a janela de chat.
    <LiveSessionProvider>
    <div className="App relative min-h-screen">
      {/* Cortina de abertura: cobre a montagem do shader, das fontes e do
          handwriting, e só entrega a página quando tudo está pronto. */}
      <LoadingScreen />
      <ProgressBar />
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
      <div data-choreography-zone className="relative isolate bg-neutral-800">
        {/* Silhuetas dos documentos do portfólio, ao fundo das conversas. */}
        {enfeites && <GhostDocuments />}
        {/* Os documentos giram e atravessam a tela na virada do chat 1 para
            o chat 2, indo parar atrás da janela que chega pela direita. */}
        {enfeites && <DocumentCarousel />}
        <ChatSection />
        <ChatSwapSection />
        <TrySection />
        {/* Uma única janela de chat, compartilhada pelas duas últimas seções:
            ela acompanha o slot de cada uma e cresce entre eles. */}
        <FloatingChat />
      </div>

      {/* Fecha o arco dos documentos: eles saem do chat e voam para os
          cards das integrações. Montado antes da seção para passar por trás
          dos cards, não por cima. */}
      {enfeites && <DocumentDispatch />}
      {/* Logo depois dos documentos: a própria janela se parte e os cacos
          viram os blocos das integrações. */}
      {enfeites && <ChatFragments />}

      <IntegrationSection />
      <TeamSection />
      {/* Os avatares do time viajam até virar as bolinhas do rodapé. */}
      {enfeites && <AvatarHandoff />}
      <FooterSection />
    </div>
    </LiveSessionProvider>
  )
}

export default App
